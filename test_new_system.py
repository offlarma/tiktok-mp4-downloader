#!/usr/bin/env python3
"""
Script di test per il nuovo sistema di download TikTok
"""

import asyncio
import tempfile
import os
from improved_downloader import download_tiktok_video_improved

async def test_download():
    """Test del nuovo sistema di download"""
    
    # URL di test (sostituisci con un URL TikTok valido)
    test_urls = [
        "https://www.tiktok.com/@tiktok/video/7016451725845712133",
        "https://vm.tiktok.com/ZMhgqjSgf/",  # Esempio di URL corto
    ]
    
    print("🧪 Test del Nuovo Sistema di Download TikTok")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📹 Test {i}: {url}")
        print("-" * 30)
        
        # Crea directory temporanea
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Prova il download
            result = await download_tiktok_video_improved(url, temp_dir)
            
            if result and os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"✅ Download riuscito!")
                print(f"📁 File: {result}")
                print(f"📊 Dimensione: {file_size / (1024*1024):.2f} MB")
                
                # Pulisci il file di test
                os.remove(result)
                print("🗑️ File di test rimosso")
            else:
                print("❌ Download fallito")
                
        except Exception as e:
            print(f"❌ Errore durante il test: {e}")
        
        finally:
            # Pulisci directory temporanea
            try:
                os.rmdir(temp_dir)
            except:
                pass

def test_url_extraction():
    """Test dell'estrazione ID video"""
    from improved_downloader import TikTokDownloader
    
    print("\n🔍 Test Estrazione ID Video")
    print("=" * 30)
    
    downloader = TikTokDownloader()
    
    test_urls = [
        "https://www.tiktok.com/@user/video/1234567890",
        "https://vm.tiktok.com/ZMhgqjSgf/",
        "https://vt.tiktok.com/ZSjQKFsP/",
        "https://m.tiktok.com/v/1234567890",
    ]
    
    for url in test_urls:
        video_id = downloader.extract_video_id(url)
        print(f"URL: {url}")
        print(f"ID: {video_id}")
        print()

async def main():
    """Funzione principale di test"""
    print("🚀 Avvio Test Sistema TikTok Downloader v2.0")
    print("=" * 60)
    
    # Test estrazione ID
    test_url_extraction()
    
    # Test download (commentato per evitare download reali durante i test)
    print("\n⚠️ Test download disabilitato per evitare download reali")
    print("Per testare il download, decommentare la riga seguente e fornire URL validi:")
    print("# await test_download()")
    
    print("\n✅ Test completati!")
    print("\n📋 Prossimi passi:")
    print("1. Sostituisci main.py con main_improved.py")
    print("2. Assicurati che improved_downloader.py sia nella stessa cartella")
    print("3. Installa aiohttp: pip install aiohttp==3.9.1")
    print("4. Avvia il server: python main.py")

if __name__ == "__main__":
    asyncio.run(main()) 