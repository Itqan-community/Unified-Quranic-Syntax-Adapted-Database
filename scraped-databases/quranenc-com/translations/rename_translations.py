#!/usr/bin/env python3
"""
Rename translation folders according to QCS standards with database metadata
Format: LANG_ORG_PERSON (Language Code - Organization - Person)
"""

import sqlite3
import os
import shutil
from pathlib import Path

# Language code mapping (ISO 639-1/639-2 where available)
LANGUAGE_CODES = {
    'Afar': 'AA',           # ISO 639-1
    'Albanian': 'SQ',       # ISO 639-1
    'Amharic': 'AM',        # ISO 639-1
    'Ankobambara': 'AKO',   # Custom code
    'Asante': 'AST',        # Custom code
    'Assamese': 'AS',       # ISO 639-1
    'Azerbaijani': 'AZ',    # ISO 639-1
    'Bisayan': 'CEB',       # ISO 639-2
    'Bosnian': 'BS',        # ISO 639-1
    'Chinese': 'ZH',        # ISO 639-1
    'Croatian': 'HR',       # ISO 639-1
    'Dutch': 'NL',          # ISO 639-1
    'English': 'EN',        # ISO 639-1
    'French': 'FR',         # ISO 639-1
    'German': 'DE',         # ISO 639-1
    'Gujarati': 'GU',       # ISO 639-1
    'Hausa': 'HA',          # ISO 639-1
    'Hindi': 'HI',          # ISO 639-1
    'Ikirundi': 'RN',       # ISO 639-1
    'Indonesian': 'ID',     # ISO 639-1
    'Japanese': 'JA',       # ISO 639-1
    'Kannada': 'KN',        # ISO 639-1
    'Khmer': 'KM',          # ISO 639-1
    'Kinyarwanda': 'RW',    # ISO 639-1
    'Kurdish': 'KU',        # ISO 639-1
    'Kyrgyz': 'KY',         # ISO 639-1
    'Lingala': 'LN',        # ISO 639-1
    'Lithuanian': 'LT',     # ISO 639-1
    'Macedonian': 'MK',     # ISO 639-1
    'Malayalam': 'ML',      # ISO 639-1
    'Moore': 'MOR',         # Custom code
    'Oromo': 'OM',          # ISO 639-1
    'Pashto': 'PS',         # ISO 639-1
    'Persian': 'FA',        # ISO 639-1
    'Portuguese': 'PT',     # ISO 639-1
    'Punjabi': 'PA',        # ISO 639-1
    'Romanian': 'RO',       # ISO 639-1
    'Serbian': 'SR',        # ISO 639-1
    'Sinhalese': 'SI',      # ISO 639-1
    'Somali': 'SO',         # ISO 639-1
    'Spanish': 'ES',        # ISO 639-1
    'Swahili': 'SW',        # ISO 639-1
    'Tagalog': 'TL',        # ISO 639-1
    'Tajik': 'TG',          # ISO 639-1
    'Tamil': 'TA',          # ISO 639-1
    'Telugu': 'TE',         # ISO 639-1
    'Turkish': 'TR',        # ISO 639-1
    'Urdu': 'UR',           # ISO 639-1
    'Uyghur': 'UG',         # ISO 639-1
    'Uzbek': 'UZ',          # ISO 639-1
    'Vietnamese': 'VI',     # ISO 639-1
    'Yoruba': 'YO',         # ISO 639-1
}

def clean_name(name):
    """Clean and standardize names for folder naming"""
    if not name:
        return "UNKNOWN"
    
    # Remove problematic characters and standardize
    name = name.strip()
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace("&", "AND")
    name = name.replace(",", "_")
    name = name.replace(".", "")
    name = name.replace("'", "")
    name = name.replace('"', "")
    name = name.upper()
    
    # Handle common organization abbreviations
    if "ROWWAD" in name:
        return "ROWWAD"
    if "NOOR_INTERNATIONAL" in name:
        return "NOOR_INTL"
    if "MUSLIM_ASSOCIATION" in name:
        return "MUSLIM_ASSOC"
    if "AFRICA_ACADEMY" in name:
        return "AFRICA_ACADEMY"
    if "TRANSLATION_CENTER" in name:
        return "TRANS_CENTER"
    
    return name[:20]  # Limit length

def extract_org_person(translator, source):
    """Extract organization and person from translator and source fields"""
    if not translator:
        translator = "UNKNOWN"
    
    # Check if translator contains organization info
    if "Center" in translator or "Academy" in translator or "Association" in translator or "International" in translator:
        org = clean_name(translator)
        person = "COLLECTIVE"
    else:
        # Individual translator
        org = "INDIVIDUAL"
        person = clean_name(translator)
    
    return org, person

def get_new_folder_name(lang_code, org, person):
    """Generate new folder name according to QCS: LANG_ORG_PERSON"""
    # Apply QCS TR category prefix
    return f"TR_{lang_code}_{org}_{person}"

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
    
    for key, translator, language, direction, source in translations:
        # Get language code
        lang_code = LANGUAGE_CODES.get(language.title(), language[:3].upper())
        
        # Extract organization and person
        org, person = extract_org_person(translator, source)
        
        # Generate new folder name
        new_name = get_new_folder_name(lang_code, org, person)
        
        # Find current folder (it might have various naming patterns)
        current_folders = list(translations_dir.glob(f"{key}*"))
        
        if current_folders:
            current_folder = current_folders[0]
            new_path = translations_dir / new_name
            
            # Check if rename is needed
            if current_folder.name != new_name:
                try:
                    if new_path.exists():
                        print(f"WARNING: Target folder {new_name} already exists for {key}")
                        new_name = f"{new_name}_{key.upper()}"
                        new_path = translations_dir / new_name
                    
                    current_folder.rename(new_path)
                    rename_log.append(f"{current_folder.name} -> {new_name}")
                    print(f"SUCCESS: {current_folder.name} -> {new_name}")
                    
                except Exception as e:
                    print(f"FAILED: {current_folder.name} -> {new_name} ({e})")
                    rename_log.append(f"FAILED: {current_folder.name} -> {new_name} ({e})")
            else:
                print(f"NO_CHANGE: {current_folder.name}")
        else:
            print(f"NOT_FOUND: {key}")
            rename_log.append(f"NOT_FOUND: {key}")
    
    # Write rename log
    with open("rename_log.txt", "w", encoding="utf-8") as f:
        f.write("Translation Folder Renaming Log\n")
        f.write("=" * 50 + "\n\n")
        for log_entry in rename_log:
            f.write(log_entry + "\n")
    
    print(f"\nSUCCESS: Renaming complete. Log written to rename_log.txt")
    print(f"Total translations processed: {len(translations)}")
    
    conn.close()

if __name__ == "__main__":
    main()