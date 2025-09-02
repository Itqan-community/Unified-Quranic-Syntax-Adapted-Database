#!/usr/bin/env python3
"""
Safe database restructuring with proper transaction handling
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_restructure_database():
    """Safely restructure the database"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    
    # Create backup
    backup_path = base_dir / f"quranenc_backup_safe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backup created: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Temporarily disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        logger.info("Starting safe database restructuring...")
        
        # STEP 1: Check current state
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        current_tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Current tables: {current_tables}")
        
        verses_exists = 'verses' in current_tables
        if verses_exists:
            cursor.execute("SELECT COUNT(*) FROM verses")
            verse_count = cursor.fetchone()[0]
            logger.info(f"Verses table contains {verse_count:,} rows")
        
        # STEP 2: Create new optimized translations table
        logger.info("Creating new translations table structure...")
        
        cursor.execute("DROP TABLE IF EXISTS translations_new")
        cursor.execute("""
            CREATE TABLE translations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                translator TEXT,
                language TEXT,
                direction TEXT DEFAULT 'ltr',
                source TEXT,
                description TEXT,
                website_url TEXT DEFAULT 'https://quranenc.com',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copy data from old translations table
        cursor.execute("""
            INSERT INTO translations_new (id, key, translator, language, direction, source, description, created_at)
            SELECT id, key, translator, language, direction, source, 
                   'Translation by ' || translator || ' in ' || language as description,
                   created_at
            FROM translations
        """)
        
        # STEP 3: Create new optimized files table
        logger.info("Creating new files table structure...")
        
        cursor.execute("DROP TABLE IF EXISTS files_new")
        cursor.execute("""
            CREATE TABLE files_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                translation_key TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_format TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                download_url TEXT,
                status TEXT DEFAULT 'available',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_files_translation 
                    FOREIGN KEY (translation_key) 
                    REFERENCES translations_new (key) 
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Copy and categorize files data
        cursor.execute("""
            INSERT INTO files_new (
                id, translation_key, file_type, file_format, 
                file_path, file_size, status, description, created_at
            )
            SELECT 
                id, translation_key,
                CASE 
                    WHEN file_type = 'json' THEN 'translation_data'
                    WHEN file_type = 'pdf' THEN 'document'
                    WHEN file_type = 'xml' THEN 'structured_data'
                    WHEN file_type = 'csv' THEN 'structured_data'
                    WHEN file_type = 'xlsx' THEN 'structured_data'
                    WHEN file_type = 'excel' THEN 'structured_data'
                    WHEN file_type = 'epub' THEN 'document'
                    ELSE 'other'
                END as file_type,
                file_type as file_format,
                file_path, 
                COALESCE(file_size, 0),
                COALESCE(status, 'available'),
                CASE 
                    WHEN file_type = 'json' THEN 'Complete translation data in JSON format'
                    WHEN file_type = 'pdf' THEN 'Formatted PDF document for reading'
                    WHEN file_type = 'xml' THEN 'Structured XML data'
                    WHEN file_type = 'csv' THEN 'Tabular CSV data'
                    WHEN file_type = 'xlsx' OR file_type = 'excel' THEN 'Excel spreadsheet format'
                    WHEN file_type = 'epub' THEN 'Electronic book format'
                    ELSE 'Other format file'
                END as description,
                created_at
            FROM files
        """)
        
        # STEP 4: Drop old tables and rename new ones
        logger.info("Replacing old tables with new structures...")
        
        # Drop verses table if it exists
        if verses_exists:
            cursor.execute("DROP TABLE verses")
            logger.info("✓ Verses table removed")
        
        cursor.execute("DROP TABLE translations")
        cursor.execute("DROP TABLE files")
        
        cursor.execute("ALTER TABLE translations_new RENAME TO translations")
        cursor.execute("ALTER TABLE files_new RENAME TO files")
        
        # STEP 5: Update metadata table
        logger.info("Updating metadata...")
        
        # Remove old metadata entries
        cursor.execute("DELETE FROM metadata WHERE key IN ('total_verses', 'verses_count')")
        
        # Add restructuring metadata
        restructure_metadata = [
            ('database_version', '2.0', 'system'),
            ('last_restructure', datetime.now().isoformat(), 'system'),
            ('verses_table_removed', 'true', 'structure'),
            ('relationship_type', 'one_to_many_translations_files', 'structure'),
            ('focus', 'translation_metadata_and_files', 'structure')
        ]
        
        for key, value, category in restructure_metadata:
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value, category, created_at)
                VALUES (?, ?, ?, ?)
            """, (key, value, category, datetime.now().isoformat()))
        
        # Update statistics
        cursor.execute("SELECT COUNT(*) FROM translations")
        trans_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM files") 
        files_count = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, category, created_at)
            VALUES ('total_translations', ?, 'statistics', ?)
        """, (str(trans_count), datetime.now().isoformat()))
        
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, category, created_at)
            VALUES ('total_files', ?, 'statistics', ?)
        """, (str(files_count), datetime.now().isoformat()))
        
        # STEP 6: Create indexes
        logger.info("Creating performance indexes...")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_translator ON translations(translator)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_translation_key ON files(translation_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_format ON files(file_format)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_category ON metadata(category)")
        
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit transaction
        cursor.execute("COMMIT")
        
        # STEP 7: Verify integrity
        logger.info("Verifying database integrity...")
        
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        
        if fk_violations:
            logger.error(f"Foreign key violations: {fk_violations}")
            raise Exception("Database integrity check failed")
        
        # Final statistics
        cursor.execute("SELECT COUNT(*) FROM translations")
        final_translations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM files")
        final_files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM metadata")
        final_metadata = cursor.fetchone()[0]
        
        # Check relationships
        cursor.execute("""
            SELECT t.key, COUNT(f.id) as file_count
            FROM translations t
            LEFT JOIN files f ON t.key = f.translation_key
            GROUP BY t.key
            ORDER BY file_count DESC
            LIMIT 5
        """)
        top_relations = cursor.fetchall()
        
        logger.info("="*60)
        logger.info("DATABASE RESTRUCTURING COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
        changes_made = [
            f"✓ Removed verses table ({verse_count:,} rows)" if verses_exists else "✓ Verses table was already removed",
            "✓ Enhanced translations table with description and website_url fields",
            "✓ Improved files table with better categorization and descriptions", 
            "✓ Updated metadata with restructuring information",
            "✓ Created proper one-to-many relationship (translations -> files)",
            "✓ Added performance indexes"
        ]
        
        for change in changes_made:
            logger.info(f"  {change}")
        
        logger.info(f"\nFinal database structure:")
        logger.info(f"  Translations: {final_translations}")
        logger.info(f"  Files: {final_files}")
        logger.info(f"  Metadata entries: {final_metadata}")
        
        logger.info(f"\nTop translation-file relationships:")
        for trans_key, file_count in top_relations:
            logger.info(f"  {trans_key}: {file_count} files")
        
        logger.info(f"\nBackup saved to: {backup_path}")
        
    except Exception as e:
        logger.error(f"Error during restructuring: {e}")
        cursor.execute("ROLLBACK")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    safe_restructure_database()