#!/usr/bin/env python3
"""
Download specific missing translations from QuranEnc.com
"""

import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path
from quranenc_scraper import QuranEncScraper

def get_missing_translation_keys():
    """List of missing translation keys to download"""
    return [
        'spanish_montada_latin',
        'urdu_junagarhi', 
        'hindi_omari',
        'telugu_muhammad',
        'gujarati_omari',
        'malayalam_kunhi',
        'kannada_hamza',
        'assamese_rafeeq',
        'punjabi_arif',
        'tamil_omar',
        'tamil_baqavi', 
        'sinhalese_mahir',
        'swahili_rwwad',
        'swahili_barawani',
        'somali_yacob',
        'amharic_zain',
        'amharic_sadiq',
        'yoruba_mikail',
        'hausa_gummi',
        'oromo_ababor',
        'afar_hamza',
        'ankobambara_dayyan',
        'kinyarwanda_assoc',
        'ikirundi_gehiti',
        'moore_rwwad',
        'asante_harun',
        'lingala_zakaria'
    ]

def find_existing_translations(base_dir):
    """Find which translations already exist by checking database"""
    db_path = Path(base_dir) / "quranenc.db"
    if not db_path.exists():
        return set()
    
    import sqlite3
    completed = set()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT key FROM translations')
        results = cursor.fetchall()
        completed = set(row[0] for row in results)
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
        
    return completed

def main():
    base_directory = Path(__file__).parent
    scraper = QuranEncScraper(base_directory)
    
    # Get all available translations
    all_translations = scraper.get_translations_list()
    print(f"Total translations available from API: {len(all_translations)}")
    
    # Get keys we want to download
    target_keys = get_missing_translation_keys()
    print(f"Target missing translations: {len(target_keys)}")
    
    # Find what we already have
    existing = find_existing_translations(base_directory)
    print(f"Already downloaded: {len(existing)}")
    print("Existing translations:")
    for ex in sorted(existing):
        print(f"  [OK] {ex}")
    
    # Filter to translations we need to download
    translations_to_download = []
    for translation in all_translations:
        key = translation.get('key', '')
        if key in target_keys:
            if key not in existing:
                translations_to_download.append(translation)
                print(f"  [MISSING] WILL DOWNLOAD: {key}")
            else:
                print(f"  [HAVE] ALREADY EXISTS: {key}")
                
    if not translations_to_download:
        print("\nAll target translations are already downloaded!")
        return
        
    print(f"\nDownloading {len(translations_to_download)} missing translations...")
    
    # Download each missing translation
    for i, translation in enumerate(translations_to_download, 1):
        key = translation.get('key', 'unknown')
        title = translation.get('title', 'unknown')
        print(f"\n[{i}/{len(translations_to_download)}] Downloading: {key}")
        print(f"    Title: {title}")
        
        try:
            translation_metadata = scraper.download_translation_data(translation)
            print(f"    [OK] Successfully downloaded {key}")
            
            # Small delay to be respectful
            time.sleep(1)
            
        except Exception as e:
            print(f"    [ERROR] Error downloading {key}: {e}")
    
    print(f"\nDownload completed!")

if __name__ == "__main__":
    main()