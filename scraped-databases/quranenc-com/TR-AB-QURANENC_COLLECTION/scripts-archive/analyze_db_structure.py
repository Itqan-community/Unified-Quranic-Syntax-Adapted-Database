#!/usr/bin/env python3
"""
Analyze current database structure before restructuring
"""

import sqlite3
from pathlib import Path

def analyze_database_structure():
    """Analyze current database structure and relationships"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    print("="*60)
    print("CURRENT DATABASE STRUCTURE ANALYSIS")
    print("="*60)
    print(f"Tables found: {tables}")
    
    # Analyze each table
    for table in tables:
        print(f"\n{table.upper()} TABLE:")
        print("-" * 40)
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
            flags = []
            if pk: flags.append("PRIMARY KEY")
            if not_null: flags.append("NOT NULL")
            flags_str = " | " + " | ".join(flags) if flags else ""
            print(f"  {col_name:<20} {col_type:<15}{flags_str}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count:,}")
        
        # Check for foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fkeys = cursor.fetchall()
        if fkeys:
            print("  Foreign Keys:")
            for fk in fkeys:
                print(f"    {fk[3]} -> {fk[2]}.{fk[4]}")
    
    # Check current relationships
    print(f"\n{'='*60}")
    print("RELATIONSHIP ANALYSIS")
    print("="*60)
    
    # Check files table relationships
    cursor.execute("SELECT COUNT(DISTINCT translation_key) FROM files")
    unique_translations_in_files = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM translations")
    total_translations = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM files")
    total_files = cursor.fetchone()[0]
    
    print(f"Total translations: {total_translations}")
    print(f"Unique translations in files table: {unique_translations_in_files}")
    print(f"Total files: {total_files}")
    print(f"Average files per translation: {total_files/total_translations:.2f}")
    
    # Sample files per translation
    cursor.execute("""
        SELECT translation_key, COUNT(*) as file_count 
        FROM files 
        GROUP BY translation_key 
        ORDER BY file_count DESC 
        LIMIT 5
    """)
    top_file_counts = cursor.fetchall()
    
    print(f"\nTop translations by file count:")
    for trans_key, file_count in top_file_counts:
        print(f"  {trans_key}: {file_count} files")
    
    # Check verses table size
    cursor.execute("SELECT COUNT(*) FROM verses")
    verse_count = cursor.fetchone()[0]
    print(f"\nVerses table: {verse_count:,} rows")
    
    # Calculate database size info
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]
    print(f"Database size: {db_size/1024/1024:.2f} MB")
    
    conn.close()
    return tables

if __name__ == "__main__":
    analyze_database_structure()