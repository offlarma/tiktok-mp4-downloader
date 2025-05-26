from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
import re
import json

app = FastAPI(title="Tik To Mp4 - Simple Version")

# HTML semplificato che funziona
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tik To Mp4 - Download TikTok Videos Without Watermark | Free TikTok Downloader</title>
    <meta name="description" content="Free TikTok video downloader without watermark. Download TikTok videos in MP4 format quickly and easily. No registration required. Works on all devices.">
    <meta name="keywords" content="tiktok downloader, download tiktok video, tiktok to mp4, remove watermark, free tiktok download, tik to mp4">
    <meta name="author" content="Tik To Mp4">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://your-domain.com/">
    <meta property="og:title" content="Tik To Mp4 - Free TikTok Video Downloader">
    <meta property="og:description" content="Download TikTok videos without watermark for free. Fast, easy, and works on all devices.">
    <meta property="og:image" content="https://your-domain.com/og-image.jpg">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://your-domain.com/">
    <meta property="twitter:title" content="Tik To Mp4 - Free TikTok Video Downloader">
    <meta property="twitter:description" content="Download TikTok videos without watermark for free. Fast, easy, and works on all devices.">
    <meta property="twitter:image" content="https://your-domain.com/og-image.jpg">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="https://your-domain.com/">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'GA_MEASUREMENT_ID');
    </script>
    
    <!-- Google Search Console Verification -->
    <meta name="google-site-verification" content="YOUR_VERIFICATION_CODE" />
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; text-align: center; }
        input[type="url"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #ff0050;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #e6004a; }
        .info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .success { background: #d4edda; border-left: 4px solid #28a745; }
        .error { background: #f8d7da; border-left: 4px solid #dc3545; }
        
        /* Google Ads Styles */
        .ad-container {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            font-size: 14px;
        }
        
        .ad-banner {
            min-height: 90px;
            background: #f8f9fa;
            border: 1px dashed #dee2e6;
            margin: 15px 0;
        }
        
        .ad-sidebar {
            min-height: 250px;
            background: #f8f9fa;
            border: 1px dashed #dee2e6;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <!-- Top Banner Ad -->
    <div class="ad-container ad-banner">
        <!-- Google AdSense Banner 728x90 -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX"
                crossorigin="anonymous"></script>
        <ins class="adsbygoogle"
             style="display:inline-block;width:728px;height:90px"
             data-ad-client="ca-pub-XXXXXXXXXX"
             data-ad-slot="XXXXXXXXXX"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
        <!-- Placeholder text (remove when adding real ads) -->
        <div style="color: #999;">📢 Google Ads Banner (728x90) - Replace with your AdSense code</div>
    </div>

    <div class="container">
        <h1>🎵 Tik To Mp4</h1>
        <p style="text-align: center; color: #666;">Simple TikTok Video Downloader</p>
        
        <div class="info">
            <strong>📋 Instructions:</strong><br>
            1. Go to TikTok and copy a video URL<br>
            2. Paste it below and click "Get Download Link"<br>
            3. Click the download link that appears
        </div>
        
        <form id="downloadForm">
            <input type="url" id="tiktokUrl" placeholder="Paste TikTok URL here..." required>
            <button type="submit">Get Download Link</button>
        </form>
        
        <!-- Middle Ad -->
        <div class="ad-container">
            <!-- Google AdSense Rectangle 300x250 -->
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX"
                    crossorigin="anonymous"></script>
            <ins class="adsbygoogle"
                 style="display:inline-block;width:300px;height:250px"
                 data-ad-client="ca-pub-XXXXXXXXXX"
                 data-ad-slot="XXXXXXXXXX"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
            <!-- Placeholder text (remove when adding real ads) -->
            <div style="color: #999;">📢 Google Ads Rectangle (300x250) - Replace with your AdSense code</div>
        </div>
        
        <div id="result" class="result">
            <div id="resultContent"></div>
        </div>
    </div>
    
    <!-- Bottom Ad -->
    <div class="ad-container ad-banner">
        <!-- Google AdSense Banner 728x90 -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX"
                crossorigin="anonymous"></script>
        <ins class="adsbygoogle"
             style="display:inline-block;width:728px;height:90px"
             data-ad-client="ca-pub-XXXXXXXXXX"
             data-ad-slot="XXXXXXXXXX"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
        <!-- Placeholder text (remove when adding real ads) -->
        <div style="color: #999;">📢 Google Ads Banner (728x90) - Replace with your AdSense code</div>
    </div>
    
    <!-- Footer with more ads space -->
    <div style="max-width: 600px; margin: 20px auto; padding: 20px;">
        <div class="ad-container">
            <!-- Google AdSense Large Rectangle 336x280 -->
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX"
                    crossorigin="anonymous"></script>
            <ins class="adsbygoogle"
                 style="display:inline-block;width:336px;height:280px"
                 data-ad-client="ca-pub-XXXXXXXXXX"
                 data-ad-slot="XXXXXXXXXX"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
            <!-- Placeholder text (remove when adding real ads) -->
                         <div style="color: #999;">📢 Google Ads Large Rectangle (336x280) - Replace with your AdSense code</div>
         </div>
     </div>
     
     <!-- SEO Content Section -->
     <div style="max-width: 600px; margin: 20px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
         <h2 style="color: #333; margin-bottom: 15px;">🎥 Free TikTok Video Downloader</h2>
         <p style="color: #666; line-height: 1.6; margin-bottom: 15px;">
             Download TikTok videos without watermark for free! Our TikTok downloader allows you to save TikTok videos in MP4 format 
             directly to your device. No registration required, works on all devices including mobile phones, tablets, and computers.
         </p>
         
         <h3 style="color: #333; margin: 20px 0 10px 0;">✨ Features:</h3>
         <ul style="color: #666; line-height: 1.8; margin-left: 20px;">
             <li>🚫 Remove watermark from TikTok videos</li>
             <li>📱 Works on mobile, tablet, and desktop</li>
             <li>⚡ Fast and reliable downloads</li>
             <li>🆓 Completely free to use</li>
             <li>🔒 No registration or login required</li>
             <li>💾 Download in high quality MP4 format</li>
         </ul>
         
         <h3 style="color: #333; margin: 20px 0 10px 0;">📋 How to use:</h3>
         <ol style="color: #666; line-height: 1.8; margin-left: 20px;">
             <li>Copy the TikTok video URL from the app or website</li>
             <li>Paste the URL in the input field above</li>
             <li>Click "Get Download Link" button</li>
             <li>Click the download link to save the video</li>
         </ol>
         
         <p style="color: #666; line-height: 1.6; margin-top: 20px; font-size: 14px;">
             <strong>Keywords:</strong> TikTok downloader, download TikTok video, TikTok to MP4, remove watermark, 
                           free TikTok download, save TikTok video, TikTok video saver, online TikTok downloader
          </p>
          
          <!-- Footer Links -->
          <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
              <p style="color: #999; font-size: 12px;">
                  <a href="/privacy" style="color: #666; text-decoration: none; margin: 0 10px;">Privacy Policy</a> |
                  <a href="/terms" style="color: #666; text-decoration: none; margin: 0 10px;">Terms of Service</a> |
                  <a href="/contact" style="color: #666; text-decoration: none; margin: 0 10px;">Contact</a>
              </p>
              <p style="color: #999; font-size: 12px;">© 2024 Tik To Mp4. All rights reserved.</p>
          </div>
      </div>

    <script>
        document.getElementById('downloadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('tiktokUrl').value;
            const result = document.getElementById('result');
            const content = document.getElementById('resultContent');
            
            result.style.display = 'block';
            result.className = 'result';
            content.innerHTML = '⏳ Processing...';
            
            try {
                const response = await fetch(`/get-download-link?url=${encodeURIComponent(url)}`);
                const data = await response.json();
                
                if (data.success) {
                    result.className = 'result success';
                    content.innerHTML = `
                        <strong>✅ Success!</strong><br>
                        <strong>Title:</strong> ${data.title || 'TikTok Video'}<br>
                        <a href="${data.download_url}" target="_blank" style="
                            display: inline-block;
                            margin-top: 10px;
                            padding: 10px 20px;
                            background: #28a745;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                        ">📥 Download Video</a>
                    `;
                } else {
                    result.className = 'result error';
                    content.innerHTML = `<strong>❌ Error:</strong> ${data.message}`;
                }
            } catch (error) {
                result.className = 'result error';
                content.innerHTML = `<strong>❌ Error:</strong> ${error.message}`;
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/get-download-link")
async def get_download_link(url: str = Query(...)):
    """Get download link using a simple API approach"""
    
    # Validate TikTok URL
    if not any(domain in url.lower() for domain in ['tiktok.com', 'vm.tiktok.com']):
        return {"success": False, "message": "Please provide a valid TikTok URL"}
    
    try:
        # Method 1: Try to extract video info directly
        video_id = extract_video_id(url)
        if not video_id:
            return {"success": False, "message": "Could not extract video ID from URL"}
        
        # Method 2: Use a simple API service (example)
        # This is a placeholder - you would use a real service
        download_url = f"https://tikcdn.io/ssstik/{video_id}"
        
        return {
            "success": True,
            "title": f"TikTok Video {video_id}",
            "download_url": download_url,
            "message": "Download link generated successfully"
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def extract_video_id(url):
    """Extract video ID from TikTok URL"""
    patterns = [
        r'/video/(\d+)',
        r'vm\.tiktok\.com/([A-Za-z0-9]+)',
        r'vt\.tiktok\.com/([A-Za-z0-9]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Simple TikTok downloader is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 