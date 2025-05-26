"""
Alternative TikTok downloader usando un approccio diverso
"""

import requests
import re
import json
from urllib.parse import urlparse, parse_qs

def extract_tiktok_video_id(url):
    """Estrae l'ID del video TikTok dall'URL"""
    # Pattern per diversi formati di URL TikTok
    patterns = [
        r'tiktok\.com/@[^/]+/video/(\d+)',
        r'vm\.tiktok\.com/([A-Za-z0-9]+)',
        r'vt\.tiktok\.com/([A-Za-z0-9]+)',
        r'm\.tiktok\.com/v/(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_tiktok_video_info(url):
    """
    Prova a ottenere informazioni sul video TikTok usando un approccio alternativo
    """
    try:
        # Headers per simulare un browser normale
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Prova a ottenere la pagina
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Cerca i dati JSON nella pagina
            content = response.text
            
            # Pattern per trovare i dati del video
            json_pattern = r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>'
            match = re.search(json_pattern, content)
            
            if match:
                try:
                    data = json.loads(match.group(1))
                    # Estrai informazioni del video
                    return {
                        'success': True,
                        'data': data,
                        'message': 'Video info extracted successfully'
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback: cerca altri pattern
            video_patterns = [
                r'"downloadAddr":"([^"]+)"',
                r'"playAddr":"([^"]+)"',
                r'playAddr":"([^"]+)"',
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    return {
                        'success': True,
                        'video_urls': matches,
                        'message': 'Video URLs found'
                    }
        
        return {
            'success': False,
            'message': f'Failed to fetch page. Status: {response.status_code}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }

def test_alternative_method(url):
    """Test del metodo alternativo"""
    print(f"🔍 Testing alternative method with: {url}")
    
    result = get_tiktok_video_info(url)
    
    if result['success']:
        print("✅ Alternative method successful!")
        print(f"📄 Message: {result['message']}")
        if 'video_urls' in result:
            print(f"🎥 Found {len(result['video_urls'])} video URLs")
        return True
    else:
        print(f"❌ Alternative method failed: {result['message']}")
        return False

if __name__ == "__main__":
    # Test con un URL TikTok
    test_url = "https://www.tiktok.com/@tiktok/video/7016451725845712133"
    test_alternative_method(test_url) 