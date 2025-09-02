#!/usr/bin/env python3
"""
Complete Arabic QCS renaming for all TR_ folders
Format: TR-AB-RESOURCE_NAME
"""

import sqlite3
import os
import json
from pathlib import Path

def main():
    db_path = "../quranenc_main.db"
    translations_dir = Path(".")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all translations
    cursor.execute("SELECT key, translator, language, direction, source FROM translations ORDER BY language, translator")
    translations = cursor.fetchall()
    
    # Create a mapping of database info
    db_info = {}
    for key, translator, language, direction, source in translations:
        db_info[key] = {
            'translator': translator,
            'language': language,
            'direction': direction,
            'source': source
        }
    
    rename_log = []
    
    print("Converting all TR_ folders to QCS format TR-AB-RESOURCE...")
    print("=" * 60)
    
    # Get all TR_ folders
    tr_folders = [f for f in translations_dir.glob("TR_*") if f.is_dir()]
    
    for folder in tr_folders:
        folder_name = folder.name
        
        try:
            # Extract language code from folder name (first part after TR_)
            parts = folder_name.split('_')
            if len(parts) >= 4:
                lang_code = parts[1]  # TR_LANG_ORG_PERSON
                org_type = parts[2]
                person = '_'.join(parts[3:])
                
                # Create QCS compliant name
                if len(person) > 15:
                    person = person[:15]
                
                qcs_name = f"TR-AB-{lang_code}_{org_type}_{person}"
                
                # Handle length limit
                if len(qcs_name) > 50:
                    qcs_name = qcs_name[:50]
                
                new_path = translations_dir / qcs_name
                
                # Check if target exists
                if new_path.exists():
                    counter = 1
                    while new_path.exists():
                        qcs_name = f"TR-AB-{lang_code}_{org_type}_{person}_{counter}"
                        if len(qcs_name) > 50:
                            qcs_name = qcs_name[:50]
                        new_path = translations_dir / qcs_name
                        counter += 1
                
                # Rename folder
                folder.rename(new_path)
                
                # Generate metadata if we can find matching database record
                matching_key = None
                for key, info in db_info.items():
                    if (lang_code.lower() in info['language'].lower() or 
                        info['language'].lower()[:3] in lang_code.lower()):
                        if person.upper() in info['translator'].upper():
                            matching_key = key
                            break
                
                if matching_key:
                    metadata = {
                        "content_framework": {
                            "category": "TR",
                            "description": "Translation - ترجمة",
                            "hierarchy": "AB", 
                            "hierarchy_type": "Ayah-Based - مبني على الآيات"
                        },
                        "translation_info": db_info[matching_key],
                        "qcs_compliance": {
                            "version": "1.0",
                            "date": "2025-09-01",
                            "standard": "TR-AB-RESOURCE_NAME",
                            "original_folder": folder_name
                        }
                    }
                    
                    metadata_file = new_path / "translation_metadata.json"
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                rename_log.append(f"{folder_name} -> {qcs_name}")
                print(f"SUCCESS: {folder_name} -> {qcs_name}")
                
        except Exception as e:
            print(f"FAILED: {folder_name} ({e})")
            rename_log.append(f"FAILED: {folder_name} ({e})")
    
    # Write final log
    with open("complete_qcs_log.txt", "w", encoding="utf-8") as f:
        f.write("Complete Arabic QCS Standards Application\n")
        f.write("Format: TR-AB-RESOURCE_NAME\n")
        f.write("=" * 50 + "\n\n")
        for log_entry in rename_log:
            f.write(log_entry + "\n")
    
    print(f"\nCOMPLETE: All TR_ folders converted to QCS format")
    print(f"Log: complete_qcs_log.txt") 
    print(f"Total processed: {len(tr_folders)} folders")
    
    conn.close()

if __name__ == "__main__":
    main()