#!/usr/bin/env python3
"""
Extract schema from stable backup and recreate database with proper CRUD operations
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuranEncDatabase:
    """CRUD-based database manager for QuranEnc"""
    
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def create_schema(self):
        """Create the proper database schema"""
        logger.info("Creating database schema...")
        
        # TRANSLATIONS table (without verses-related columns)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                translator TEXT NOT NULL,
                language TEXT NOT NULL,
                direction TEXT DEFAULT 'ltr',
                source TEXT NOT NULL,
                description TEXT,
                website_url TEXT DEFAULT 'https://quranenc.com',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # FILES table with proper relationship
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
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
                    REFERENCES translations (key) 
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # METADATA table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_translation_key ON files(translation_key)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_category ON metadata(category)")
        
        self.conn.commit()
        logger.info("Schema created successfully")
    
    def insert_translation(self, key, translator, language, direction, source, description=None, website_url=None):
        """Insert a translation record"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO translations 
            (key, translator, language, direction, source, description, website_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (key, translator, language, direction, source, description, website_url, datetime.now().isoformat()))
        return self.cursor.lastrowid
    
    def insert_file(self, translation_key, file_type, file_format, file_path, file_size=0, 
                   download_url=None, status='available', description=None):
        """Insert a file record"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO files 
            (translation_key, file_type, file_format, file_path, file_size, download_url, status, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (translation_key, file_type, file_format, file_path, file_size, download_url, status, description, datetime.now().isoformat()))
        return self.cursor.lastrowid
    
    def insert_metadata(self, key, value, category='general'):
        """Insert or update metadata"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO metadata 
            (key, value, category, updated_at)
            VALUES (?, ?, ?, ?)
        """, (key, value, category, datetime.now().isoformat()))
        return self.cursor.lastrowid
    
    def get_translation_count(self):
        """Get total number of translations"""
        self.cursor.execute("SELECT COUNT(*) FROM translations")
        return self.cursor.fetchone()[0]
    
    def get_file_count(self):
        """Get total number of files"""
        self.cursor.execute("SELECT COUNT(*) FROM files")
        return self.cursor.fetchone()[0]

def extract_and_migrate_data():
    """Extract data from stable backup and recreate database properly"""
    
    base_dir = Path(__file__).parent
    stable_backup = base_dir / "quranenc_backup_20250901_104852.db"
    current_db = base_dir / "quranenc.db"
    
    logger.info(f"Extracting data from stable backup: {stable_backup}")
    
    # Connect to stable backup
    backup_conn = sqlite3.connect(stable_backup)
    backup_cursor = backup_conn.cursor()
    
    # Extract all data
    backup_cursor.execute("SELECT * FROM translations ORDER BY id")
    translations_data = backup_cursor.fetchall()
    
    backup_cursor.execute("SELECT * FROM files ORDER BY id")  
    files_data = backup_cursor.fetchall()
    
    backup_cursor.execute("SELECT * FROM metadata ORDER BY id")
    metadata_data = backup_cursor.fetchall()
    
    # Get column names for reference
    backup_cursor.execute("PRAGMA table_info(translations)")
    trans_columns = [col[1] for col in backup_cursor.fetchall()]
    
    backup_cursor.execute("PRAGMA table_info(files)")
    files_columns = [col[1] for col in backup_cursor.fetchall()]
    
    backup_cursor.execute("PRAGMA table_info(metadata)")
    metadata_columns = [col[1] for col in backup_cursor.fetchall()]
    
    backup_conn.close()
    
    logger.info(f"Extracted {len(translations_data)} translations, {len(files_data)} files, {len(metadata_data)} metadata entries")
    
    # Create backup of current corrupted database and create new one
    if current_db.exists():
        corrupted_backup = base_dir / f"quranenc_corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(current_db, corrupted_backup)
        logger.info(f"Corrupted database backed up to: {corrupted_backup}")
        
        # Create new database with different name first
        new_db = base_dir / f"quranenc_new_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    else:
        new_db = current_db
    
    # Create new database with proper CRUD operations
    logger.info("Creating new database with proper schema...")
    db = QuranEncDatabase(new_db)
    db.connect()
    db.create_schema()
    
    # Migrate translations data
    logger.info("Migrating translations data...")
    for i, row in enumerate(translations_data):
        # Map old columns to new schema (excluding file_path and total_verses)
        row_dict = dict(zip(trans_columns, row))
        
        # Create description from translator and language
        description = f"Translation by {row_dict['translator']} in {row_dict['language']}"
        
        db.insert_translation(
            key=row_dict['key'],
            translator=row_dict['translator'],
            language=row_dict['language'],
            direction=row_dict.get('direction', 'ltr'),
            source=row_dict['source'],
            description=description,
            website_url='https://quranenc.com'
        )
        
        if (i + 1) % 10 == 0:
            logger.info(f"Migrated {i + 1}/{len(translations_data)} translations")
    
    # Migrate files data with better categorization
    logger.info("Migrating files data...")
    for i, row in enumerate(files_data):
        row_dict = dict(zip(files_columns, row))
        
        # Categorize file types properly
        file_format = row_dict.get('file_type', 'unknown')
        
        if file_format == 'json':
            file_type = 'translation_data'
            description = 'Complete translation data in JSON format'
        elif file_format == 'pdf':
            file_type = 'document'
            description = 'Formatted PDF document for reading'
        elif file_format in ['xml', 'csv', 'xlsx', 'excel']:
            file_type = 'structured_data'
            description = f'Structured data in {file_format.upper()} format'
        elif file_format == 'epub':
            file_type = 'document'
            description = 'Electronic book format'
        else:
            file_type = 'other'
            description = f'File in {file_format} format'
        
        db.insert_file(
            translation_key=row_dict['translation_key'],
            file_type=file_type,
            file_format=file_format,
            file_path=row_dict['file_path'],
            file_size=row_dict.get('file_size', 0),
            download_url=row_dict.get('download_url'),
            status=row_dict.get('status', 'available'),
            description=description
        )
        
        if (i + 1) % 20 == 0:
            logger.info(f"Migrated {i + 1}/{len(files_data)} files")
    
    # Migrate metadata (filtering out duplicates and unwanted entries)
    logger.info("Migrating metadata...")
    processed_keys = set()
    
    for row in metadata_data:
        row_dict = dict(zip(metadata_columns, row))
        key = row_dict['key']
        
        # Skip duplicates and verses-related metadata
        if key in processed_keys or 'verse' in key.lower():
            continue
            
        processed_keys.add(key)
        
        db.insert_metadata(
            key=key,
            value=row_dict['value'],
            category=row_dict.get('category', 'general')
        )
    
    # Add new metadata about the recreation
    db.insert_metadata('database_version', '2.0', 'system')
    db.insert_metadata('recreated_at', datetime.now().isoformat(), 'system')
    db.insert_metadata('verses_table_removed', 'true', 'structure')
    db.insert_metadata('crud_based', 'true', 'structure')
    db.insert_metadata('total_translations', str(db.get_translation_count()), 'statistics')
    db.insert_metadata('total_files', str(db.get_file_count()), 'statistics')
    
    # Commit all changes
    db.conn.commit()
    
    # Final verification
    final_translations = db.get_translation_count()
    final_files = db.get_file_count()
    
    db.disconnect()
    
    # If we created a new database with a different name, now replace the old one
    if new_db != current_db:
        import time
        time.sleep(1)  # Give any processes time to release the file
        try:
            if current_db.exists():
                current_db.unlink()
            new_db.rename(current_db)
            logger.info(f"New database moved to: {current_db}")
        except Exception as e:
            logger.warning(f"Could not replace old database: {e}")
            logger.info(f"New database available at: {new_db}")
    
    logger.info("="*70)
    logger.info("DATABASE RECREATION COMPLETED SUCCESSFULLY")
    logger.info("="*70)
    logger.info("Migration results:")
    logger.info(f"  Translations: {len(translations_data)} -> {final_translations}")
    logger.info(f"  Files: {len(files_data)} -> {final_files}")
    logger.info(f"  Metadata: {len(metadata_data)} -> {len(processed_keys) + 6} (duplicates removed)")
    logger.info("")
    logger.info("Database features:")
    logger.info("  ✓ CRUD-based operations")
    logger.info("  ✓ Proper foreign key constraints")
    logger.info("  ✓ No duplicate metadata entries")
    logger.info("  ✓ Verses table removed")
    logger.info("  ✓ Enhanced file categorization")
    logger.info("  ✓ Schema-driven design")
    
    final_db_path = current_db if new_db == current_db or not new_db.exists() else new_db
    logger.info(f"\nFinal database location: {final_db_path}")

if __name__ == "__main__":
    extract_and_migrate_data()