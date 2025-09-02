#!/usr/bin/env python3
"""
Apply Arabic QCS standards to translation folders
Format: TR-AB-RESOURCE_NAME (according to QCS)
"""

import sqlite3
import os
import json
from pathlib import Path

def get_arabic_qcs_name(language, translator, key):
    """Generate Arabic QCS compliant name: TR-AB-RESOURCE"""
    
    # Create simple resource identifier
    lang_short = language[:3].upper() if language else "UNK"
    trans_short = translator.split()[0][:8].upper() if translator else "UNKNOWN"
    
    # QCS format: TR-AB-RESOURCE
    resource_name = f"{lang_short}_{trans_short}_{key.upper()}"
    
    return f"TR-AB-{resource_name}"

def generate_metadata_file(translation_data, folder_path):
    """Generate QCS metadata file"""
    
    metadata = {
        "content_framework": {
            "category": "TR",
            "description": "Translation",
            "hierarchy": "AB",
            "hierarchy_type": "Ayah-Based"
        },
        "translation_info": {
            "key": translation_data['key'],
            "translator": translation_data['translator'],
            "language": translation_data['language'],
            "direction": translation_data['direction'],
            "source": translation_data['source']
        },
        "qcs_compliance": {
            "version": "1.0",
            "date": "2025-09-01",
            "standard": "TR-AB-RESOURCE_NAME"
        }
    }
    
    metadata_file = folder_path / "translation_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return metadata_file

def main():
    db_path = "../quranenc_main.db"
    translations_dir = Path(".")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all translations
    cursor.execute("SELECT key, translator, language, direction, source FROM translations ORDER BY language, translator")
    translations = cursor.fetchall()
    
    rename_log = []
    
    print("Applying Arabic QCS Standards to Translation Folders...")
    print("=" * 60)
    
    for key, translator, language, direction, source in translations:
        
        # Generate Arabic QCS compliant name
        qcs_name = get_arabic_qcs_name(language, translator, key)
        
        # Find current TR_ folder
        current_folders = [f for f in translations_dir.glob("TR_*") if f.is_dir()]
        
        target_folder = None
        for folder in current_folders:
            # Try to match by key in folder name
            if key.upper() in folder.name.upper():
                target_folder = folder
                break
            # Try to match by language and partial translator
            if language.upper()[:3] in folder.name.upper() and translator.split()[0].upper()[:5] in folder.name.upper():
                target_folder = folder
                break
        
        if target_folder and target_folder.is_dir():
            new_path = translations_dir / qcs_name
            
            try:
                if new_path.exists():
                    print(f"WARNING: Target exists, adding suffix")
                    qcs_name = f"{qcs_name}_DUP"
                    new_path = translations_dir / qcs_name
                
                # Rename folder to QCS format
                target_folder.rename(new_path)
                
                # Generate QCS metadata file
                translation_data = {
                    'key': key,
                    'translator': translator,
                    'language': language,
                    'direction': direction,
                    'source': source
                }
                generate_metadata_file(translation_data, new_path)
                
                rename_log.append(f"{target_folder.name} -> {qcs_name}")
                print(f"SUCCESS: {target_folder.name} -> {qcs_name}")
                
            except Exception as e:
                print(f"FAILED: {target_folder.name} -> {qcs_name} ({e})")
                rename_log.append(f"FAILED: {target_folder.name} -> {qcs_name} ({e})")
        else:
            print(f"NOT_FOUND: {key}")
            rename_log.append(f"NOT_FOUND: {key}")
    
    # Write rename log
    with open("qcs_application_log.txt", "w", encoding="utf-8") as f:
        f.write("Arabic QCS Standards Application Log\n")
        f.write("Format: TR-AB-RESOURCE_NAME\n")
        f.write("=" * 50 + "\n\n")
        for log_entry in rename_log:
            f.write(log_entry + "\n")
    
    print(f"\nCOMPLETE: QCS standards applied")
    print(f"Log: qcs_application_log.txt")
    print(f"Total processed: {len(translations)} translations")
    
    conn.close()

if __name__ == "__main__":
    main()