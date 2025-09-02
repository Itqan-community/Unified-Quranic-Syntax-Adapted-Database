#!/usr/bin/env python3
"""
Resume QuranEnc.com scraping from where we left off
"""

import requests
import json
import os
from pathlib import Path
from quranenc_scraper import QuranEncScraper

def find_completed_translations(base_dir):
    """Find which translations have already been processed"""
    translations_dir = Path(base_dir) / "translations"
    if not translations_dir.exists():
        return set()
    
    completed = set()
    for translation_dir in translations_dir.iterdir():
        if translation_dir.is_dir():
            # Extract translation key from directory name (first part before underscore)
            dir_name = translation_dir.name
            if '_' in dir_name:
                translation_key = dir_name.split('_')[0]
                completed.add(translation_key)
    return completed

def main():
    base_directory = Path(__file__).parent
    scraper = QuranEncScraper(base_directory)
    
    # Get all translations
    all_translations = scraper.get_translations_list()
    print(f"Total translations available: {len(all_translations)}")
    
    # Find which ones are already completed
    completed = find_completed_translations(base_directory)
    print(f"Already completed: {len(completed)}")
    
    # Filter to remaining translations
    remaining_translations = [t for t in all_translations if t.get('key') not in completed]
    print(f"Remaining to process: {len(remaining_translations)}")
    
    if not remaining_translations:
        print("All translations have been processed!")
        return
    
    # Process remaining translations
    print("\nResuming download of remaining translations...")
    for i, translation in enumerate(remaining_translations, 1):
        print(f"\nProcessing {i}/{len(remaining_translations)}: {translation.get('key', 'unknown')}")
        try:
            translation_metadata = scraper.download_translation_data(translation)
            scraper.metadata['translations'].append(translation_metadata)
            
            # Small delay to be respectful
            import time
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {translation.get('key', 'unknown')}: {e}")
            scraper.metadata.setdefault('errors', []).append({
                'translation_key': translation.get('key', 'unknown'),
                'error': str(e)
            })
    
    # Update metadata and generate report
    scraper.metadata['total_translations'] = len(all_translations)
    scraper.save_metadata()
    scraper.generate_report()
    
    print("\nResume operation completed!")

if __name__ == "__main__":
    main()