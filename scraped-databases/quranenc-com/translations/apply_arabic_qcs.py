#!/usr/bin/env python3
"""
Apply Arabic QCS standards to translation folders and files
Format: TR-AB-RESOURCE_NAME (according to معايير المحتوى القرآني)
"""

import sqlite3
import os
import json
from pathlib import Path

# Arabic language name mapping for QCS compliance
ARABIC_LANGUAGE_NAMES = {
    'Afar': 'عفار',
    'Albanian': 'ألباني',
    'Amharic': 'أمهري',
    'Ankobambara': 'أنكوبامبارا',
    'Asante': 'أسانتي',
    'Assamese': 'أسامي',
    'Azerbaijani': 'أذربيجاني',
    'Bisayan': 'بيسايان',
    'Bosnian': 'بوسني',
    'Chinese': 'صيني',
    'Croatian': 'كرواتي',
    'Dutch': 'هولندي',
    'English': 'إنجليزي',
    'French': 'فرنسي',
    'German': 'ألماني',
    'Gujarati': 'غوجاراتي',
    'Hausa': 'هوسا',
    'Hindi': 'هندي',
    'Ikirundi': 'روندي',
    'Indonesian': 'إندونيسي',
    'Japanese': 'ياباني',
    'Kannada': 'كانادا',
    'Khmer': 'خمير',
    'Kinyarwanda': 'رواندي',
    'Kurdish': 'كردي',
    'Kyrgyz': 'قرغيزي',
    'Lingala': 'لينغالا',
    'Lithuanian': 'ليتواني',
    'Macedonian': 'مقدوني',
    'Malayalam': 'مالايالام',
    'Moore': 'موري',
    'Oromo': 'أورومو',
    'Pashto': 'بشتو',
    'Persian': 'فارسي',
    'Portuguese': 'برتغالي',
    'Punjabi': 'بنجابي',
    'Romanian': 'روماني',
    'Serbian': 'صربي',
    'Sinhalese': 'سنهالي',
    'Somali': 'صومالي',
    'Spanish': 'إسباني',
    'Swahili': 'سواحلي',
    'Tagalog': 'تاغالوغ',
    'Tajik': 'طاجيكي',
    'Tamil': 'تاميلي',
    'Telugu': 'تيلوغو',
    'Turkish': 'تركي',
    'Urdu': 'أردو',
    'Uyghur': 'أويغوري',
    'Uzbek': 'أوزبكي',
    'Vietnamese': 'فيتنامي',
    'Yoruba': 'يوروبا',
}

def clean_arabic_name(name):
    """Clean and standardize Arabic names"""
    if not name:
        return "غير_محدد"
    
    name = name.strip()
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace("&", "و")
    name = name.replace(",", "_")
    name = name.replace(".", "")
    name = name.replace("'", "")
    name = name.replace('"', "")
    
    return name

def get_arabic_qcs_name(language, translator, key):
    """Generate Arabic QCS compliant name: TR-AB-RESOURCE"""
    
    # Get Arabic language name
    arabic_lang = ARABIC_LANGUAGE_NAMES.get(language.title(), language)
    
    # Clean translator name for Arabic context
    translator_clean = clean_arabic_name(translator)
    
    # Create resource identifier combining language and translator
    # Following QCS format: TR-AB-مورد_محدد
    if len(translator_clean) > 15:
        translator_clean = translator_clean[:15]
    
    resource_name = f"ترجمة_{arabic_lang}_{translator_clean}"
    
    # Full QCS format: Category-Hierarchy-Resource
    return f"TR-AB-{resource_name}"

def generate_qcs_metadata_file(translation_data, folder_path):
    """Generate QCS compliant metadata file for each translation"""
    
    metadata = {
        "إطار_المحتوى": {
            "الفئة": "TR",
            "الوصف": "ترجمة",
            "التسلسل_الهرمي": "AB",
            "نوع_التسلسل": "مبني_على_الآيات"
        },
        "معلومات_الترجمة": {
            "المفتاح": translation_data['key'],
            "المترجم": translation_data['translator'],
            "اللغة": translation_data['language'],
            "اللغة_بالعربية": ARABIC_LANGUAGE_NAMES.get(translation_data['language'].title(), translation_data['language']),
            "الاتجاه": translation_data['direction'],
            "المصدر": translation_data['source']
        },
        "معايير_المحتوى_القرآني": {
            "الإصدار": "1.0",
            "التاريخ": "2025-09-01",
            "المعيار": "TR-AB-مورد_محدد"
        }
    }
    
    metadata_file = folder_path / "معلومات_الترجمة.json"
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
    
    print("تطبيق معايير المحتوى القرآني العربية...")
    print("=" * 50)
    
    for key, translator, language, direction, source in translations:
        
        # Generate Arabic QCS compliant name
        arabic_qcs_name = get_arabic_qcs_name(language, translator, key)
        
        # Find current folder (TR_ prefixed folders from previous rename)
        current_folders = list(translations_dir.glob(f"TR_*{key.upper()}*")) + list(translations_dir.glob(f"TR_*"))
        
        # Find exact match by checking folder contents or database key
        target_folder = None
        for folder in current_folders:
            if key.lower() in folder.name.lower() or any(key.lower() in part.lower() for part in folder.name.split('_')):
                target_folder = folder
                break
        
        if not target_folder:
            # Try finding by original pattern
            pattern_matches = list(translations_dir.glob(f"*{key}*"))
            if pattern_matches:
                target_folder = pattern_matches[0]
        
        if target_folder and target_folder.is_dir():
            new_path = translations_dir / arabic_qcs_name
            
            try:
                if new_path.exists():
                    print(f"تحذير: المجلد الهدف موجود بالفعل {arabic_qcs_name}")
                    arabic_qcs_name = f"{arabic_qcs_name}_{key.upper()}"
                    new_path = translations_dir / arabic_qcs_name
                
                # Rename folder to Arabic QCS format
                target_folder.rename(new_path)
                
                # Generate QCS metadata file
                translation_data = {
                    'key': key,
                    'translator': translator,
                    'language': language,
                    'direction': direction,
                    'source': source
                }
                metadata_file = generate_qcs_metadata_file(translation_data, new_path)
                
                rename_log.append(f"{target_folder.name} -> {arabic_qcs_name}")
                print(f"نجح: {target_folder.name} -> {arabic_qcs_name}")
                
            except Exception as e:
                print(f"فشل: {target_folder.name} -> {arabic_qcs_name} ({e})")
                rename_log.append(f"فشل: {target_folder.name} -> {arabic_qcs_name} ({e})")
        else:
            print(f"غير_موجود: {key}")
            rename_log.append(f"غير_موجود: {key}")
    
    # Write Arabic rename log
    with open("سجل_إعادة_التسمية_العربية.txt", "w", encoding="utf-8") as f:
        f.write("سجل تطبيق معايير المحتوى القرآني العربية\\n")
        f.write("=" * 50 + "\\n\\n")
        for log_entry in rename_log:
            f.write(log_entry + "\\n")
    
    print(f"\\nتم الانتهاء: تم إنشاء السجل في سجل_إعادة_التسمية_العربية.txt")
    print(f"المجموع: {len(translations)} ترجمة")
    
    conn.close()

if __name__ == "__main__":
    main()