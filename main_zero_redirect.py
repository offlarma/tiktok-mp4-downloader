import os
import tempfile
import asyncio
from pathlib import Path
from typing import Optional
import requests
import re
import json
import aiohttp
import aiofiles
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse

app = FastAPI(
    title="Tik To Mp4",
    description="Download TikTok videos without watermark",
    version="4.0.0"
)

# HTML template con approccio fetch invece di link diretto
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="description" content="Tik To Mp4 - Download TikTok videos without watermark easily and quickly">
    <title>Tik To Mp4 - Download TikTok Videos Without Watermark</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 15px;
            overflow-x: hidden;
        }
        
        .container {
            background: white;
            padding: 30px 25px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
            text-align: center;
            position: relative;
        }
        
        h1 {
            color: #333;
            margin-bottom: 8px;
            font-size: 2.2em;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 25px;
            font-size: 1em;
            line-height: 1.4;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        input[type="url"] {
            width: 100%;
            padding: 16px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 16px;
            transition: border-color 0.3s ease;
            -webkit-appearance: none;
            appearance: none;
            background: #fff;
        }
        
        input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 16px 30px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            width: 100%;
            min-height: 54px;
            -webkit-appearance: none;
            appearance: none;
            touch-action: manipulation;
        }
        
        .download-btn:active {
            transform: scale(0.98);
        }
        
        .download-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }
        
        .error {
            color: #e74c3c;
            margin-top: 15px;
            display: none;
            font-size: 14px;
            padding: 12px;
            background: #fdf2f2;
            border-radius: 8px;
            border: 1px solid #fecaca;
        }
        
        .success {
            color: #27ae60;
            margin-top: 15px;
            display: none;
            font-size: 14px;
            padding: 12px;
            background: #f0f9f4;
            border-radius: 8px;
            border: 1px solid #86efac;
        }
        
        .info-box {
            background: #e8f4fd;
            border: 1px solid #bee5eb;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #0c5460;
            text-align: left;
        }
        
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #856404;
            text-align: left;
        }
        
        .warning-box ul {
            margin: 8px 0 0 16px;
            padding: 0;
        }
        
        .warning-box li {
            margin-bottom: 4px;
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background-color: #e1e5e9;
            border-radius: 2px;
            margin-top: 15px;
            overflow: hidden;
            display: none;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
            animation: progress-animation 2s infinite;
        }
        
        @keyframes progress-animation {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
        
        /* Mobile specific optimizations */
        @media (max-width: 480px) {
            body {
                padding: 10px;
            }
            
            .container {
                padding: 25px 20px;
                border-radius: 15px;
            }
            
            h1 {
                font-size: 1.8em;
            }
            
            .subtitle {
                font-size: 0.9em;
            }
            
            input[type="url"] {
                padding: 14px 12px;
                font-size: 16px;
            }
            
            .download-btn {
                padding: 14px 25px;
                font-size: 15px;
                min-height: 50px;
            }
            
            .info-box, .warning-box {
                font-size: 12px;
                padding: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Tik To Mp4</h1>
        <p class="subtitle">Download TikTok videos without watermark</p>
        
        <div class="info-box">
            <strong>✨ Zero Redirect System!</strong><br>
            New streaming approach - no redirects, no external sites, direct download.
        </div>
        
        <div class="warning-box">
            <strong>📱 Instructions:</strong>
            <ul>
                <li>Copy the TikTok link from the app</li>
                <li>Paste it in the field below</li>
                <li>Tap download and wait (processing takes 20-60 seconds)</li>
                <li>Video streams directly to your device</li>
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
            <p>🔄 Streaming video... Please wait</p>
            <small>Zero redirects - streaming directly (20-60 seconds)</small>
        </div>
        
        <div class="success" id="success"></div>
        <div class="error" id="error"></div>
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
                
                // Use streaming endpoint
                const streamUrl = `/stream-download?url=${encodeURIComponent(cleanUrl)}`;
                
                // Fetch with streaming response
                const response = await fetch(streamUrl);
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                // Get filename from headers
                const contentDisposition = response.headers.get('content-disposition');
                let filename = 'tiktok_video.mp4';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }
                
                // Create blob from response
                const blob = await response.blob();
                
                // Create download link
                const downloadUrl = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = filename;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Clean up
                window.URL.revokeObjectURL(downloadUrl);
                
                // Show success
                success.textContent = '✅ Download completed! Check your downloads folder.';
                success.style.display = 'block';
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
            }, 10000);
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

class ZeroRedirectDownloader:
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
            timeout = aiohttp.ClientTimeout(total=60)
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
                    
                    # Fallback: cerca pattern diretti
                    video_patterns = [
                        r'"downloadAddr":"([^"]+)"',
                        r'"playAddr":"([^"]+)"',
                        r'playAddr":"([^"]+)"',
                        r'"download_addr":"([^"]+)"',
                        r'src="([^"]*\.mp4[^"]*)"',
                    ]
                    
                    for pattern in video_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            video_url = matches[0].replace('\\u002F', '/').replace('\\/', '/')
                            video_url = unquote(video_url)
                            return {
                                'success': True,
                                'download_url': video_url,
                                'title': 'tiktok_video',
                            }
        except Exception as e:
            print(f"Scraping failed: {e}")
        return None

    def _extract_video_urls_from_data(self, data: dict) -> list:
        urls = []
        
        def search_recursive(obj, keys_to_find):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in keys_to_find and isinstance(value, str) and 'http' in value and '.mp4' in value:
                        urls.append(value)
                    elif isinstance(value, (dict, list)):
                        search_recursive(value, keys_to_find)
            elif isinstance(obj, list):
                for item in obj:
                    search_recursive(item, keys_to_find)
        
        keys_to_find = ['downloadAddr', 'playAddr', 'download_addr', 'play_addr', 'url', 'src']
        search_recursive(data, keys_to_find)
        
        return urls

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

    async def stream_video_download(self, download_url: str) -> Optional[bytes]:
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
            print(f"Stream download failed: {e}")
        return None

    async def get_video_data(self, url: str) -> Optional[tuple]:
        try:
            result = await self.scrape_tiktok_page(url)
            if result and result.get('success'):
                title = result.get('title', 'tiktok_video')
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title[:50] if safe_title else 'tiktok_video'
                
                video_data = await self.stream_video_download(result['download_url'])
                
                if video_data:
                    return video_data, safe_title
            return None
        except Exception as e:
            print(f"Get video data error: {e}")
            return None
        finally:
            await self.close_session()

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/stream-download")
async def stream_download(request: Request, url: str = Query(..., description="TikTok video URL")):
    """Stream download - zero redirects approach"""
    
    user_agent = request.headers.get("user-agent", "").lower()
    is_mobile_request = any(device in user_agent for device in ["mobile", "android", "iphone", "ipad"])
    
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
        print(f"🔍 Stream processing: {url} (Mobile: {is_mobile_request})")
        
        downloader = ZeroRedirectDownloader()
        result = await downloader.get_video_data(url)
        
        if result:
            video_data, safe_title = result
            print(f"✅ Stream download successful: {len(video_data)} bytes")
            
            # Create streaming response
            def generate():
                yield video_data
            
            headers = {
                "Content-Disposition": f'attachment; filename="{safe_title}.mp4"',
                "Content-Type": "video/mp4",
                "Content-Length": str(len(video_data)),
            }
            
            if is_mobile_request:
                headers.update({
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                })
            
            return StreamingResponse(
                generate(),
                media_type='video/mp4',
                headers=headers
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to process video. The video might be private or unavailable."
            )
        
    except Exception as e:
        print(f"❌ Stream processing error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to process video. Please try a different video or try again later."
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "4.0.0", "message": "Zero redirect streaming system running"}

@app.get("/test")
async def test_endpoint():
    return {
        "status": "ok",
        "message": "Zero redirect streaming system active",
        "features": [
            "Zero redirects",
            "Streaming response", 
            "No FileResponse",
            "Direct memory transfer"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 