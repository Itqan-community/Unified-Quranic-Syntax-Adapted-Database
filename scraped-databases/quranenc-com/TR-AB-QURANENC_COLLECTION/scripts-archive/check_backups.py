#!/usr/bin/env python3
"""
Check which backup is the last stable version
"""

import sqlite3
from pathlib import Path

def check_backup_integrity():
    """Check all backups to find the last stable one"""
    
    base_dir = Path(__file__).parent
    backups = [
        'quranenc_backup_20250901_104852.db',  # Before restructuring attempts
        'quranenc_backup_20250901_104907.db',  # After first attempt
        'quranenc_backup_safe_20250901_105002.db'  # Before safe restructuring
    ]
    
    print("="*70)
    print("BACKUP INTEGRITY CHECK")
    print("="*70)
    
    stable_backup = None
    
    for backup_name in backups:
        backup_path = base_dir / backup_name
        if not backup_path.exists():
            print(f"❌ {backup_name}: File not found")
            continue
            
        print(f"\n📁 {backup_name}:")
        
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   Tables: {tables}")
            
            # Check for duplicate metadata
            cursor.execute("SELECT key, COUNT(*) as count FROM metadata GROUP BY key HAVING count > 1")
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"   ⚠️ Duplicate metadata keys found:")
                for key, count in duplicates:
                    print(f"      {key}: {count} entries")
            else:
                print(f"   ✅ No duplicate metadata keys")
            
            # Check translation count
            if 'translations' in tables:
                cursor.execute("SELECT COUNT(*) FROM translations")
                trans_count = cursor.fetchone()[0]
                print(f"   Translations: {trans_count}")
            
            # Check files count
            if 'files' in tables:
                cursor.execute("SELECT COUNT(*) FROM files")
                files_count = cursor.fetchone()[0]
                print(f"   Files: {files_count}")
            
            # Check verses count
            if 'verses' in tables:
                cursor.execute("SELECT COUNT(*) FROM verses")
                verses_count = cursor.fetchone()[0]
                print(f"   Verses: {verses_count:,}")
            else:
                print(f"   Verses: Table not present")
            
            # Check metadata consistency
            cursor.execute("SELECT COUNT(DISTINCT key) as unique_keys, COUNT(*) as total_entries FROM metadata")
            unique_keys, total_entries = cursor.fetchone()
            print(f"   Metadata: {total_entries} entries, {unique_keys} unique keys")
            
            # This backup is good if no duplicates and has expected structure
            if not duplicates and 'translations' in tables and 'files' in tables:
                if stable_backup is None:  # First good backup we find
                    stable_backup = backup_name
                    print(f"   ✅ STABLE BACKUP CANDIDATE")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error checking backup: {e}")
    
    print(f"\n{'='*70}")
    if stable_backup:
        print(f"🎯 RECOMMENDED STABLE BACKUP: {stable_backup}")
    else:
        print("❌ No stable backup found!")
    print("="*70)
    
    return stable_backup

if __name__ == "__main__":
    check_backup_integrity()