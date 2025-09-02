import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

def create_quranenc_database():
    """Create SQLite database for QuranEnc.com scraped data"""
    
    # Database path
    db_path = Path("quranenc-com/quranenc.db")
    metadata_path = Path("quranenc-com/quranenc_comprehensive_metadata.json")
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            translator TEXT,
            language TEXT,
            direction TEXT,
            source TEXT,
            curl_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            translation_key TEXT,
            file_type TEXT,
            file_path TEXT,
            file_size INTEGER,
            download_url TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (translation_key) REFERENCES translations (key)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            translation_key TEXT,
            sura_number INTEGER,
            verse_number INTEGER,
            arabic_text TEXT,
            translation_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (translation_key) REFERENCES translations (key)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Load and insert metadata if exists
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Insert translations
        if 'translations' in metadata:
            for trans_key, trans_data in metadata['translations'].items():
                cursor.execute("""
                    INSERT OR REPLACE INTO translations 
                    (key, translator, language, direction, source, curl_key)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    trans_key,
                    trans_data.get('translator', ''),
                    trans_data.get('language', ''),
                    trans_data.get('direction', ''),
                    trans_data.get('source', ''),
                    trans_data.get('curl_key', '')
                ))
        
        # Insert file information
        if 'files' in metadata:
            for file_info in metadata['files']:
                cursor.execute("""
                    INSERT OR REPLACE INTO files 
                    (translation_key, file_type, file_path, file_size, download_url, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    file_info.get('translation_key', ''),
                    file_info.get('type', ''),
                    file_info.get('path', ''),
                    file_info.get('size', 0),
                    file_info.get('url', ''),
                    file_info.get('status', 'downloaded')
                ))
        
        # Insert general metadata
        cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                      ('total_translations', str(metadata.get('total_translations', 0)), 'statistics'))
        cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                      ('total_files', str(metadata.get('total_files', 0)), 'statistics'))
        cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                      ('total_size', str(metadata.get('total_size_mb', 0)), 'statistics'))
        cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                      ('scrape_date', str(metadata.get('scrape_timestamp', datetime.now().isoformat())), 'info'))
    
    # Load JSON translation files and extract verses
    api_data_dir = Path("quranenc-com/api-data")
    if api_data_dir.exists():
        for json_file in api_data_dir.glob("*.json"):
            translation_key = json_file.stem.replace('quranenc_', '').replace('_complete', '')
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for sura in data:
                        sura_num = sura.get('id', 0)
                        if 'array' in sura:
                            for verse in sura['array']:
                                verse_num = verse.get('id', 0)
                                arabic = verse.get('ar', '')
                                translation = verse.get('tr', '')
                                
                                cursor.execute("""
                                    INSERT OR REPLACE INTO verses 
                                    (translation_key, sura_number, verse_number, arabic_text, translation_text)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (translation_key, sura_num, verse_num, arabic, translation))
            
            except json.JSONDecodeError:
                print(f"Error loading {json_file}")
                continue
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_translation ON verses(translation_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_sura ON verses(sura_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_translation ON files(translation_key)")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"QuranEnc database created successfully at: {db_path}")
    return db_path

if __name__ == "__main__":
    create_quranenc_database()