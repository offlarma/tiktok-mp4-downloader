import os
import tempfile
import asyncio
from pathlib import Path
from typing import Optional
import requests
import re

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import yt_dlp
import aiofiles

app = FastAPI(
    title="Tik To Mp4",
    description="Download TikTok videos without watermark",
    version="2.1.0"
)

# HTML template ottimizzato per mobile senza redirect esterni
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
                font-size: 16px; /* Prevents zoom on iOS */
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
        
        /* iOS Safari specific fixes */
        @supports (-webkit-touch-callout: none) {
            input[type="url"] {
                font-size: 16px !important; /* Prevents zoom */
                transform: translateZ(0); /* Hardware acceleration */
            }
            
            .download-btn {
                transform: translateZ(0); /* Hardware acceleration */
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Tik To Mp4</h1>
        <p class="subtitle">Download TikTok videos without watermark</p>
        
        <div class="info-box">
            <strong>✨ Direct Download!</strong><br>
            No external redirects - downloads directly from our server for better mobile compatibility.
        </div>
        
        <div class="warning-box">
            <strong>📱 Mobile Instructions:</strong>
            <ul>
                <li>Copy the TikTok link from the app</li>
                <li>Paste it in the field below</li>
                <li>Tap download and wait (may take 10-30 seconds)</li>
                <li>Video will download directly to your device</li>
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
            <p>🔄 Processing your video... Please wait</p>
            <small>This may take 10-30 seconds on mobile</small>
        </div>
        
        <div class="success" id="success"></div>
        <div class="error" id="error"></div>
    </div>

    <script>
        // Direct download approach for mobile
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
                // Clean URL for mobile
                let cleanUrl = url;
                cleanUrl = cleanUrl.replace(/[?&]_r=\d+/, '');
                cleanUrl = cleanUrl.replace(/[?&]u_code=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]preview_pb=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]language=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]timestamp=[^&]*/, '');
                cleanUrl = cleanUrl.replace(/[?&]enter_method=[^&]*/, '');
                
                // Use direct download approach - no external redirects
                const downloadUrl = `/download-direct?url=${encodeURIComponent(cleanUrl)}`;
                
                // Create a hidden iframe for download (works better on mobile)
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = downloadUrl;
                document.body.appendChild(iframe);
                
                // Show success message
                setTimeout(() => {
                    success.textContent = '✅ Download started! Check your downloads folder.';
                    success.style.display = 'block';
                    loading.style.display = 'none';
                    progressBar.style.display = 'none';
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = '📥 Download Video';
                    
                    // Remove iframe after download
                    setTimeout(() => {
                        if (iframe.parentNode) {
                            iframe.parentNode.removeChild(iframe);
                        }
                    }, 5000);
                }, 2000);
                
            } catch (err) {
                console.error('Download error:', err);
                error.textContent = `❌ Error: ${err.message}`;
                error.style.display = 'block';
                
                // Reset button state on error
                loading.style.display = 'none';
                progressBar.style.display = 'none';
                downloadBtn.disabled = false;
                downloadBtn.textContent = '📥 Download Video';
            }
        });
        
        // Auto-clear messages after 8 seconds
        function autoClearMessage(element) {
            setTimeout(() => {
                if (element.style.display !== 'none') {
                    element.style.display = 'none';
                }
            }, 8000);
        }
        
        // Apply auto-clear to success and error messages
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
        
        // Handle paste event for better mobile UX
        document.getElementById('tiktokUrl').addEventListener('paste', function(e) {
            setTimeout(() => {
                const pastedText = this.value;
                if (pastedText && pastedText.includes('tiktok.com')) {
                    // Auto-focus download button after paste
                    document.getElementById('downloadBtn').focus();
                }
            }, 100);
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main page"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/download-direct")
async def download_video_direct(request: Request, url: str = Query(..., description="TikTok video URL")):
    """Direct download without external redirects - optimized for mobile"""
    
    # Detect if request is from mobile
    user_agent = request.headers.get("user-agent", "").lower()
    is_mobile_request = any(device in user_agent for device in ["mobile", "android", "iphone", "ipad"])
    
    # Validate URL
    if not url:
        raise HTTPException(status_code=400, detail="Please provide a TikTok URL")
    
    tiktok_domains = ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com', 'm.tiktok.com']
    if not any(domain in url.lower() for domain in tiktok_domains):
        raise HTTPException(status_code=400, detail="Please provide a valid TikTok URL")
    
    # Mobile-specific URL cleaning
    if is_mobile_request:
        url = re.sub(r'[?&]_r=\d+', '', url)
        url = re.sub(r'[?&]u_code=[^&]*', '', url)
        url = re.sub(r'[?&]preview_pb=[^&]*', '', url)
        url = re.sub(r'[?&]language=[^&]*', '', url)
        url = re.sub(r'[?&]timestamp=[^&]*', '', url)
        url = re.sub(r'[?&]enter_method=[^&]*', '', url)
    
    # Clean URL parameters
    if '?' in url and any(param in url for param in ['q=', 't=']):
        url = url.split('?')[0]
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        print(f"🔍 Direct download attempt: {url} (Mobile: {is_mobile_request})")
        
        # Use only yt-dlp with mobile-optimized settings (avoid external APIs)
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best' if is_mobile_request else 'best[ext=mp4]/best',
            'noplaylist': True,
            'extractaudio': False,
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            # Mobile-optimized headers
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1' if is_mobile_request else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Connection': 'keep-alive',
                'Referer': 'https://www.tiktok.com/',
            },
            # TikTok specific options
            'extractor_args': {
                'tiktok': {
                    'webpage_url_basename': 'video'
                }
            },
            # Retry and timeout options
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            'socket_timeout': 30,
            # Anti-detection
            'sleep_interval': 2,
            'max_sleep_interval': 8,
            'sleep_interval_requests': 2,
        }
        
        # Download video with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'tiktok_video')
                
                # Clean filename
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:50] if safe_title else 'tiktok_video'
                
                # Update output template
                ydl_opts['outtmpl'] = os.path.join(temp_dir, f'{safe_title}.%(ext)s')
                
                # Download the video
                ydl.download([url])
                
            except Exception as e:
                print(f"yt-dlp extraction failed: {e}")
                # Fallback: try direct download without info extraction
                safe_title = "tiktok_video"
                ydl_opts['outtmpl'] = os.path.join(temp_dir, f'{safe_title}.%(ext)s')
                ydl.download([url])
        
        # Find the downloaded file
        downloaded_files = list(Path(temp_dir).glob('*'))
        if not downloaded_files:
            raise HTTPException(
                status_code=500, 
                detail="Failed to download video. The video might be private or unavailable."
            )
        
        video_file = downloaded_files[0]
        print(f"✅ Direct download successful: {video_file}")
        
        # Mobile-specific headers for better compatibility
        headers = {
            "Content-Disposition": f'attachment; filename="{safe_title}.mp4"',
            "Content-Type": "video/mp4",
        }
        
        if is_mobile_request:
            headers.update({
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-Content-Type-Options": "nosniff",
            })
        
        return FileResponse(
            path=str(video_file),
            filename=f"{safe_title}.mp4",
            media_type='video/mp4',
            headers=headers,
            background=cleanup_temp_file(str(video_file), temp_dir)
        )
        
    except yt_dlp.DownloadError as e:
        cleanup_temp_dir(temp_dir)
        
        error_msg = str(e)
        if "blocked" in error_msg.lower() or "ip" in error_msg.lower():
            raise HTTPException(
                status_code=503, 
                detail="TikTok is currently blocking downloads. Please try again in a few minutes."
            )
        elif "private" in error_msg.lower() or "unavailable" in error_msg.lower():
            raise HTTPException(
                status_code=404, 
                detail="This video is private or unavailable. Please try a different video."
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Failed to download video. Please try a different video or try again later."
            )
    except Exception as e:
        cleanup_temp_dir(temp_dir)
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred. Please try again."
        )

async def cleanup_temp_file(file_path: str, temp_dir: str):
    """Background task to clean up temporary files"""
    try:
        await asyncio.sleep(3)
        if os.path.exists(file_path):
            os.remove(file_path)
        cleanup_temp_dir(temp_dir)
    except Exception:
        pass

def cleanup_temp_dir(temp_dir: str):
    """Clean up temporary directory"""
    try:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception:
        pass

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.1.0", "message": "Direct download system running"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "status": "ok",
        "message": "Direct download system active",
        "features": [
            "Direct downloads (no external redirects)",
            "Mobile optimized", 
            "Better error handling",
            "No tikcdn.io redirects"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 