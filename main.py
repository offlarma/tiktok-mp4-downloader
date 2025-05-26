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
    version="1.0.0"
)

# HTML template for the frontend
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
        
        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tik To Mp4</h1>
        <p class="subtitle">Download TikTok videos without watermark</p>
        
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin-bottom: 20px; font-size: 14px; color: #856404;">
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
                Download Video
            </button>
        </form>
        
        <div class="loading" id="loading">
            <p>Processing your video... Please wait</p>
        </div>
        
        <div class="error" id="error"></div>
    </div>

    <script>
        document.getElementById('downloadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('tiktokUrl').value;
            const downloadBtn = document.getElementById('downloadBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            
            // Reset states
            error.style.display = 'none';
            loading.style.display = 'block';
            downloadBtn.disabled = true;
            downloadBtn.textContent = 'Processing...';
            
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
                
                // Reset form after a delay
                setTimeout(() => {
                    loading.style.display = 'none';
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = 'Download Video';
                    document.getElementById('tiktokUrl').value = '';
                }, 2000);
                
            } catch (err) {
                error.textContent = err.message || 'An error occurred. Please try again.';
                error.style.display = 'block';
                loading.style.display = 'none';
                downloadBtn.disabled = false;
                downloadBtn.textContent = 'Download Video';
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main HTML page"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.head("/download")
@app.get("/download")
async def download_video(request: Request, url: str = Query(..., description="TikTok video URL")):
    """Download TikTok video and return as file"""
    
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
            # Use cookies if available
            'cookiefile': None,
            'cookiesfrombrowser': None,
        }
        
        # Download video
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
        
        # Return file response
        return FileResponse(
            path=str(video_file),
            filename=f"{safe_title}.mp4",
            media_type='video/mp4',
            background=cleanup_temp_file(str(video_file), temp_dir)
        )
        
    except yt_dlp.DownloadError as e:
        # Se yt-dlp fallisce, prova il metodo fallback
        print(f"yt-dlp failed: {e}")
        print("Trying fallback method...")
        
        fallback_file = await fallback_tiktok_download(url, temp_dir)
        
        if fallback_file and os.path.exists(fallback_file):
            # Fallback successful!
            video_id_match = re.search(r'/video/(\d+)', url)
            safe_title = f"tiktok_video_{video_id_match.group(1)}" if video_id_match else "tiktok_video"
            
            return FileResponse(
                path=fallback_file,
                filename=f"{safe_title}.mp4",
                media_type='video/mp4',
                background=cleanup_temp_file(fallback_file, temp_dir)
            )
        
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

async def fallback_tiktok_download(url: str, temp_dir: str):
    """
    Fallback method using a different approach when yt-dlp fails
    """
    try:
        # Try to extract video ID from URL
        video_id_match = re.search(r'/video/(\d+)', url)
        if not video_id_match:
            return None
        
        video_id = video_id_match.group(1)
        
        # Use a simple approach to try to get video info
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.tiktok.com/',
        }
        
        # Try to get the page content
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Look for video URLs in the page content
            video_patterns = [
                r'"downloadAddr":"([^"]+)"',
                r'"playAddr":"([^"]+)"',
                r'playAddr":"([^"]+)"',
                r'"download_addr":"([^"]+)"',
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    # Try to download the first video URL found
                    video_url = matches[0].replace('\\u002F', '/')
                    
                    # Download the video
                    video_response = requests.get(video_url, headers=headers, timeout=30)
                    if video_response.status_code == 200:
                        # Save the video file
                        video_filename = f"tiktok_video_{video_id}.mp4"
                        video_path = os.path.join(temp_dir, video_filename)
                        
                        with open(video_path, 'wb') as f:
                            f.write(video_response.content)
                        
                        return video_path
        
        return None
        
    except Exception as e:
        print(f"Fallback method failed: {e}")
        return None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Tik To Mp4"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 