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

# Importa il nuovo downloader migliorato
from improved_downloader import download_tiktok_video_improved

app = FastAPI(
    title="Tik To Mp4",
    description="Download TikTok videos without watermark",
    version="2.0.0"
)

# HTML template for the frontend (migliorato)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Tik To Mp4 - Download TikTok videos without watermark easily and quickly">
    <title>Tik To Mp4 - Download TikTok Videos Without Watermark</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        input[type="url"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        
        input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
            width: 100%;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
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
        }
        
        .error {
            color: #e74c3c;
            margin-top: 15px;
            display: none;
        }
        
        .success {
            color: #27ae60;
            margin-top: 15px;
            display: none;
        }
        
        .info-box {
            background: #e8f4fd;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #0c5460;
        }
        
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #856404;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2em;
            }
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background-color: #e1e5e9;
            border-radius: 2px;
            margin-top: 10px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Tik To Mp4</h1>
        <p class="subtitle">Download TikTok videos without watermark</p>
        
        <div class="info-box">
            <strong>✨ New Improved System!</strong><br>
            We now use multiple methods to ensure more reliable and faster downloads.
        </div>
        
        <div class="warning-box">
            <strong>⚠️ Note:</strong> TikTok frequently updates their anti-bot measures. If downloads fail, try:
            <ul style="margin: 8px 0 0 20px; text-align: left;">
                <li>Using a different TikTok video URL</li>
                <li>Waiting a few minutes and trying again</li>
                <li>Making sure the video is public and accessible</li>
            </ul>
        </div>
        
        <form id="downloadForm">
            <div class="form-group">
                <input 
                    type="url" 
                    id="tiktokUrl" 
                    placeholder="Paste your TikTok video URL here" 
                    required
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
            <small>We're trying different methods to ensure the best result</small>
        </div>
        
        <div class="success" id="success"></div>
        <div class="error" id="error"></div>
    </div>

    <script>
        document.getElementById('downloadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('tiktokUrl').value;
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
                // Create download URL
                const downloadUrl = `/download?url=${encodeURIComponent(url)}`;
                
                // First, check if the request will succeed by making a HEAD request
                const response = await fetch(downloadUrl, { method: 'HEAD' });
                
                if (!response.ok) {
                    // If HEAD request fails, try GET to get the error message
                    const errorResponse = await fetch(downloadUrl);
                    const errorData = await errorResponse.json();
                    throw new Error(errorData.detail || 'Download failed');
                }
                
                // If HEAD request succeeds, proceed with download
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = '';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Show success message
                success.textContent = '✅ Download started successfully!';
                success.style.display = 'block';
                
            } catch (err) {
                console.error('Download error:', err);
                error.textContent = `❌ Error: ${err.message}`;
                error.style.display = 'block';
            } finally {
                // Reset button and hide loading
                loading.style.display = 'none';
                progressBar.style.display = 'none';
                downloadBtn.disabled = false;
                downloadBtn.textContent = '📥 Download Video';
            }
        });
        
        // Auto-clear messages after 5 seconds
        function autoClearMessage(element) {
            setTimeout(() => {
                if (element.style.display !== 'none') {
                    element.style.display = 'none';
                }
            }, 5000);
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
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main page"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.head("/download")
@app.get("/download")
async def download_video(request: Request, url: str = Query(..., description="TikTok video URL")):
    """Download TikTok video using improved methods"""
    
    # For HEAD requests, just validate the URL and return success
    if request.method == "HEAD":
        # Quick validation
        if not url:
            raise HTTPException(status_code=400, detail="Please provide a TikTok URL")
        
        tiktok_domains = ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com', 'm.tiktok.com']
        if not any(domain in url.lower() for domain in tiktok_domains):
            raise HTTPException(status_code=400, detail="Please provide a valid TikTok URL")
        
        return JSONResponse(content={"status": "ok"})
    
    # Validate and clean URL
    if not url:
        raise HTTPException(
            status_code=400, 
            detail="Please provide a TikTok URL"
        )
    
    # Support various TikTok URL formats
    tiktok_domains = ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com', 'm.tiktok.com']
    if not any(domain in url.lower() for domain in tiktok_domains):
        raise HTTPException(
            status_code=400, 
            detail="Please provide a valid TikTok URL"
        )
    
    # Clean URL parameters that might cause issues
    if '?' in url and any(param in url for param in ['q=', 't=']):
        url = url.split('?')[0]
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        print(f"🔍 Attempting to download: {url}")
        
        # Try the improved downloader first
        video_file = await download_tiktok_video_improved(url, temp_dir)
        
        if video_file and os.path.exists(video_file):
            print(f"✅ Improved downloader successful: {video_file}")
            
            # Extract safe filename
            filename = os.path.basename(video_file)
            safe_title = filename.replace('.mp4', '')
            
            return FileResponse(
                path=str(video_file),
                filename=f"{safe_title}.mp4",
                media_type='video/mp4',
                background=cleanup_temp_file(str(video_file), temp_dir)
            )
        
        # Fallback to yt-dlp if improved method fails
        print("🔄 Improved method failed, trying yt-dlp fallback...")
        
        # Configure yt-dlp options with better TikTok support
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'format': 'best[ext=mp4]/best[height<=720]/best',
            'noplaylist': True,
            'extractaudio': False,
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            # Better headers and user agent for TikTok
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '300',
                'Connection': 'keep-alive',
            },
            # Additional options for TikTok
            'extractor_args': {
                'tiktok': {
                    'webpage_url_basename': 'video'
                }
            },
            # Retry options
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            # Anti-detection measures
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'sleep_interval_requests': 1,
        }
        
        # Download video with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to get the title
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'tiktok_video')
            
            # Clean filename
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Limit length
            
            # Update output template with safe title
            ydl_opts['outtmpl'] = os.path.join(temp_dir, f'{safe_title}.%(ext)s')
            
            # Download the video
            ydl.download([url])
        
        # Find the downloaded file
        downloaded_files = list(Path(temp_dir).glob('*'))
        if not downloaded_files:
            raise HTTPException(
                status_code=500, 
                detail="Failed to download video. Please check the URL and try again."
            )
        
        video_file = downloaded_files[0]
        
        print(f"✅ yt-dlp fallback successful: {video_file}")
        
        # Return file response
        return FileResponse(
            path=str(video_file),
            filename=f"{safe_title}.mp4",
            media_type='video/mp4',
            background=cleanup_temp_file(str(video_file), temp_dir)
        )
        
    except yt_dlp.DownloadError as e:
        # Both methods failed
        cleanup_temp_dir(temp_dir)
        
        error_msg = str(e)
        if "blocked" in error_msg.lower() or "ip" in error_msg.lower():
            raise HTTPException(
                status_code=503, 
                detail="TikTok is currently blocking downloads. This is a temporary issue. Please try again later or use a different video URL."
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Failed to download video. This might be due to TikTok's anti-bot measures. Please try a different video or try again later."
            )
    except Exception as e:
        # Clean up temp directory
        cleanup_temp_dir(temp_dir)
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred. Please try again."
        )

async def cleanup_temp_file(file_path: str, temp_dir: str):
    """Background task to clean up temporary files"""
    try:
        # Wait a bit to ensure file transfer is complete
        await asyncio.sleep(2)
        
        # Remove the file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove temp directory
        cleanup_temp_dir(temp_dir)
    except Exception:
        pass  # Ignore cleanup errors

def cleanup_temp_dir(temp_dir: str):
    """Clean up temporary directory"""
    try:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception:
        pass  # Ignore cleanup errors

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0", "message": "TikTok downloader is running with improved methods"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify the service is working"""
    return {
        "status": "ok",
        "message": "Service is running",
        "features": [
            "Multiple download methods",
            "Improved reliability", 
            "Better error handling",
            "Italian interface"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 