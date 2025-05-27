import os
import tempfile
import asyncio
import base64
from pathlib import Path
from typing import Optional
import requests
import re
import json
import aiohttp
import aiofiles
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Tik To Mp4",
    description="Download TikTok videos without watermark",
    version="5.0.0"
)

class DownloadRequest(BaseModel):
    url: str

# HTML template con approccio POST e base64
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="description" content="Tik To Mp4 - Free TikTok video downloader without watermark. Download TikTok videos to MP4 format instantly. Best Tik To Mp4 converter online.">
    <meta name="keywords" content="Tik To Mp4, TikTok downloader, download TikTok video, TikTok to MP4, remove watermark, free TikTok download, Tik To Mp4 converter, TikTok video saver">
    <title>Tik To Mp4 - Free TikTok Video Downloader Without Watermark | Best Tik To Mp4 Converter</title>
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="Tik To Mp4 - Free TikTok Video Downloader">
    <meta property="og:description" content="Best Tik To Mp4 converter. Download TikTok videos without watermark for free. Fast, reliable, and works on all devices.">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="Tik To Mp4 - Free TikTok Video Downloader">
    <meta property="twitter:description" content="Best Tik To Mp4 converter. Download TikTok videos without watermark for free.">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #feca57 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 15px;
            overflow-x: hidden;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 35px 30px;
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15), 0 0 0 1px rgba(255,255,255,0.1);
            max-width: 420px;
            width: 100%;
            text-align: center;
            position: relative;
            border: 2px solid rgba(255,255,255,0.2);
            animation: containerFloat 6s ease-in-out infinite;
        }
        
        @keyframes containerFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        h1 {
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 800;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            animation: titlePulse 3s ease-in-out infinite;
        }
        
        @keyframes titlePulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .subtitle {
            color: #555;
            margin-bottom: 25px;
            font-size: 1.1em;
            line-height: 1.4;
            font-weight: 500;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        input[type="url"] {
            width: 100%;
            padding: 18px 20px;
            border: 3px solid transparent;
            background: linear-gradient(white, white) padding-box, 
                        linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1) border-box;
            border-radius: 15px;
            font-size: 16px;
            transition: all 0.3s ease;
            -webkit-appearance: none;
            appearance: none;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        input[type="url"]:focus {
            outline: none;
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.15);
            background: linear-gradient(white, white) padding-box, 
                        linear-gradient(135deg, #4ecdc4, #45b7d1, #96ceb4) border-box;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%);
            background-size: 200% 200%;
            color: white;
            border: none;
            padding: 18px 35px;
            border-radius: 15px;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            min-height: 60px;
            -webkit-appearance: none;
            appearance: none;
            touch-action: manipulation;
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
            animation: buttonGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes buttonGlow {
            from { box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3); }
            to { box-shadow: 0 10px 30px rgba(78, 205, 196, 0.4); }
        }
        
        .download-btn:hover {
            transform: translateY(-3px);
            background-position: 100% 0;
            box-shadow: 0 15px 40px rgba(255, 107, 107, 0.4);
        }
        
        .download-btn:active {
            transform: translateY(-1px);
        }
        
        .download-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
            animation: none;
        }
        
        .loading {
            display: none;
            margin-top: 20px;
            color: #555;
            font-size: 15px;
            font-weight: 500;
        }
        
        .error {
            color: #e74c3c;
            margin-top: 15px;
            display: none;
            font-size: 14px;
            padding: 15px;
            background: linear-gradient(135deg, #fdf2f2, #fef5f5);
            border-radius: 12px;
            border: 2px solid #fecaca;
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.1);
        }
        
        .success {
            color: #27ae60;
            margin-top: 15px;
            display: none;
            font-size: 14px;
            padding: 15px;
            background: linear-gradient(135deg, #f0f9f4, #f7fcf9);
            border-radius: 12px;
            border: 2px solid #86efac;
            box-shadow: 0 5px 15px rgba(39, 174, 96, 0.1);
        }
        
        .info-box {
            background: linear-gradient(135deg, #e8f4fd, #f0f9ff);
            border: 2px solid #bee5eb;
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #0c5460;
            text-align: left;
            box-shadow: 0 5px 15px rgba(14, 165, 233, 0.1);
        }
        
        .warning-box {
            background: linear-gradient(135deg, #fff3cd, #fef9e7);
            border: 2px solid #ffeaa7;
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #856404;
            text-align: left;
            box-shadow: 0 5px 15px rgba(254, 202, 87, 0.1);
        }
        
        .warning-box ul {
            margin: 10px 0 0 18px;
            padding: 0;
        }
        
        .warning-box li {
            margin-bottom: 6px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
            margin-top: 15px;
            overflow: hidden;
            display: none;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
            background-size: 200% 100%;
            width: 0%;
            transition: width 0.3s ease;
            animation: progressFlow 2s linear infinite;
        }
        
        @keyframes progressFlow {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        .seo-section {
            max-width: 420px;
            margin: 25px auto 0;
            padding: 25px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .seo-section h2 {
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
            font-size: 1.6em;
            font-weight: 700;
        }
        
        .seo-section h3 {
            color: #333;
            margin: 20px 0 12px 0;
            font-size: 1.3em;
            font-weight: 600;
        }
        
        .seo-section p, .seo-section li {
            color: #666;
            line-height: 1.7;
            font-size: 14px;
        }
        
        .seo-section ul, .seo-section ol {
            margin-left: 20px;
        }
        
        .seo-section li {
            margin-bottom: 6px;
        }
        
        /* Mobile specific optimizations */
        @media (max-width: 480px) {
            body {
                padding: 10px;
            }
            
            .container {
                padding: 25px 20px;
                border-radius: 20px;
                max-width: 100%;
            }
            
            h1 {
                font-size: 2.2em;
            }
            
            .subtitle {
                font-size: 1em;
            }
            
            input[type="url"] {
                padding: 16px 18px;
                font-size: 16px;
            }
            
            .download-btn {
                padding: 16px 30px;
                font-size: 16px;
                min-height: 55px;
            }
            
            .info-box, .warning-box {
                font-size: 13px;
                padding: 15px;
            }
            
            .seo-section {
                margin-top: 20px;
                padding: 20px;
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Tik To Mp4</h1>
        <p class="subtitle">Download TikTok videos without watermark</p>
        
        <div class="info-box">
            <strong>✨ FIXED VERSION!</strong><br>
            POST + Base64 approach - absolutely no redirects possible, pure JavaScript download.
        </div>
        
        <div class="warning-box">
            <strong>📱 Instructions:</strong>
            <ul>
                <li>Copy the TikTok link from the app</li>
                <li>Paste it in the field below</li>
                <li>Tap download and wait (processing takes 30-90 seconds)</li>
                <li>Video downloads via pure JavaScript</li>
            </ul>
        </div>
        
        <form id="downloadForm">
            <div class="form-group">
                <input 
                    type="url" 
                    id="tiktokUrl" 
                    placeholder="Paste your TikTok video URL here" 
                    required
                    autocomplete="off"
                    autocorrect="off"
                    autocapitalize="off"
                    spellcheck="false"
                >
            </div>
            <button type="submit" class="download-btn" id="downloadBtn">
                📥 Download Video
            </button>
        </form>
        
        <div class="progress-bar" id="progressBar">
            <div class="progress-fill"></div>
        </div>
        
        <div class="loading" id="loading">
            <p>🔄 Processing via POST... Please wait</p>
            <small>Base64 transfer - no redirects possible (30-90 seconds)</small>
        </div>
        
        <div class="success" id="success"></div>
        <div class="error" id="error"></div>
    </div>
    
    <!-- SEO Content Section -->
    <div class="seo-section">
        <h2>🎥 Tik To Mp4 - Best TikTok Video Downloader</h2>
        <p>
            <strong>Tik To Mp4</strong> is the best free TikTok video downloader that allows you to download TikTok videos without watermark. 
            Our Tik To Mp4 converter works on all devices and provides high-quality MP4 downloads instantly.
        </p>
        
        <h3>✨ Why Choose Tik To Mp4?</h3>
        <ul>
            <li>🚫 <strong>Remove watermark</strong> from TikTok videos automatically</li>
            <li>📱 <strong>Works on mobile</strong>, tablet, and desktop devices</li>
            <li>⚡ <strong>Fast Tik To Mp4 conversion</strong> in seconds</li>
            <li>🆓 <strong>Completely free</strong> TikTok downloader</li>
            <li>🔒 <strong>No registration</strong> or login required</li>
            <li>💾 <strong>High quality MP4</strong> format downloads</li>
        </ul>
        
        <h3>📋 How to use Tik To Mp4:</h3>
        <ol>
            <li>Copy the TikTok video URL from the app or website</li>
            <li>Paste the URL in the Tik To Mp4 converter above</li>
            <li>Click "Download Video" button</li>
            <li>Wait for Tik To Mp4 to process and download your video</li>
        </ol>
        
        <p style="margin-top: 20px; font-size: 12px;">
            <strong>Keywords:</strong> Tik To Mp4, TikTok downloader, download TikTok video, TikTok to MP4, remove watermark, 
            free TikTok download, Tik To Mp4 converter, TikTok video saver, online TikTok downloader, Tik To Mp4 online
        </p>
    </div>

    <script>
        document.getElementById('downloadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('tiktokUrl').value.trim();
            const downloadBtn = document.getElementById('downloadBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const success = document.getElementById('success');
            const progressBar = document.getElementById('progressBar');
            
            // Reset states
            error.style.display = 'none';
            success.style.display = 'none';
            loading.style.display = 'block';
            progressBar.style.display = 'block';
            downloadBtn.disabled = true;
            downloadBtn.textContent = '🔄 Processing...';
            
            try {
                // Clean URL
                let cleanUrl = url;
                cleanUrl = cleanUrl.replace(/[?&]_r=\d+/, '');
                cleanUrl = cleanUrl.replace(/[?&]u_code=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]preview_pb=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]language=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]timestamp=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]enter_method=[^&]*/, '');
                
                // Use POST request with JSON
                const response = await fetch('/download-post', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: cleanUrl
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Server error: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success && data.video_data) {
                    // Decode base64 data
                    const binaryString = atob(data.video_data);
                    const bytes = new Uint8Array(binaryString.length);
                    for (let i = 0; i < binaryString.length; i++) {
                        bytes[i] = binaryString.charCodeAt(i);
                    }
                    
                    // Create blob
                    const blob = new Blob([bytes], { type: 'video/mp4' });
                    
                    // Create download link
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.download = data.filename || 'tiktok_video.mp4';
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    // Clean up
                    window.URL.revokeObjectURL(downloadUrl);
                    
                    // Show success
                    success.textContent = '✅ Download completed! Check your downloads folder.';
                    success.style.display = 'block';
                } else {
                    throw new Error(data.message || 'Failed to process video');
                }
                
                loading.style.display = 'none';
                progressBar.style.display = 'none';
                downloadBtn.disabled = false;
                downloadBtn.textContent = '📥 Download Video';
                
            } catch (err) {
                console.error('Download error:', err);
                error.textContent = `❌ Error: ${err.message}`;
                error.style.display = 'block';
                
                loading.style.display = 'none';
                progressBar.style.display = 'none';
                downloadBtn.disabled = false;
                downloadBtn.textContent = '📥 Download Video';
            }
        });
        
        // Auto-clear messages
        function autoClearMessage(element) {
            setTimeout(() => {
                if (element.style.display !== 'none') {
                    element.style.display = 'none';
                }
            }, 12000);
        }
        
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const target = mutation.target;
                    if (target.id === 'success' || target.id === 'error') {
                        if (target.style.display === 'block') {
                            autoClearMessage(target);
                        }
                    }
                }
            });
        });
        
        observer.observe(document.getElementById('success'), { attributes: true });
        observer.observe(document.getElementById('error'), { attributes: true });
    </script>
</body>
</html>
"""

class UltimateDownloader:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    async def create_session(self):
        if not self.session:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=90)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
        return self.session

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def resolve_short_url(self, url: str) -> str:
        if 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
            try:
                session = await self.create_session()
                async with session.get(url, allow_redirects=True) as response:
                    return str(response.url)
            except:
                pass
        return url

    async def scrape_tiktok_page(self, url: str) -> Optional[dict]:
        try:
            resolved_url = await self.resolve_short_url(url)
            session = await self.create_session()
            
            async with session.get(resolved_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Cerca i dati JSON nella pagina
                    patterns = [
                        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                        r'<script[^>]*>window\.__INITIAL_STATE__\s*=\s*({.*?})</script>',
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, content, re.DOTALL)
                        if match:
                            try:
                                data = json.loads(match.group(1))
                                video_urls = self._extract_video_urls_from_data(data)
                                if video_urls:
                                    return {
                                        'success': True,
                                        'download_url': video_urls[0],
                                        'title': self._extract_title_from_data(data),
                                    }
                            except json.JSONDecodeError:
                                continue
                    
                    # Fallback: cerca pattern diretti (priorità agli URL senza watermark)
                    priority_patterns = [
                        r'"downloadAddr":"([^"]+)"',
                        r'"download_addr":"([^"]+)"',
                        r'"downloadUrl":"([^"]+)"',
                        r'"download_url":"([^"]+)"',
                        r'"noWaterMarkDownload":"([^"]+)"',
                        r'"noWatermark":"([^"]+)"',
                        r'"hdDownload":"([^"]+)"',
                        r'"originCover":"([^"]+\.mp4[^"]*)"',
                    ]
                    
                    fallback_patterns = [
                        r'"playAddr":"([^"]+)"',
                        r'playAddr":"([^"]+)"',
                        r'"play_addr":"([^"]+)"',
                        r'"playUrl":"([^"]+)"',
                        r'src="([^"]*\.mp4[^"]*)"',
                    ]
                    
                    # Prima prova con i pattern senza watermark
                    for pattern in priority_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            video_url = matches[0].replace('\\u002F', '/').replace('\\/', '/')
                            video_url = unquote(video_url)
                            print(f"✅ Found downloadAddr URL: {video_url[:100]}...")
                            return {
                                'success': True,
                                'download_url': video_url,
                                'title': 'tiktok_video',
                            }
                    
                    # Se non trova nulla, usa i pattern con watermark
                    for pattern in fallback_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            video_url = matches[0].replace('\\u002F', '/').replace('\\/', '/')
                            video_url = unquote(video_url)
                            print(f"⚠️ Using playAddr URL (may have watermark): {video_url[:100]}...")
                            return {
                                'success': True,
                                'download_url': video_url,
                                'title': 'tiktok_video',
                            }
        except Exception as e:
            print(f"Scraping failed: {e}")
        return None

    def _extract_video_urls_from_data(self, data: dict) -> list:
        download_urls = []  # URLs senza watermark
        play_urls = []      # URLs con watermark (fallback)
        
        def search_recursive(obj, priority_keys, fallback_keys):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in priority_keys and isinstance(value, str) and 'http' in value and '.mp4' in value:
                        download_urls.append(value)
                    elif key in fallback_keys and isinstance(value, str) and 'http' in value and '.mp4' in value:
                        play_urls.append(value)
                    elif isinstance(value, (dict, list)):
                        search_recursive(value, priority_keys, fallback_keys)
            elif isinstance(obj, list):
                for item in obj:
                    search_recursive(item, priority_keys, fallback_keys)
        
        # Priorità: downloadAddr (senza watermark) > playAddr (con watermark)
        priority_keys = ['downloadAddr', 'download_addr', 'downloadUrl', 'download_url']
        fallback_keys = ['playAddr', 'play_addr', 'playUrl', 'play_url', 'url', 'src']
        
        search_recursive(data, priority_keys, fallback_keys)
        
        # Restituisci prima gli URL senza watermark, poi quelli con watermark
        return download_urls + play_urls

    def _extract_title_from_data(self, data: dict) -> str:
        def search_title(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['desc', 'title', 'description'] and isinstance(value, str):
                        return value
                    elif isinstance(value, (dict, list)):
                        result = search_title(value)
                        if result:
                            return result
            elif isinstance(obj, list):
                for item in obj:
                    result = search_title(item)
                    if result:
                        return result
            return None
        
        title = search_title(data)
        return title if title else 'tiktok_video'

    async def download_video_bytes(self, download_url: str) -> Optional[bytes]:
        try:
            session = await self.create_session()
            
            download_headers = {
                **self.headers,
                'Referer': 'https://www.tiktok.com/',
            }
            
            async with session.get(download_url, headers=download_headers) as response:
                if response.status in [200, 206]:
                    video_data = await response.read()
                    return video_data
        except Exception as e:
            print(f"Download failed: {e}")
        return None

    async def try_alternative_api(self, url: str) -> Optional[dict]:
        """Prova con API alternative per video senza watermark"""
        try:
            session = await self.create_session()
            
            # API 1: TikWM (affidabile per video senza watermark)
            api_url = "https://www.tikwm.com/api/"
            payload = {
                'url': url,
                'hd': 1
            }
            
            async with session.post(api_url, data=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == 0 and data.get('data'):
                        video_data = data['data']
                        # Priorità: hdplay (HD senza watermark) > play (normale)
                        if 'hdplay' in video_data and video_data['hdplay']:
                            print("✅ Found HD video without watermark from API")
                            return {
                                'success': True,
                                'download_url': video_data['hdplay'],
                                'title': video_data.get('title', 'tiktok_video')
                            }
                        elif 'play' in video_data and video_data['play']:
                            print("⚠️ Found normal video from API (may have watermark)")
                            return {
                                'success': True,
                                'download_url': video_data['play'],
                                'title': video_data.get('title', 'tiktok_video')
                            }
        except Exception as e:
            print(f"Alternative API failed: {e}")
        
        return None

    async def get_video_base64(self, url: str) -> Optional[dict]:
        try:
            # Metodo 1: API alternativa (priorità per video senza watermark)
            print("🔄 Trying alternative API for watermark-free video...")
            alt_result = await self.try_alternative_api(url)
            if alt_result and alt_result.get('success'):
                title = alt_result.get('title', 'tiktok_video')
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title[:50] if safe_title else 'tiktok_video'
                
                download_url = alt_result['download_url']
                print(f"🎯 Using API URL: {download_url[:100]}...")
                
                video_data = await self.download_video_bytes(download_url)
                
                if video_data:
                    # Convert to base64
                    video_base64 = base64.b64encode(video_data).decode('utf-8')
                    return {
                        'success': True,
                        'video_data': video_base64,
                        'filename': f"{safe_title}.mp4",
                        'size': len(video_data)
                    }
            
            # Metodo 2: Scraping diretto (fallback)
            print("🔄 Trying direct scraping as fallback...")
            result = await self.scrape_tiktok_page(url)
            if result and result.get('success'):
                title = result.get('title', 'tiktok_video')
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title[:50] if safe_title else 'tiktok_video'
                
                download_url = result['download_url']
                print(f"🎯 Using scraping URL: {download_url[:100]}...")
                
                video_data = await self.download_video_bytes(download_url)
                
                if video_data:
                    # Convert to base64
                    video_base64 = base64.b64encode(video_data).decode('utf-8')
                    return {
                        'success': True,
                        'video_data': video_base64,
                        'filename': f"{safe_title}.mp4",
                        'size': len(video_data)
                    }
            
            return None
        except Exception as e:
            print(f"Get video base64 error: {e}")
            return None
        finally:
            await self.close_session()

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.post("/download-post")
async def download_post(request: Request, download_request: DownloadRequest):
    """POST download with base64 response - absolutely no redirects"""
    
    user_agent = request.headers.get("user-agent", "").lower()
    is_mobile_request = any(device in user_agent for device in ["mobile", "android", "iphone", "ipad"])
    
    url = download_request.url.strip()
    
    if not url:
        raise HTTPException(status_code=400, detail="Please provide a TikTok URL")
    
    tiktok_domains = ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com', 'm.tiktok.com']
    if not any(domain in url.lower() for domain in tiktok_domains):
        raise HTTPException(status_code=400, detail="Please provide a valid TikTok URL")
    
    # Clean URL
    if is_mobile_request:
        url = re.sub(r'[?&]_r=\d+', '', url)
        url = re.sub(r'[?&]u_code=[^&]*', '', url)
        url = re.sub(r'[?&]preview_pb=[^&]*', '', url)
        url = re.sub(r'[?&]language=[^&]*', '', url)
        url = re.sub(r'[?&]timestamp=[^&]*', '', url)
        url = re.sub(r'[?&]enter_method=[^&]*', '', url)
    
    if '?' in url and any(param in url for param in ['q=', 't=']):
        url = url.split('?')[0]
    
    try:
        print(f"🔍 POST processing: {url} (Mobile: {is_mobile_request})")
        
        downloader = UltimateDownloader()
        result = await downloader.get_video_base64(url)
        
        if result and result.get('success'):
            print(f"✅ POST download successful: {result['size']} bytes")
            
            return JSONResponse(content={
                "success": True,
                "video_data": result['video_data'],
                "filename": result['filename'],
                "size": result['size'],
                "message": "Video processed successfully"
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Failed to process video. The video might be private or unavailable."
                }
            )
        
    except Exception as e:
        print(f"❌ POST processing error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to process video. Please try a different video or try again later."
            }
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "5.0.0", "message": "Ultimate POST + Base64 system running"}

@app.get("/test")
async def test_endpoint():
    return {
        "status": "ok",
        "message": "Ultimate POST + Base64 system active",
        "features": [
            "POST requests only",
            "Base64 encoding", 
            "JSON responses",
            "Pure JavaScript download",
            "Absolutely no redirects possible"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 