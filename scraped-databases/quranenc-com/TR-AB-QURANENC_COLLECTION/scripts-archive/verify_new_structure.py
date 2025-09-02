#!/usr/bin/env python3
"""
Verify the new database structure after restructuring
"""

import sqlite3
from pathlib import Path

def verify_new_database_structure():
    """Verify the restructured database"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*70)
    print("NEW DATABASE STRUCTURE VERIFICATION")
    print("="*70)
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    # Verify translations table
    print(f"\n{'TRANSLATIONS TABLE':<50}")
    print("-" * 50)
    cursor.execute("PRAGMA table_info(translations)")
    for col in cursor.fetchall():
        col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
        flags = []
        if pk: flags.append("PK")
        if not_null: flags.append("NOT NULL")
        if default: flags.append(f"DEFAULT {default}")
        flags_str = " | " + " | ".join(flags) if flags else ""
        print(f"  {col_name:<20} {col_type:<15}{flags_str}")
    
    cursor.execute("SELECT COUNT(*) FROM translations")
    print(f"  Rows: {cursor.fetchone()[0]}")
    
    # Sample translations data
    cursor.execute("SELECT key, translator, language, description FROM translations LIMIT 3")
    print("  Sample data:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]} ({row[2]}) - {row[3][:50]}...")
    
    # Verify files table
    print(f"\n{'FILES TABLE':<50}")
    print("-" * 50)
    cursor.execute("PRAGMA table_info(files)")
    for col in cursor.fetchall():
        col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
        flags = []
        if pk: flags.append("PK")
        if not_null: flags.append("NOT NULL")
        if default: flags.append(f"DEFAULT {default}")
        flags_str = " | " + " | ".join(flags) if flags else ""
        print(f"  {col_name:<20} {col_type:<15}{flags_str}")
    
    cursor.execute("SELECT COUNT(*) FROM files")
    print(f"  Rows: {cursor.fetchone()[0]}")
    
    # File type distribution
    cursor.execute("SELECT file_type, COUNT(*) FROM files GROUP BY file_type ORDER BY COUNT(*) DESC")
    print("  File types:")
    for file_type, count in cursor.fetchall():
        print(f"    {file_type}: {count} files")
    
    # File format distribution  
    cursor.execute("SELECT file_format, COUNT(*) FROM files GROUP BY file_format ORDER BY COUNT(*) DESC")
    print("  File formats:")
    for file_format, count in cursor.fetchall():
        print(f"    {file_format}: {count} files")
    
    # Verify foreign key relationship
    print(f"\n{'RELATIONSHIP VERIFICATION':<50}")
    print("-" * 50)
    
    cursor.execute("PRAGMA foreign_key_list(files)")
    fkeys = cursor.fetchall()
    print("Foreign keys in files table:")
    for fk in fkeys:
        print(f"  {fk[3]} -> {fk[2]}.{fk[4]} (ON DELETE {fk[5]}, ON UPDATE {fk[6]})")
    
    # Test relationship integrity
    cursor.execute("""
        SELECT t.key, t.translator, COUNT(f.id) as file_count
        FROM translations t
        LEFT JOIN files f ON t.key = f.translation_key
        GROUP BY t.key, t.translator
        ORDER BY file_count DESC
        LIMIT 10
    """)
    
    print("Translation -> Files relationships (top 10):")
    for key, translator, file_count in cursor.fetchall():
        print(f"  {key}: {translator} -> {file_count} files")
    
    # Check for orphaned files
    cursor.execute("""
        SELECT f.translation_key, COUNT(*) as orphaned_files
        FROM files f
        LEFT JOIN translations t ON f.translation_key = t.key
        WHERE t.key IS NULL
        GROUP BY f.translation_key
    """)
    
    orphaned = cursor.fetchall()
    if orphaned:
        print(f"\n⚠ ORPHANED FILES FOUND:")
        for trans_key, count in orphaned:
            print(f"  {trans_key}: {count} orphaned files")
    else:
        print(f"\n✓ No orphaned files found")
    
    # Check translations without files
    cursor.execute("""
        SELECT t.key, t.translator
        FROM translations t
        LEFT JOIN files f ON t.key = f.translation_key
        WHERE f.translation_key IS NULL
    """)
    
    no_files = cursor.fetchall()
    if no_files:
        print(f"\n⚠ TRANSLATIONS WITHOUT FILES:")
        for key, translator in no_files:
            print(f"  {key}: {translator}")
    else:
        print(f"\n✓ All translations have associated files")
    
    # Verify metadata
    print(f"\n{'METADATA TABLE':<50}")
    print("-" * 50)
    cursor.execute("SELECT key, value, category FROM metadata ORDER BY category, key")
    current_category = ""
    for key, value, category in cursor.fetchall():
        if category != current_category:
            current_category = category
            print(f"\n  {category.upper()}:")
        print(f"    {key}: {value}")
    
    # Database size info
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]
    
    print(f"\n{'DATABASE STATISTICS':<50}")
    print("-" * 50)
    print(f"Database size: {db_size/1024/1024:.2f} MB")
    print(f"Tables: {len(tables)}")
    
    # Performance check - test a join query
    import time
    start_time = time.time()
    cursor.execute("""
        SELECT t.key, t.translator, t.language, 
               GROUP_CONCAT(f.file_format) as formats,
               COUNT(f.id) as file_count
        FROM translations t
        JOIN files f ON t.key = f.translation_key
        GROUP BY t.key, t.translator, t.language
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    query_time = time.time() - start_time
    
    print(f"\nPerformance test (join query): {query_time*1000:.2f}ms")
    print("Sample join results:")
    for row in results:
        print(f"  {row[0]}: {row[1]} ({row[2]}) -> {row[4]} files [{row[3]}]")
    
    conn.close()
    
    print(f"\n{'='*70}")
    print("DATABASE RESTRUCTURING VERIFICATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    verify_new_database_structure()