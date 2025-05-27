"""
Downloader TikTok migliorato con multiple strategie
"""

import os
import tempfile
import asyncio
import aiohttp
import aiofiles
import requests
import re
import json
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs, unquote
import time
import random

class TikTokDownloader:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
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
        """Crea una sessione aiohttp"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
        return self.session

    async def close_session(self):
        """Chiude la sessione"""
        if self.session:
            await self.session.close()
            self.session = None

    def extract_video_id(self, url: str) -> Optional[str]:
        """Estrae l'ID del video dall'URL TikTok"""
        patterns = [
            r'tiktok\.com/@[^/]+/video/(\d+)',
            r'vm\.tiktok\.com/([A-Za-z0-9]+)',
            r'vt\.tiktok\.com/([A-Za-z0-9]+)',
            r'm\.tiktok\.com/v/(\d+)',
            r'tiktok\.com/t/([A-Za-z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def resolve_short_url(self, url: str) -> str:
        """Risolve URL corti di TikTok"""
        if 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
            try:
                session = await self.create_session()
                async with session.get(url, allow_redirects=True) as response:
                    return str(response.url)
            except:
                pass
        return url

    async def method_1_api_approach(self, url: str) -> Optional[Dict[str, Any]]:
        """Metodo 1: Approccio tramite API TikTok"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return None

            # API endpoint (questo potrebbe cambiare)
            api_url = f"https://api.tiktokv.com/aweme/v1/aweme/detail/?aweme_id={video_id}"
            
            session = await self.create_session()
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'aweme_detail' in data:
                        video_data = data['aweme_detail']['video']
                        download_url = video_data.get('download_addr', {}).get('url_list', [])
                        if download_url:
                            return {
                                'success': True,
                                'download_url': download_url[0],
                                'title': data['aweme_detail'].get('desc', 'tiktok_video'),
                                'method': 'api_approach'
                            }
        except Exception as e:
            print(f"Method 1 failed: {e}")
        return None

    async def method_2_web_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """Metodo 2: Web scraping della pagina TikTok"""
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
                                # Cerca URL del video nei dati
                                video_urls = self._extract_video_urls_from_data(data)
                                if video_urls:
                                    return {
                                        'success': True,
                                        'download_url': video_urls[0],
                                        'title': self._extract_title_from_data(data),
                                        'method': 'web_scraping'
                                    }
                            except json.JSONDecodeError:
                                continue
                    
                    # Fallback: cerca pattern diretti nell'HTML
                    video_patterns = [
                        r'"downloadAddr":"([^"]+)"',
                        r'"playAddr":"([^"]+)"',
                        r'playAddr":"([^"]+)"',
                        r'"download_addr":"([^"]+)"',
                    ]
                    
                    for pattern in video_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            # Decodifica URL se necessario
                            video_url = matches[0].replace('\\u002F', '/').replace('\\/', '/')
                            return {
                                'success': True,
                                'download_url': video_url,
                                'title': 'tiktok_video',
                                'method': 'pattern_matching'
                            }
        except Exception as e:
            print(f"Method 2 failed: {e}")
        return None

    async def method_3_third_party_api(self, url: str) -> Optional[Dict[str, Any]]:
        """Metodo 3: Usa API di terze parti"""
        try:
            # Lista di API gratuite per TikTok (queste potrebbero cambiare)
            apis = [
                {
                    'url': 'https://tikwm.com/api/',
                    'params': {'url': url, 'hd': '1'}
                },
                {
                    'url': 'https://www.tikwm.com/api/',
                    'params': {'url': url}
                }
            ]
            
            session = await self.create_session()
            
            for api in apis:
                try:
                    async with session.get(api['url'], params=api['params']) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('code') == 0 and 'data' in data:
                                video_data = data['data']
                                download_url = video_data.get('hdplay') or video_data.get('play')
                                if download_url:
                                    return {
                                        'success': True,
                                        'download_url': download_url,
                                        'title': video_data.get('title', 'tiktok_video'),
                                        'method': 'third_party_api'
                                    }
                except Exception as e:
                    print(f"API {api['url']} failed: {e}")
                    continue
        except Exception as e:
            print(f"Method 3 failed: {e}")
        return None

    def _extract_video_urls_from_data(self, data: Dict) -> list:
        """Estrae URL video dai dati JSON"""
        urls = []
        
        def search_recursive(obj, keys_to_find):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in keys_to_find and isinstance(value, str) and 'http' in value:
                        urls.append(value)
                    elif isinstance(value, (dict, list)):
                        search_recursive(value, keys_to_find)
            elif isinstance(obj, list):
                for item in obj:
                    search_recursive(item, keys_to_find)
        
        keys_to_find = ['downloadAddr', 'playAddr', 'download_addr', 'play_addr', 'url']
        search_recursive(data, keys_to_find)
        
        return urls

    def _extract_title_from_data(self, data: Dict) -> str:
        """Estrae il titolo dai dati JSON"""
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

    async def download_video_file(self, download_url: str, temp_dir: str, filename: str) -> Optional[str]:
        """Scarica il file video"""
        try:
            session = await self.create_session()
            
            # Headers specifici per il download
            download_headers = {
                **self.headers,
                'Referer': 'https://www.tiktok.com/',
                'Range': 'bytes=0-'
            }
            
            async with session.get(download_url, headers=download_headers) as response:
                if response.status in [200, 206]:
                    file_path = os.path.join(temp_dir, f"{filename}.mp4")
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        return file_path
        except Exception as e:
            print(f"Download failed: {e}")
        return None

    async def download_tiktok_video(self, url: str, temp_dir: str) -> Optional[str]:
        """Metodo principale per scaricare video TikTok"""
        try:
            # Prova tutti i metodi in sequenza
            methods = [
                self.method_2_web_scraping,  # Inizia con web scraping (più affidabile)
                self.method_3_third_party_api,
                self.method_1_api_approach,
            ]
            
            for i, method in enumerate(methods, 1):
                print(f"Trying method {i}...")
                
                result = await method(url)
                if result and result.get('success'):
                    print(f"Method {i} successful: {result['method']}")
                    
                    # Pulisci il titolo per il nome file
                    title = result.get('title', 'tiktok_video')
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_title = safe_title[:50] if safe_title else 'tiktok_video'
                    
                    # Scarica il file
                    file_path = await self.download_video_file(
                        result['download_url'], 
                        temp_dir, 
                        safe_title
                    )
                    
                    if file_path:
                        return file_path
                
                # Aspetta un po' prima del prossimo tentativo
                if i < len(methods):
                    await asyncio.sleep(random.uniform(1, 3))
            
            return None
            
        except Exception as e:
            print(f"Download error: {e}")
            return None
        finally:
            await self.close_session()

# Funzione di utilità per l'integrazione
async def download_tiktok_video_improved(url: str, temp_dir: str) -> Optional[str]:
    """Funzione wrapper per il download migliorato"""
    downloader = TikTokDownloader()
    return await downloader.download_tiktok_video(url, temp_dir) 