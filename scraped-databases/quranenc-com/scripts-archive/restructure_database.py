#!/usr/bin/env python3
"""
Restructure QuranEnc database:
1. Remove verses table
2. Update files table structure and relationships
3. Update metadata table
4. Create proper one-to-many relationship between translations and files
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_database():
    """Create a backup of the current database"""
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    backup_path = base_dir / f"quranenc_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    # Copy database file
    import shutil
    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backup created: {backup_path}")
    return backup_path

def restructure_database():
    """Perform database restructuring"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    
    # Create backup first
    backup_path = backup_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Temporarily disable foreign key constraints for restructuring
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    logger.info("Starting database restructuring...")
    
    # STEP 1: Get current statistics before changes
    cursor.execute("SELECT COUNT(*) FROM verses")
    verse_count = cursor.fetchone()[0]
    logger.info(f"Verses table contains {verse_count:,} rows - will be removed")
    
    cursor.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    logger.info(f"Files table contains {file_count} rows")
    
    # STEP 2: Remove verses table
    logger.info("Dropping verses table...")
    cursor.execute("DROP TABLE IF EXISTS verses")
    
    # STEP 3: Update translations table (remove file_path and total_verses columns)
    logger.info("Updating translations table structure...")
    
    # Create new translations table
    cursor.execute("""
        CREATE TABLE translations_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            translator TEXT,
            language TEXT,
            direction TEXT DEFAULT 'ltr',
            source TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Copy data from old table (excluding file_path and total_verses)
    cursor.execute("""
        INSERT INTO translations_new (id, key, translator, language, direction, source, description, created_at)
        SELECT id, key, translator, language, direction, source, source as description, created_at
        FROM translations
    """)
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE translations")
    cursor.execute("ALTER TABLE translations_new RENAME TO translations")
    
    # STEP 4: Update files table structure
    logger.info("Updating files table structure...")
    
    # Create new files table with better structure
    cursor.execute("""
        CREATE TABLE files_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            translation_key TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_format TEXT,
            file_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            download_url TEXT,
            status TEXT DEFAULT 'available',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (translation_key) REFERENCES translations (key) ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)
    
    # Copy and enhance data from old files table
    cursor.execute("""
        INSERT INTO files_new (id, translation_key, file_type, file_format, file_path, file_size, status, created_at)
        SELECT id, translation_key, 
               CASE 
                   WHEN file_type = 'json' THEN 'translation_data'
                   WHEN file_type = 'pdf' THEN 'document'
                   WHEN file_type = 'xml' THEN 'structured_data'
                   WHEN file_type = 'csv' THEN 'structured_data'
                   WHEN file_type = 'xlsx' THEN 'structured_data'
                   WHEN file_type = 'epub' THEN 'document'
                   ELSE 'other'
               END as file_type,
               file_type as file_format,
               file_path, file_size, 
               COALESCE(status, 'available'),
               created_at
        FROM files
    """)
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE files")
    cursor.execute("ALTER TABLE files_new RENAME TO files")
    
    # STEP 5: Update metadata table
    logger.info("Updating metadata table...")
    
    # Remove old verse-related metadata
    cursor.execute("DELETE FROM metadata WHERE key LIKE '%verse%' OR key LIKE '%total_verses%'")
    
    # Add new metadata about the restructuring
    restructure_metadata = [
        ('database_version', '2.0', 'system'),
        ('last_restructure', datetime.now().isoformat(), 'system'),
        ('verses_table_removed', 'true', 'structure'),
        ('relationship_type', 'one_to_many_translations_files', 'structure'),
        ('total_translations', '68', 'statistics'),
        ('total_files', str(file_count), 'statistics')
    ]
    
    for key, value, category in restructure_metadata:
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, category, created_at)
            VALUES (?, ?, ?, ?)
        """, (key, value, category, datetime.now().isoformat()))
    
    # STEP 6: Create indexes for better performance
    logger.info("Creating performance indexes...")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_translation_key ON files(translation_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_category ON metadata(category)")
    
    # STEP 7: Update file descriptions based on file types
    logger.info("Adding file descriptions...")
    
    file_descriptions = {
        'json': 'Complete translation data in JSON format',
        'pdf': 'Formatted document for reading',
        'xml': 'Structured translation data',
        'csv': 'Tabular translation data',
        'xlsx': 'Excel spreadsheet format',
        'epub': 'Electronic book format'
    }
    
    for file_format, description in file_descriptions.items():
        cursor.execute("""
            UPDATE files 
            SET description = ? 
            WHERE file_format = ? AND description IS NULL
        """, (description, file_format))
    
    # Re-enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Commit all changes
    conn.commit()
    
    # STEP 8: Verify the new structure
    logger.info("Verifying new database structure...")
    
    # Check foreign key integrity
    cursor.execute("PRAGMA foreign_key_check")
    fk_violations = cursor.fetchall()
    
    if fk_violations:
        logger.error(f"Foreign key violations found: {fk_violations}")
    else:
        logger.info("✓ Foreign key integrity verified")
    
    # Get final statistics
    cursor.execute("SELECT COUNT(*) FROM translations")
    final_translations = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM files")
    final_files = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM metadata")
    final_metadata = cursor.fetchone()[0]
    
    # Check relationship integrity
    cursor.execute("""
        SELECT t.key, COUNT(f.id) as file_count
        FROM translations t
        LEFT JOIN files f ON t.key = f.translation_key
        GROUP BY t.key
        HAVING file_count = 0
    """)
    translations_without_files = cursor.fetchall()
    
    conn.close()
    
    # Report results
    logger.info("="*60)
    logger.info("DATABASE RESTRUCTURING COMPLETED")
    logger.info("="*60)
    logger.info("Changes made:")
    logger.info(f"  ✓ Removed verses table ({verse_count:,} rows)")
    logger.info("  ✓ Updated translations table structure")
    logger.info("  ✓ Enhanced files table with better categorization")
    logger.info("  ✓ Updated metadata table")
    logger.info("  ✓ Created proper one-to-many relationship")
    logger.info("  ✓ Added performance indexes")
    
    logger.info(f"\nFinal statistics:")
    logger.info(f"  Translations: {final_translations}")
    logger.info(f"  Files: {final_files}")
    logger.info(f"  Metadata entries: {final_metadata}")
    
    if translations_without_files:
        logger.warning(f"  Translations without files: {len(translations_without_files)}")
        for trans_key, file_count in translations_without_files:
            logger.warning(f"    - {trans_key}")
    else:
        logger.info("  ✓ All translations have associated files")
    
    logger.info(f"\nBackup saved to: {backup_path}")
    logger.info("Database restructuring successful!")

if __name__ == "__main__":
    restructure_database()