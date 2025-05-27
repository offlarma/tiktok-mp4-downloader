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
# Blog Templates
BLOG_INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Learn how to download TikTok videos without watermark. Complete guides and tutorials for Tik To Mp4 converter.">
    <meta name="keywords" content="how to download tiktok video, tiktok downloader guide, download tiktok without watermark, tik to mp4 tutorial">
    <title>How to Download TikTok Videos - Complete Guide | Tik To Mp4 Blog</title>
    <link rel="canonical" href="https://www.tikto-mp4.com/blog">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #4ecdc4; padding-bottom: 10px; }
        .post-list { list-style: none; padding: 0; }
        .post-item { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #ff6b6b; }
        .post-item h3 { margin: 0 0 10px 0; }
        .post-item a { text-decoration: none; color: #333; font-weight: bold; }
        .post-item a:hover { color: #4ecdc4; }
        .back-home { display: inline-block; margin-top: 30px; padding: 10px 20px; background: #4ecdc4; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Tik To Mp4 Blog - How to Download TikTok Videos</h1>
        <p>Learn everything about downloading TikTok videos without watermark with our comprehensive guides.</p>
        
        <ul class="post-list">
            <li class="post-item">
                <h3><a href="/blog/how-to-download-tiktok-video">How to Download TikTok Video - Complete Guide 2024</a></h3>
                <p>Step-by-step tutorial on downloading any TikTok video quickly and easily.</p>
            </li>
            
            <li class="post-item">
                <h3><a href="/blog/how-to-download-tiktok-videos-without-watermark">How to Download TikTok Videos Without Watermark</a></h3>
                <p>Remove watermarks from TikTok videos with our advanced Tik To Mp4 converter.</p>
            </li>
            
            <li class="post-item">
                <h3><a href="/blog/how-to-save-tiktok-without-watermark">How to Save TikTok Without Watermark</a></h3>
                <p>Best methods to save TikTok videos in high quality without any watermarks.</p>
            </li>
            
            <li class="post-item">
                <h3><a href="/blog/how-to-download-tik-tok-video-without-watermark">How to Download Tik Tok Video Without Watermark</a></h3>
                <p>Professional techniques for downloading clean TikTok videos for any purpose.</p>
            </li>
        </ul>
        
        <a href="/" class="back-home">🏠 Back to Tik To Mp4 Converter</a>
    </div>
</body>
</html>
"""

BLOG_POST_1_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Learn how to download TikTok video in 2024. Complete step-by-step guide using Tik To Mp4 converter. Fast, free, and easy method.">
    <meta name="keywords" content="how to download tiktok video, tiktok video download, download tiktok, tik to mp4, tiktok downloader">
    <title>How to Download TikTok Video - Complete Guide 2024 | Tik To Mp4</title>
    <link rel="canonical" href="https://www.tikto-mp4.com/blog/how-to-download-tiktok-video">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        h1 { border-bottom: 3px solid #4ecdc4; padding-bottom: 10px; }
        .step { background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #ff6b6b; }
        .cta-box { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }
        .cta-box a { color: white; font-weight: bold; text-decoration: none; background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 5px; display: inline-block; margin-top: 10px; }
        .back-links { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        .back-links a { margin-right: 20px; color: #4ecdc4; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 How to Download TikTok Video - Complete Guide 2024</h1>
        
        <p>Want to learn <strong>how to download TikTok video</strong> quickly and easily? You're in the right place! This comprehensive guide will show you the best method to download any TikTok video in just a few clicks.</p>
        
        <div class="cta-box">
            <h3>🚀 Try Tik To Mp4 Converter Now!</h3>
            <p>Download any TikTok video instantly with our free converter</p>
            <a href="/">Start Downloading →</a>
        </div>
        
        <h2>🎯 Why Download TikTok Videos?</h2>
        <ul>
            <li><strong>Save favorites:</strong> Keep your favorite TikTok videos forever</li>
            <li><strong>Offline viewing:</strong> Watch videos without internet connection</li>
            <li><strong>Share easily:</strong> Send videos to friends via other platforms</li>
            <li><strong>Content creation:</strong> Use videos for your own projects</li>
        </ul>
        
        <h2>📋 How to Download TikTok Video - Step by Step</h2>
        
        <div class="step">
            <h3>Step 1: Copy the TikTok Video URL</h3>
            <p>Open TikTok app or website, find the video you want to download, and tap the "Share" button. Then select "Copy Link" to copy the video URL.</p>
        </div>
        
        <div class="step">
            <h3>Step 2: Open Tik To Mp4 Converter</h3>
            <p>Visit our <a href="/">Tik To Mp4 converter</a> - the best free tool to download TikTok videos without watermark.</p>
        </div>
        
        <div class="step">
            <h3>Step 3: Paste the URL</h3>
            <p>Paste the copied TikTok URL into the input field on our converter page.</p>
        </div>
        
        <div class="step">
            <h3>Step 4: Click Download</h3>
            <p>Click the "Download Video" button and wait for the processing to complete (usually 30-90 seconds).</p>
        </div>
        
        <div class="step">
            <h3>Step 5: Save Your Video</h3>
            <p>The video will automatically download to your device in MP4 format, ready to watch offline!</p>
        </div>
        
        <h2>✨ Why Choose Tik To Mp4?</h2>
        <ul>
            <li>🆓 <strong>Completely free</strong> - no hidden costs</li>
            <li>🚫 <strong>No watermark</strong> - clean video downloads</li>
            <li>📱 <strong>Works on all devices</strong> - mobile, tablet, desktop</li>
            <li>⚡ <strong>Fast processing</strong> - downloads in seconds</li>
            <li>🔒 <strong>No registration</strong> - start downloading immediately</li>
        </ul>
        
        <h2>🔧 Troubleshooting Tips</h2>
        <p>If you're having trouble downloading a TikTok video:</p>
        <ul>
            <li>Make sure the video is public (not private)</li>
            <li>Check your internet connection</li>
            <li>Try copying the URL again</li>
            <li>Clear your browser cache</li>
        </ul>
        
        <div class="cta-box">
            <h3>🎬 Ready to Download TikTok Videos?</h3>
            <p>Start using our free Tik To Mp4 converter now!</p>
            <a href="/">Download TikTok Videos →</a>
        </div>
        
        <h2>📚 Related Guides</h2>
        <ul>
            <li><a href="/blog/how-to-download-tiktok-videos-without-watermark">How to Download TikTok Videos Without Watermark</a></li>
            <li><a href="/blog/how-to-save-tiktok-without-watermark">How to Save TikTok Without Watermark</a></li>
        </ul>
        
        <div class="back-links">
            <a href="/blog">← Back to Blog</a>
            <a href="/">🏠 Tik To Mp4 Converter</a>
        </div>
    </div>
</body>
</html>
 """

BLOG_POST_2_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Learn how to download TikTok videos without watermark. Remove watermarks easily with Tik To Mp4 converter. Free and fast method.">
    <meta name="keywords" content="how to download tiktok videos without watermark, remove tiktok watermark, tiktok no watermark, tik to mp4">
    <title>How to Download TikTok Videos Without Watermark | Tik To Mp4</title>
    <link rel="canonical" href="https://www.tikto-mp4.com/blog/how-to-download-tiktok-videos-without-watermark">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        h1 { border-bottom: 3px solid #4ecdc4; padding-bottom: 10px; }
        .highlight { background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0; }
        .cta-box { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }
        .cta-box a { color: white; font-weight: bold; text-decoration: none; background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 5px; display: inline-block; margin-top: 10px; }
        .back-links { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        .back-links a { margin-right: 20px; color: #4ecdc4; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚫 How to Download TikTok Videos Without Watermark</h1>
        
        <p>Looking to <strong>download TikTok videos without watermark</strong>? You've found the perfect solution! Our Tik To Mp4 converter automatically removes watermarks, giving you clean, professional-quality videos.</p>
        
        <div class="highlight">
            <strong>💡 Pro Tip:</strong> Watermarks can be distracting and unprofessional. Remove them easily with our free converter!
        </div>
        
        <div class="cta-box">
            <h3>🎯 Remove Watermarks Now!</h3>
            <p>Get clean TikTok videos without any watermarks</p>
            <a href="/">Start Converting →</a>
        </div>
        
        <h2>🤔 Why Remove TikTok Watermarks?</h2>
        <ul>
            <li><strong>Professional use:</strong> Clean videos for business presentations</li>
            <li><strong>Content creation:</strong> Use in your own videos without branding</li>
            <li><strong>Social sharing:</strong> Share on other platforms without TikTok logo</li>
            <li><strong>Personal collection:</strong> Archive videos without distractions</li>
        </ul>
        
        <h2>🛠️ How to Download TikTok Videos Without Watermark</h2>
        
        <h3>Method 1: Using Tik To Mp4 Converter (Recommended)</h3>
        <ol>
            <li>Copy the TikTok video URL</li>
            <li>Visit our <a href="/">Tik To Mp4 converter</a></li>
            <li>Paste the URL in the input field</li>
            <li>Click "Download Video"</li>
            <li>Get your watermark-free video in MP4 format!</li>
        </ol>
        
        <h3>✨ Why Our Method Works Best</h3>
        <ul>
            <li>🎯 <strong>Automatic watermark removal</strong> - no manual editing needed</li>
            <li>🆓 <strong>100% free</strong> - no subscription or payment required</li>
            <li>⚡ <strong>Fast processing</strong> - results in under 2 minutes</li>
            <li>📱 <strong>Works everywhere</strong> - mobile, tablet, desktop</li>
            <li>🔒 <strong>Safe and secure</strong> - no malware or viruses</li>
        </ul>
        
        <h2>🎬 Video Quality After Watermark Removal</h2>
        <p>Our Tik To Mp4 converter maintains the original video quality while removing watermarks:</p>
        <ul>
            <li><strong>Resolution:</strong> Same as original (up to 1080p)</li>
            <li><strong>Audio:</strong> Crystal clear, no quality loss</li>
            <li><strong>Format:</strong> MP4 (compatible with all devices)</li>
            <li><strong>File size:</strong> Optimized for quick downloads</li>
        </ul>
        
        <div class="cta-box">
            <h3>🚀 Ready to Remove Watermarks?</h3>
            <p>Try our free Tik To Mp4 converter now!</p>
            <a href="/">Download Without Watermark →</a>
        </div>
        
        <h2>📚 Related Guides</h2>
        <ul>
            <li><a href="/blog/how-to-download-tiktok-video">How to Download TikTok Video - Complete Guide</a></li>
            <li><a href="/blog/how-to-save-tiktok-without-watermark">How to Save TikTok Without Watermark</a></li>
        </ul>
        
        <div class="back-links">
            <a href="/blog">← Back to Blog</a>
            <a href="/">🏠 Tik To Mp4 Converter</a>
        </div>
    </div>
</body>
</html>
"""

BLOG_POST_3_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Learn how to save TikTok without watermark. Best methods to save clean TikTok videos using Tik To Mp4 converter.">
    <meta name="keywords" content="how to save tiktok without watermark, save tiktok video, tiktok saver, download tiktok clean">
    <title>How to Save TikTok Without Watermark - Best Methods | Tik To Mp4</title>
    <link rel="canonical" href="https://www.tikto-mp4.com/blog/how-to-save-tiktok-without-watermark">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        h1 { border-bottom: 3px solid #4ecdc4; padding-bottom: 10px; }
        .method { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #28a745; }
        .cta-box { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }
        .cta-box a { color: white; font-weight: bold; text-decoration: none; background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 5px; display: inline-block; margin-top: 10px; }
        .back-links { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        .back-links a { margin-right: 20px; color: #4ecdc4; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💾 How to Save TikTok Without Watermark</h1>
        
        <p>Want to <strong>save TikTok without watermark</strong> for your personal collection? This guide shows you the most effective methods to save clean, professional-quality TikTok videos.</p>
        
        <div class="cta-box">
            <h3>💫 Save TikTok Videos Now!</h3>
            <p>Get watermark-free TikTok videos instantly</p>
            <a href="/">Start Saving →</a>
        </div>
        
        <h2>🎯 Best Methods to Save TikTok Without Watermark</h2>
        
        <div class="method">
            <h3>Method 1: Tik To Mp4 Converter (Easiest)</h3>
            <p><strong>Best for:</strong> Quick, hassle-free saving</p>
            <ol>
                <li>Copy TikTok video link</li>
                <li>Open <a href="/">Tik To Mp4 converter</a></li>
                <li>Paste link and click download</li>
                <li>Save clean video to your device</li>
            </ol>
        </div>
        
        <div class="method">
            <h3>Method 2: Mobile App Saving</h3>
            <p><strong>Best for:</strong> Saving directly on phone</p>
            <ul>
                <li>Use our mobile-optimized converter</li>
                <li>Works on iOS and Android</li>
                <li>Save directly to camera roll</li>
            </ul>
        </div>
        
        <div class="method">
            <h3>Method 3: Bulk Saving</h3>
            <p><strong>Best for:</strong> Saving multiple videos</p>
            <ul>
                <li>Save multiple TikTok URLs</li>
                <li>Process them one by one</li>
                <li>Build your watermark-free collection</li>
            </ul>
        </div>
        
        <h2>📱 Saving TikTok on Different Devices</h2>
        
        <h3>💻 Desktop/Laptop</h3>
        <ul>
            <li>Right-click to save video file</li>
            <li>Choose download location</li>
            <li>Organize in folders</li>
        </ul>
        
        <h3>📱 Mobile (iOS/Android)</h3>
        <ul>
            <li>Tap and hold to save</li>
            <li>Save to Photos/Gallery</li>
            <li>Share to other apps</li>
        </ul>
        
        <h2>🔧 Tips for Better TikTok Saving</h2>
        <ul>
            <li><strong>Check video quality:</strong> Choose highest available resolution</li>
            <li><strong>Organize files:</strong> Create folders by date or topic</li>
            <li><strong>Backup important videos:</strong> Save to cloud storage</li>
            <li><strong>Respect copyright:</strong> Only save for personal use</li>
        </ul>
        
        <div class="cta-box">
            <h3>🎬 Start Saving TikTok Videos!</h3>
            <p>Use our free converter to save clean videos</p>
            <a href="/">Save Without Watermark →</a>
        </div>
        
        <h2>📚 Related Guides</h2>
        <ul>
            <li><a href="/blog/how-to-download-tiktok-video">How to Download TikTok Video</a></li>
            <li><a href="/blog/how-to-download-tiktok-videos-without-watermark">How to Download TikTok Videos Without Watermark</a></li>
        </ul>
        
        <div class="back-links">
            <a href="/blog">← Back to Blog</a>
            <a href="/">🏠 Tik To Mp4 Converter</a>
        </div>
    </div>
</body>
</html>
"""

BLOG_POST_4_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Professional guide on how to download Tik Tok video without watermark. Advanced techniques using Tik To Mp4 converter.">
    <meta name="keywords" content="how to download tik tok video without watermark, tik tok downloader, remove watermark tik tok">
    <title>How to Download Tik Tok Video Without Watermark - Pro Guide | Tik To Mp4</title>
    <link rel="canonical" href="https://www.tikto-mp4.com/blog/how-to-download-tik-tok-video-without-watermark">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        h1 { border-bottom: 3px solid #4ecdc4; padding-bottom: 10px; }
        .pro-tip { background: #e8f5e8; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; margin: 20px 0; }
        .cta-box { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); color: white; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; }
        .cta-box a { color: white; font-weight: bold; text-decoration: none; background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 5px; display: inline-block; margin-top: 10px; }
        .back-links { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        .back-links a { margin-right: 20px; color: #4ecdc4; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 How to Download Tik Tok Video Without Watermark - Professional Guide</h1>
        
        <p>Master the art of <strong>downloading Tik Tok video without watermark</strong> with our professional techniques. Get clean, high-quality videos for any purpose using advanced methods.</p>
        
        <div class="cta-box">
            <h3>🚀 Professional Tik Tok Downloader</h3>
            <p>Download clean Tik Tok videos like a pro</p>
            <a href="/">Start Professional Download →</a>
        </div>
        
        <h2>🎬 Professional Use Cases</h2>
        <ul>
            <li><strong>Content creation:</strong> Use in your own videos</li>
            <li><strong>Marketing materials:</strong> Clean videos for campaigns</li>
            <li><strong>Educational content:</strong> Teaching and presentations</li>
            <li><strong>Research purposes:</strong> Academic and professional analysis</li>
        </ul>
        
        <h2>🛠️ Advanced Download Techniques</h2>
        
        <div class="pro-tip">
            <h3>🎯 Pro Technique 1: Quality Optimization</h3>
            <p>Our Tik To Mp4 converter automatically selects the highest quality version available, ensuring professional results every time.</p>
        </div>
        
        <div class="pro-tip">
            <h3>⚡ Pro Technique 2: Batch Processing</h3>
            <p>For multiple videos, bookmark our converter and process videos one after another for efficient workflow.</p>
        </div>
        
        <div class="pro-tip">
            <h3>🔧 Pro Technique 3: Format Optimization</h3>
            <p>All downloads are in MP4 format, ensuring compatibility with all editing software and devices.</p>
        </div>
        
        <h2>📊 Quality Comparison</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background: #f8f9fa;">
                <th style="padding: 10px; border: 1px solid #ddd;">Method</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Quality</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Watermark</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Speed</th>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">Tik To Mp4</td>
                <td style="padding: 10px; border: 1px solid #ddd;">🟢 High</td>
                <td style="padding: 10px; border: 1px solid #ddd;">🚫 Removed</td>
                <td style="padding: 10px; border: 1px solid #ddd;">⚡ Fast</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">Screen Recording</td>
                <td style="padding: 10px; border: 1px solid #ddd;">🟡 Medium</td>
                <td style="padding: 10px; border: 1px solid #ddd;">✅ Present</td>
                <td style="padding: 10px; border: 1px solid #ddd;">🐌 Slow</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">Other Tools</td>
                <td style="padding: 10px; border: 1px solid #ddd;">🟡 Variable</td>
                <td style="padding: 10px; border: 1px solid #ddd;">🟡 Sometimes</td>
                <td style="padding: 10px; border: 1px solid #ddd;">🟡 Variable</td>
            </tr>
        </table>
        
        <h2>🔒 Professional Best Practices</h2>
        <ul>
            <li><strong>Copyright compliance:</strong> Only download videos you have permission to use</li>
            <li><strong>Quality control:</strong> Always check video quality before using</li>
            <li><strong>File organization:</strong> Maintain proper file naming and folder structure</li>
            <li><strong>Backup strategy:</strong> Keep copies of important downloads</li>
        </ul>
        
        <div class="cta-box">
            <h3>🎯 Ready for Professional Downloads?</h3>
            <p>Use our advanced Tik To Mp4 converter now</p>
            <a href="/">Download Professionally →</a>
        </div>
        
        <h2>📚 Complete Guide Series</h2>
        <ul>
            <li><a href="/blog/how-to-download-tiktok-video">How to Download TikTok Video - Beginner Guide</a></li>
            <li><a href="/blog/how-to-download-tiktok-videos-without-watermark">How to Download TikTok Videos Without Watermark</a></li>
            <li><a href="/blog/how-to-save-tiktok-without-watermark">How to Save TikTok Without Watermark</a></li>
        </ul>
        
        <div class="back-links">
            <a href="/blog">← Back to Blog</a>
            <a href="/">🏠 Tik To Mp4 Converter</a>
        </div>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="description" content="Tik To Mp4 - Free TikTok video downloader without watermark. Download TikTok videos to MP4 format instantly. Best Tik To Mp4 converter online.">
    <meta name="keywords" content="Tik To Mp4, TikTok downloader, download TikTok video, TikTok to MP4, remove watermark, free TikTok download, Tik To Mp4 converter, TikTok video saver">
    <meta name="author" content="Tik To Mp4">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="googlebot" content="index, follow">
    <link rel="canonical" href="https://www.tikto-mp4.com/">
    <title>Tik To Mp4 - Free TikTok Video Downloader Without Watermark | Best Tik To Mp4 Converter</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><defs><linearGradient id='grad1' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' style='stop-color:%23ff6b6b;stop-opacity:1' /><stop offset='50%25' style='stop-color:%234ecdc4;stop-opacity:1' /><stop offset='100%25' style='stop-color:%2345b7d1;stop-opacity:1' /></linearGradient></defs><circle cx='50' cy='50' r='45' fill='url(%23grad1)' stroke='white' stroke-width='3'/><text x='50' y='65' font-family='Arial, sans-serif' font-size='45' font-weight='bold' text-anchor='middle' fill='white'>🎵</text></svg>">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><defs><linearGradient id='grad1' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' style='stop-color:%23ff6b6b;stop-opacity:1' /><stop offset='50%25' style='stop-color:%234ecdc4;stop-opacity:1' /><stop offset='100%25' style='stop-color:%2345b7d1;stop-opacity:1' /></linearGradient></defs><circle cx='50' cy='50' r='45' fill='url(%23grad1)' stroke='white' stroke-width='3'/><text x='50' y='65' font-family='Arial, sans-serif' font-size='45' font-weight='bold' text-anchor='middle' fill='white'>🎵</text></svg>">
    
    <!-- Google Analytics - ORDINE CORRETTO -->
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        
        // Inizializza gtag PRIMA di tutto
        gtag('js', new Date());
        
        // Consent mode PERMISSIVO per analytics
        gtag('consent', 'default', {
            'ad_storage': 'granted',
            'ad_user_data': 'granted', 
            'ad_personalization': 'granted',
            'analytics_storage': 'granted'
        });
        
        // Configura Analytics
        gtag('config', 'G-5Q7ZFCF4K8', {
            'anonymize_ip': true,
            'allow_google_signals': true,
            'allow_ad_personalization_signals': true
        });
        
        // Track download events
        function trackDownload(url) {
            gtag('event', 'download', {
                'event_category': 'TikTok',
                'event_label': 'Video Download',
                'value': 1
            });
        }
    </script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-5Q7ZFCF4K8"></script>
    
    <!-- Google AdSense - Ottimizzato -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2184814096326522"
         crossorigin="anonymous"></script>
    <script>
        window.adsbygoogle = window.adsbygoogle || [];
    </script>
    
    <!-- Google Funding Choices (CMP) -->
    <script async src="https://fundingchoicesmessages.google.com/i/pub-2184814096326522?ers=1" nonce="RANDOM_NONCE"></script>
    <script nonce="RANDOM_NONCE">(function() {function signalGooglefcPresent() {if (!window.frames['googlefcPresent']) {if (document.body) {const iframe = document.createElement('iframe'); iframe.style = 'width: 0; height: 0; border: none; z-index: -1000; left: -1000px; top: -1000px;'; iframe.style.display = 'none'; iframe.name = 'googlefcPresent'; document.body.appendChild(iframe);} else {setTimeout(signalGooglefcPresent, 0);}}}signalGooglefcPresent();})();</script>
    
    <!-- Schema.org Structured Data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Tik To Mp4",
        "description": "Free TikTok video downloader without watermark. Download TikTok videos to MP4 format instantly.",
        "url": "https://www.tikto-mp4.com",
        "applicationCategory": "MultimediaApplication",
        "operatingSystem": "Any",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "featureList": [
            "Download TikTok videos without watermark",
            "Convert TikTok to MP4",
            "Free online converter",
            "Works on all devices",
            "No registration required"
        ],
        "author": {
            "@type": "Organization",
            "name": "Tik To Mp4"
        }
    }
    </script>
    
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
    
        <!-- AdSense Banner Top -->
    <div style="text-align: center; margin: 20px 0; max-width: 420px;">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-2184814096326522"
             data-ad-slot="1234567890"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
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
        
        <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
            <a href="/blog" style="color: #4ecdc4; text-decoration: none; font-weight: bold;">
                📚 Read Our Complete TikTok Download Guides →
            </a>
        </div>
    </div>
    
    <!-- AdSense Banner Bottom -->
    <div style="text-align: center; margin: 30px auto; max-width: 420px;">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-2184814096326522"
             data-ad-slot="9876543210"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
    </div>

    <script>
        // Track page view
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_view', {
                'page_title': 'Tik To Mp4 Homepage',
                'page_location': window.location.href
            });
        }
        
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
                    // Track download event
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'download', {
                            'event_category': 'TikTok',
                            'event_label': 'Video Download Success',
                            'value': 1
                        });
                    }
                    
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
        
        // Initialize AdSense ads
        try {
            (adsbygoogle = window.adsbygoogle || []).push({});
            (adsbygoogle = window.adsbygoogle || []).push({});
        } catch (e) {
            console.log('AdSense not ready yet');
        }
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

# Blog Routes
@app.get("/blog", response_class=HTMLResponse)
async def blog_index():
    return HTMLResponse(content=BLOG_INDEX_TEMPLATE)

@app.get("/blog/how-to-download-tiktok-video", response_class=HTMLResponse)
async def blog_post_1():
    return HTMLResponse(content=BLOG_POST_1_TEMPLATE)

@app.get("/blog/how-to-download-tiktok-videos-without-watermark", response_class=HTMLResponse)
async def blog_post_2():
    return HTMLResponse(content=BLOG_POST_2_TEMPLATE)

@app.get("/blog/how-to-save-tiktok-without-watermark", response_class=HTMLResponse)
async def blog_post_3():
    return HTMLResponse(content=BLOG_POST_3_TEMPLATE)

@app.get("/blog/how-to-download-tik-tok-video-without-watermark", response_class=HTMLResponse)
async def blog_post_4():
    return HTMLResponse(content=BLOG_POST_4_TEMPLATE)

@app.get("/ads.txt")
async def ads_txt():
    """Serve ads.txt file for Google AdSense"""
    return "google.com, pub-2184814096326522, DIRECT, f08c47fec0942fa0"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 