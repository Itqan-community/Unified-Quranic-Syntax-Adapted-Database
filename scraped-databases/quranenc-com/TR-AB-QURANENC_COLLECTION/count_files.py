#!/usr/bin/env python3
import os
from pathlib import Path
import json

# Count downloaded files
base_dir = Path(".")
translations_dir = base_dir / "translations"

if translations_dir.exists():
    all_files = []
    for root, dirs, files in os.walk(translations_dir):
        for file in files:
            if file.endswith(('.json', '.pdf', '.epub', '.xml', '.csv', '.xlsx')):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                all_files.append({'path': file_path, 'size': file_size, 'extension': os.path.splitext(file)[1]})
    
    # Group by extension
    by_extension = {}
    total_size = 0
    for file_info in all_files:
        ext = file_info['extension']
        if ext not in by_extension:
            by_extension[ext] = {'count': 0, 'total_size': 0}
        by_extension[ext]['count'] += 1
        by_extension[ext]['total_size'] += file_info['size']
        total_size += file_info['size']
    
    print(f"=== QuranEnc.com Download Progress ===")
    print(f"Total files downloaded: {len(all_files)}")
    print(f"Total size: {total_size / (1024*1024):.1f} MB")
    print(f"\nBreakdown by file type:")
    for ext, info in sorted(by_extension.items()):
        print(f"  {ext}: {info['count']} files ({info['total_size'] / (1024*1024):.1f} MB)")
    
    # Count directories (translations)
    translation_dirs = [d for d in translations_dir.iterdir() if d.is_dir()]
    print(f"\nTranslations processed: {len(translation_dirs)}")
    
    # Show some examples
    print(f"\nSample translations downloaded:")
    for i, dir_name in enumerate(sorted([d.name for d in translation_dirs[:10]])):
        print(f"  {i+1}. {dir_name}")
    if len(translation_dirs) > 10:
        print(f"  ... and {len(translation_dirs) - 10} more")
else:
    print("No translations directory found!")