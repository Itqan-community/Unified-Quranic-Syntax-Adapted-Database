import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

def fix_quranenc_database():
    """Fix and populate SQLite database for QuranEnc.com scraped data"""
    
    # Database path
    db_path = Path("quranenc-com/quranenc.db")
    
    # Remove old database and create fresh one
    if db_path.exists():
        os.remove(db_path)
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            translator TEXT,
            language TEXT,
            direction TEXT,
            source TEXT,
            file_path TEXT,
            total_verses INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE verses (
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
        CREATE TABLE files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            translation_key TEXT,
            file_type TEXT,
            file_path TEXT,
            file_size INTEGER,
            status TEXT DEFAULT 'downloaded',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (translation_key) REFERENCES translations (key)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Find all JSON translation files
    translations_dir = Path("quranenc-com/translations")
    total_files = 0
    total_verses = 0
    total_translations = 0
    
    if translations_dir.exists():
        for trans_dir in translations_dir.iterdir():
            if trans_dir.is_dir():
                # Look for JSON files in each translation directory
                json_files = list(trans_dir.glob("*.json"))
                for json_file in json_files:
                    total_files += 1
                    
                    # Extract translation key from directory name
                    trans_key = trans_dir.name.split('_', 2)[0] + '_' + trans_dir.name.split('_', 2)[1]
                    
                    # Get file info
                    file_size = json_file.stat().st_size if json_file.exists() else 0
                    
                    try:
                        # Load and parse JSON data
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Extract metadata from directory name
                        dir_parts = trans_dir.name.split('_')
                        if len(dir_parts) >= 3:
                            language = dir_parts[0]
                            translator = dir_parts[1]
                            full_name = '_'.join(dir_parts[2:])
                        else:
                            language = "unknown"
                            translator = "unknown" 
                            full_name = trans_dir.name
                        
                        verses_count = 0
                        
                        # Insert translation record
                        cursor.execute("""
                            INSERT OR REPLACE INTO translations 
                            (key, translator, language, source, file_path, total_verses)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            trans_key,
                            translator,
                            language,
                            full_name,
                            str(json_file),
                            0  # Will update after processing verses
                        ))
                        
                        # Insert file record
                        cursor.execute("""
                            INSERT INTO files 
                            (translation_key, file_type, file_path, file_size)
                            VALUES (?, ?, ?, ?)
                        """, (trans_key, 'JSON', str(json_file), file_size))
                        
                        # Process verses - handle the actual JSON structure
                        if isinstance(data, dict) and 'suras' in data:
                            for sura_id, sura_data in data['suras'].items():
                                if 'result' in sura_data and isinstance(sura_data['result'], list):
                                    for verse in sura_data['result']:
                                        if isinstance(verse, dict):
                                            sura_num = int(verse.get('sura', 0))
                                            verse_num = int(verse.get('aya', 0))
                                            arabic = verse.get('arabic_text', '')
                                            translation = verse.get('translation', '')
                                            
                                            cursor.execute("""
                                                INSERT INTO verses 
                                                (translation_key, sura_number, verse_number, arabic_text, translation_text)
                                                VALUES (?, ?, ?, ?, ?)
                                            """, (trans_key, sura_num, verse_num, arabic, translation))
                                            
                                            verses_count += 1
                                            total_verses += 1
                        
                        # Update translation with verse count
                        cursor.execute("""
                            UPDATE translations SET total_verses = ? WHERE key = ?
                        """, (verses_count, trans_key))
                        
                        total_translations += 1
                        print(f"Processed {trans_key}: {verses_count} verses")
                    
                    except Exception as e:
                        print(f"Error processing {json_file}: {str(e)}")
                        continue
    
    # Insert summary metadata
    cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                  ('total_translations', str(total_translations), 'statistics'))
    cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                  ('total_files', str(total_files), 'statistics'))
    cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                  ('total_verses', str(total_verses), 'statistics'))
    cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                  ('database_created', datetime.now().isoformat(), 'info'))
    cursor.execute("INSERT INTO metadata (key, value, category) VALUES (?, ?, ?)", 
                  ('source', 'quranenc.com', 'info'))
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX idx_verses_translation ON verses(translation_key)")
    cursor.execute("CREATE INDEX idx_verses_sura ON verses(sura_number)")
    cursor.execute("CREATE INDEX idx_verses_verse ON verses(verse_number)")
    cursor.execute("CREATE INDEX idx_files_translation ON files(translation_key)")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n=== Database Statistics ===")
    print(f"Total translations: {total_translations}")
    print(f"Total files: {total_files}")
    print(f"Total verses: {total_verses}")
    print(f"Database created at: {db_path}")
    
    return db_path

if __name__ == "__main__":
    fix_quranenc_database()