#!/usr/bin/env python3
"""
Test script per verificare che yt-dlp funzioni con TikTok
"""

import yt_dlp
import tempfile
import os

def test_tiktok_download():
    """Test di download TikTok"""
    
    # URL di test (usa un URL TikTok pubblico)
    test_url = "https://www.tiktok.com/@tiktok/video/7016451725845712133"
    
    # Crea directory temporanea
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Configurazione yt-dlp migliorata
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
        }
        
        print(f"🔍 Testing TikTok download with URL: {test_url}")
        print("📥 Attempting to extract video info...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Prima estrai solo le informazioni
            info = ydl.extract_info(test_url, download=False)
            
            print(f"✅ Video info extracted successfully!")
            print(f"📹 Title: {info.get('title', 'Unknown')}")
            print(f"👤 Uploader: {info.get('uploader', 'Unknown')}")
            print(f"⏱️ Duration: {info.get('duration', 'Unknown')} seconds")
            
            # Ora prova il download
            print("📥 Attempting download...")
            ydl.download([test_url])
            
            # Verifica se il file è stato scaricato
            files = os.listdir(temp_dir)
            if files:
                print(f"✅ Download successful! File: {files[0]}")
                return True
            else:
                print("❌ Download failed - no file created")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

if __name__ == "__main__":
    print("🚀 TikTok Download Test")
    print("=" * 50)
    
    success = test_tiktok_download()
    
    print("=" * 50)
    if success:
        print("🎉 Test PASSED! TikTok download is working!")
    else:
        print("💥 Test FAILED! Check the error messages above.")
        print("\n💡 Possible solutions:")
        print("   1. Update yt-dlp: py -m pip install --upgrade yt-dlp")
        print("   2. Try a different TikTok URL")
        print("   3. Check your internet connection")
        print("   4. TikTok might have updated their anti-bot measures") 