#!/usr/bin/env python3
"""
Fix the two missing translations that had path length issues
"""

import sqlite3
import json
import requests
import time
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_translation_directly(translation_key, api_base="https://quranenc.com/api/v1"):
    """Download complete translation data directly from API"""
    
    complete_translation = {
        'translation_key': translation_key,
        'suras': {}
    }
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'QuranEnc Database Fixer - Academic Research'
    })
    
    # Download all 114 suras
    for sura_num in range(1, 115):
        try:
            time.sleep(0.1)  # Be respectful to the server
            response = session.get(f"{api_base}/translation/sura/{translation_key}/{sura_num}")
            
            if response.status_code == 200:
                sura_data = response.json()
                complete_translation['suras'][str(sura_num)] = sura_data
                if sura_num % 10 == 0:  # Progress indicator
                    logger.info(f"Downloaded sura {sura_num}/114 for {translation_key}")
            else:
                logger.warning(f"Failed to download sura {sura_num} for {translation_key}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error downloading sura {sura_num} for {translation_key}: {e}")
            continue
    
    return complete_translation

def add_translation_to_database(translation_key, translator, language, translation_data):
    """Add translation directly to database"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert translation record
    cursor.execute("""
        INSERT OR REPLACE INTO translations 
        (key, translator, language, direction, source, total_verses, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        translation_key,
        translator,
        language,
        'ltr',
        'quranenc.com',
        0,  # Will be updated after verse counting
        datetime.now().isoformat()
    ))
    
    logger.info(f"Added translation record: {translation_key} - {translator}")
    
    # Process verses from JSON data
    verse_count = 0
    if 'suras' in translation_data:
        for sura_num_str, sura_data in translation_data['suras'].items():
            try:
                sura_num = int(sura_num_str)
                if 'result' in sura_data and isinstance(sura_data['result'], list):
                    for verse in sura_data['result']:
                        verse_num = verse.get('id', 0)
                        arabic = verse.get('ar', '')
                        translation_text = verse.get('tr', '')
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO verses 
                            (translation_key, sura_number, verse_number, arabic_text, translation_text, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (translation_key, sura_num, verse_num, arabic, translation_text, datetime.now().isoformat()))
                        
                        verse_count += 1
            except (ValueError, TypeError) as e:
                logger.warning(f"Error processing sura {sura_num_str} for {translation_key}: {e}")
                continue
    
    # Update verse count
    cursor.execute("UPDATE translations SET total_verses = ? WHERE key = ?", (verse_count, translation_key))
    logger.info(f"Added {verse_count} verses for {translation_key}")
    
    # Add a file record for the JSON data
    cursor.execute("""
        INSERT OR REPLACE INTO files 
        (translation_key, file_type, file_path, file_size, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        translation_key,
        'json',
        f'direct_download_{translation_key}.json',
        len(json.dumps(translation_data)),
        'downloaded_direct',
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return verse_count

def fix_missing_translations():
    """Fix the two missing translations"""
    
    missing_translations = [
        {
            'key': 'malayalam_kunhi',
            'translator': 'Abdulhamid Haidar Al-Madany & Kunhi Muhammad',
            'language': 'Malayalam'
        },
        {
            'key': 'spanish_montada_latin',
            'translator': 'Noor International (Latin American)',
            'language': 'Spanish'
        }
    ]
    
    total_verses_added = 0
    
    for trans_info in missing_translations:
        logger.info(f"Processing missing translation: {trans_info['key']}")
        
        try:
            # Download translation data
            translation_data = download_translation_directly(trans_info['key'])
            
            # Add to database
            verse_count = add_translation_to_database(
                trans_info['key'],
                trans_info['translator'],
                trans_info['language'],
                translation_data
            )
            
            total_verses_added += verse_count
            logger.info(f"Successfully added {trans_info['key']} with {verse_count} verses")
            
        except Exception as e:
            logger.error(f"Error processing {trans_info['key']}: {e}")
    
    logger.info(f"Fix completed. Total verses added: {total_verses_added}")

if __name__ == "__main__":
    fix_missing_translations()