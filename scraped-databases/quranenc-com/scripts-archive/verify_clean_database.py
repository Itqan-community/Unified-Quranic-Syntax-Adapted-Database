#!/usr/bin/env python3
"""
Verify the clean, schema-based database
"""

import sqlite3
from pathlib import Path

def verify_clean_database():
    """Verify the newly created clean database"""
    
    base_dir = Path(__file__).parent
    db_path = base_dir / "quranenc_clean.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*80)
    print("CLEAN SCHEMA-BASED DATABASE VERIFICATION")
    print("="*80)
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    # Check translations table
    print(f"\nTRANSLATIONS TABLE:")
    print("-" * 50)
    cursor.execute("PRAGMA table_info(translations)")
    columns = cursor.fetchall()
    for col in columns:
        col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
        flags = []
        if pk: flags.append("PRIMARY KEY")
        if not_null: flags.append("NOT NULL")
        if default: flags.append(f"DEFAULT {default}")
        flags_str = " | " + " | ".join(flags) if flags else ""
        print(f"  {col_name:<20} {col_type:<15}{flags_str}")
    
    cursor.execute("SELECT COUNT(*) FROM translations")
    trans_count = cursor.fetchone()[0]
    print(f"  Rows: {trans_count}")
    
    # Check files table
    print(f"\nFILES TABLE:")
    print("-" * 50)
    cursor.execute("PRAGMA table_info(files)")
    columns = cursor.fetchall()
    for col in columns:
        col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
        flags = []
        if pk: flags.append("PRIMARY KEY")
        if not_null: flags.append("NOT NULL")
        if default: flags.append(f"DEFAULT {default}")
        flags_str = " | " + " | ".join(flags) if flags else ""
        print(f"  {col_name:<20} {col_type:<15}{flags_str}")
    
    cursor.execute("SELECT COUNT(*) FROM files")
    files_count = cursor.fetchone()[0]
    print(f"  Rows: {files_count}")
    
    # Check foreign key relationship
    cursor.execute("PRAGMA foreign_key_list(files)")
    fkeys = cursor.fetchall()
    print("\n  Foreign Keys:")
    for fk in fkeys:
        print(f"    {fk[3]} -> {fk[2]}.{fk[4]} (ON DELETE {fk[5]}, ON UPDATE {fk[6]})")
    
    # Check metadata table
    print(f"\nMETADATA TABLE:")
    print("-" * 50) 
    cursor.execute("PRAGMA table_info(metadata)")
    columns = cursor.fetchall()
    for col in columns:
        col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
        flags = []
        if pk: flags.append("PRIMARY KEY")
        if not_null: flags.append("NOT NULL")
        if default: flags.append(f"DEFAULT {default}")
        flags_str = " | " + " | ".join(flags) if flags else ""
        print(f"  {col_name:<20} {col_type:<15}{flags_str}")
    
    cursor.execute("SELECT COUNT(*) FROM metadata")
    metadata_count = cursor.fetchone()[0]
    print(f"  Rows: {metadata_count}")
    
    # Check for duplicate metadata keys
    cursor.execute("SELECT key, COUNT(*) as count FROM metadata GROUP BY key HAVING count > 1")
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n❌ DUPLICATE METADATA KEYS FOUND:")
        for key, count in duplicates:
            print(f"    {key}: {count} occurrences")
    else:
        print(f"\n✅ NO DUPLICATE METADATA KEYS")
    
    # Show metadata content
    print(f"\nMETADATA CONTENT:")
    cursor.execute("SELECT key, value, category FROM metadata ORDER BY category, key")
    current_category = ""
    for key, value, category in cursor.fetchall():
        if category != current_category:
            current_category = category
            print(f"\n  {category.upper()}:")
        print(f"    {key}: {value}")
    
    # Test relationship integrity
    print(f"\nRELATIONSHIP INTEGRITY:")
    print("-" * 50)
    
    # Check for orphaned files
    cursor.execute("""
        SELECT f.translation_key, COUNT(*) as orphaned_count
        FROM files f
        LEFT JOIN translations t ON f.translation_key = t.key
        WHERE t.key IS NULL
        GROUP BY f.translation_key
    """)
    orphaned = cursor.fetchall()
    
    if orphaned:
        print(f"❌ ORPHANED FILES:")
        for trans_key, count in orphaned:
            print(f"    {trans_key}: {count} orphaned files")
    else:
        print(f"✅ No orphaned files")
    
    # Check translations without files
    cursor.execute("""
        SELECT t.key, t.translator
        FROM translations t
        LEFT JOIN files f ON t.key = f.translation_key
        WHERE f.translation_key IS NULL
    """)
    no_files = cursor.fetchall()
    
    if no_files:
        print(f"❌ TRANSLATIONS WITHOUT FILES:")
        for key, translator in no_files:
            print(f"    {key}: {translator}")
    else:
        print(f"✅ All translations have files")
    
    # File type distribution
    print(f"\nFILE CATEGORIZATION:")
    print("-" * 50)
    cursor.execute("SELECT file_type, COUNT(*) FROM files GROUP BY file_type ORDER BY COUNT(*) DESC")
    for file_type, count in cursor.fetchall():
        print(f"  {file_type}: {count} files")
    
    # Sample join query performance
    import time
    start_time = time.time()
    cursor.execute("""
        SELECT t.key, t.translator, t.language, COUNT(f.id) as file_count
        FROM translations t
        JOIN files f ON t.key = f.translation_key
        GROUP BY t.key, t.translator, t.language
        ORDER BY file_count DESC
        LIMIT 5
    """)
    results = cursor.fetchall()
    query_time = time.time() - start_time
    
    print(f"\nPERFORMANCE TEST:")
    print("-" * 50)
    print(f"Join query time: {query_time*1000:.2f}ms")
    print("Top translations by file count:")
    for key, translator, language, file_count in results:
        print(f"  {key}: {translator} ({language}) -> {file_count} files")
    
    # Database size
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]
    
    print(f"\nDATABASE STATISTICS:")
    print("-" * 50)
    print(f"Database size: {db_size/1024/1024:.2f} MB")
    print(f"Total translations: {trans_count}")
    print(f"Total files: {files_count}")
    print(f"Metadata entries: {metadata_count}")
    print(f"Average files per translation: {files_count/trans_count:.2f}")
    
    conn.close()
    
    print(f"\n{'='*80}")
    print("VERIFICATION RESULTS:")
    
    checks_passed = []
    if 'verses' not in tables:
        checks_passed.append("✅ Verses table successfully removed")
    else:
        checks_passed.append("❌ Verses table still present")
    
    if not duplicates:
        checks_passed.append("✅ No duplicate metadata entries")
    else:
        checks_passed.append("❌ Duplicate metadata found")
    
    if not orphaned and not no_files:
        checks_passed.append("✅ Perfect one-to-many relationships")
    else:
        checks_passed.append("❌ Relationship integrity issues")
    
    if all("✅" in check for check in checks_passed):
        checks_passed.append("✅ CRUD-based schema working correctly")
        checks_passed.append("✅ Database recreation SUCCESSFUL")
    
    for check in checks_passed:
        print(check)
    
    print("="*80)

if __name__ == "__main__":
    verify_clean_database()