#!/usr/bin/env python3
"""
Fix database inconsistencies for newly added translations
"""

import sqlite3
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_database_inconsistencies():
    """Fix inconsistencies in the newly added translation records"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all translations that need fixing (those with generic source)
    cursor.execute("""
        SELECT key, translator, language, file_path 
        FROM translations 
        WHERE source = 'quranenc.com'
        ORDER BY key
    """)
    
    translations_to_fix = cursor.fetchall()
    logger.info(f"Found {len(translations_to_fix)} translations to fix")
    
    fixes_applied = 0
    
    for key, translator, language, current_file_path in translations_to_fix:
        logger.info(f"Fixing: {key}")
        
        # Create proper source name (matching the pattern of original translations)
        # Format: "Language_translation_Translator_Name" (with spaces replaced by underscores)
        source_name = f"{language}_translation_{translator.replace(' ', '_').replace('-', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')}"
        
        # Fix file path
        translations_dir = base_dir / "translations"
        
        # Find the actual directory for this translation
        actual_dir = None
        for dir_path in translations_dir.iterdir():
            if dir_path.is_dir() and dir_path.name.startswith(key + '_'):
                actual_dir = dir_path
                break
        
        if actual_dir:
            # Look for JSON file
            json_files = list(actual_dir.glob("quranenc_*_complete_translation.json"))
            if json_files:
                # Use the found JSON file path
                json_file = json_files[0]
                correct_file_path = f"quranenc-com\\{json_file.relative_to(base_dir)}"
            else:
                # No JSON file found, but directory exists
                correct_file_path = f"quranenc-com\\translations\\{actual_dir.name}\\quranenc_{key}_complete_translation.json"
        else:
            # Directory not found, use expected path
            expected_dir_name = f"{key}_{language}_translation_{translator.replace(' ', '_')}"
            correct_file_path = f"quranenc-com\\translations\\{expected_dir_name}\\quranenc_{key}_complete_translation.json"
        
        # Handle special cases for direct downloads
        if key in ['malayalam_kunhi', 'spanish_montada_latin']:
            correct_file_path = f"quranenc-com\\direct_download_{key}.json"
        
        # Update the database record
        cursor.execute("""
            UPDATE translations 
            SET source = ?, file_path = ?
            WHERE key = ?
        """, (source_name, correct_file_path, key))
        
        fixes_applied += 1
        logger.info(f"Fixed {key}:")
        logger.info(f"  Source: {source_name}")
        logger.info(f"  Path: {correct_file_path}")
    
    # Also fix the files table to have consistent paths
    cursor.execute("""
        SELECT translation_key, file_path 
        FROM files 
        WHERE file_path NOT LIKE 'quranenc-com%'
        AND file_path != 'direct_download_%'
    """)
    
    files_to_fix = cursor.fetchall()
    logger.info(f"Found {len(files_to_fix)} file records to fix")
    
    for trans_key, current_path in files_to_fix:
        if not current_path.startswith('quranenc-com'):
            correct_path = f"quranenc-com\\{current_path}"
            cursor.execute("""
                UPDATE files 
                SET file_path = ?
                WHERE translation_key = ? AND file_path = ?
            """, (correct_path, trans_key, current_path))
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    logger.info(f"Database fixes completed:")
    logger.info(f"  Translation records fixed: {fixes_applied}")
    logger.info(f"  File path records fixed: {len(files_to_fix)}")
    
    return fixes_applied

def verify_consistency():
    """Verify that the database is now consistent"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for any remaining inconsistencies
    cursor.execute("SELECT COUNT(*) FROM translations WHERE source = 'quranenc.com'")
    remaining_generic_sources = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM translations WHERE file_path IS NULL OR file_path = 'None'")
    null_paths = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM files WHERE file_path NOT LIKE 'quranenc-com%' AND file_path NOT LIKE 'direct_download_%'")
    inconsistent_file_paths = cursor.fetchone()[0]
    
    conn.close()
    
    logger.info("Consistency check results:")
    logger.info(f"  Translations with generic source: {remaining_generic_sources}")
    logger.info(f"  Translations with null/None paths: {null_paths}")
    logger.info(f"  Files with inconsistent paths: {inconsistent_file_paths}")
    
    if remaining_generic_sources == 0 and null_paths == 0 and inconsistent_file_paths == 0:
        logger.info("✓ Database is now consistent!")
        return True
    else:
        logger.warning("⚠ Some inconsistencies remain")
        return False

if __name__ == "__main__":
    logger.info("Starting database consistency fixes...")
    fix_database_inconsistencies()
    logger.info("Verifying consistency...")
    verify_consistency()