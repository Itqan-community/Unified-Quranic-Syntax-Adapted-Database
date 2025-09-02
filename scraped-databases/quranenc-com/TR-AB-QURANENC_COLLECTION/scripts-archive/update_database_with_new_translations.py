#!/usr/bin/env python3
"""
Update QuranEnc database with newly scraped translations
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_database_with_translations():
    """Update the QuranEnc database with newly scraped translations"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    translations_dir = base_dir / "translations"
    
    if not translations_dir.exists():
        logger.error(f"Translations directory not found: {translations_dir}")
        return
        
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing translations to avoid duplicates
    cursor.execute("SELECT key FROM translations")
    existing_translations = set(row[0] for row in cursor.fetchall())
    
    new_translations = 0
    new_verses = 0
    new_files = 0
    
    # Process each translation directory
    for trans_dir in translations_dir.iterdir():
        if not trans_dir.is_dir():
            continue
            
        # Extract translation key from directory name
        dir_name = trans_dir.name
        translation_key = dir_name.split('_')[0] + '_' + dir_name.split('_')[1]
        
        # Skip if already in database
        if translation_key in existing_translations:
            logger.debug(f"Translation {translation_key} already in database, skipping")
            continue
            
        logger.info(f"Processing new translation: {translation_key}")
        
        # Find the JSON file with complete translation data
        json_files = list(trans_dir.glob("quranenc_*_complete_translation.json"))
        if not json_files:
            logger.warning(f"No complete translation JSON found for {translation_key}")
            continue
            
        json_file = json_files[0]
        
        try:
            # Load translation data
            with open(json_file, 'r', encoding='utf-8') as f:
                translation_data = json.load(f)
            
            # Extract translator and language from directory name
            title_parts = dir_name.split('_')[2:]  # Skip key parts
            translator = "Unknown"
            language = translation_key.split('_')[0].title()
            
            # Try to extract translator name from title
            title = '_'.join(title_parts).replace('_', ' ')
            if 'translation' in title.lower():
                title_words = title.split()
                try:
                    trans_idx = next(i for i, word in enumerate(title_words) if 'translation' in word.lower())
                    if trans_idx < len(title_words) - 1:
                        translator = ' '.join(title_words[trans_idx + 1:])
                except StopIteration:
                    pass
            
            # Insert translation record
            cursor.execute("""
                INSERT OR REPLACE INTO translations 
                (key, translator, language, direction, source, file_path, total_verses, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                translation_key,
                translator.strip(),
                language,
                'ltr',  # Default direction
                'quranenc.com',
                str(json_file.relative_to(base_dir)),
                0,  # Will be updated after verse counting
                datetime.now().isoformat()
            ))
            
            new_translations += 1
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
            new_verses += verse_count
            logger.info(f"Added {verse_count} verses for {translation_key}")
            
            # Process downloaded files
            file_count = 0
            for file_path in trans_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    file_type = file_path.suffix.lower().lstrip('.')
                    if not file_type:
                        file_type = 'unknown'
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO files 
                        (translation_key, file_type, file_path, file_size, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        translation_key,
                        file_type,
                        str(file_path.relative_to(base_dir)),
                        file_path.stat().st_size,
                        'downloaded',
                        datetime.now().isoformat()
                    ))
                    file_count += 1
            
            new_files += file_count
            logger.info(f"Added {file_count} file records for {translation_key}")
            
        except Exception as e:
            logger.error(f"Error processing {translation_key}: {e}")
            continue
    
    # Update metadata
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value, category, created_at)
        VALUES (?, ?, ?, ?)
    """, ('last_update', datetime.now().isoformat(), 'system', datetime.now().isoformat()))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    logger.info(f"Database update completed:")
    logger.info(f"  New translations added: {new_translations}")
    logger.info(f"  New verses added: {new_verses}")
    logger.info(f"  New file records added: {new_files}")
    
    return new_translations, new_verses, new_files

if __name__ == "__main__":
    update_database_with_translations()