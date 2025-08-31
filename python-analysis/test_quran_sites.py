#!/usr/bin/env python3
"""
Test Script for Quran Resource Sites

Testing the web resource extractor with two specific Quranic resource sites:
1. https://qul.tarteel.ai/resources/quran-script (Quranic Script/Text)
2. https://quranenc.com/en/home (Quran Translation)

This script will help us understand the structure of these sites and
improve our extraction patterns.
"""

import sys
import json
from web_resource_extractor import WebResourceExtractor
from pathlib import Path


def test_quran_sites():
    """Test extraction from both Quran resource sites"""
    
    print("=== Testing Web Resource Extractor with Quranic Sites ===")
    print("=" * 60)
    
    # URLs to test
    urls = [
        {
            'url': 'https://qul.tarteel.ai/resources/quran-script',
            'type': 'Quranic Script/Text',
            'description': 'QUL Tarteel - Quran Script Resources'
        },
        {
            'url': 'https://quranenc.com/en/home',
            'type': 'Quran Translation',
            'description': 'QuranEnc - Quran Encyclopedia and Translations'
        }
    ]
    
    # Initialize extractor with debug logging
    extractor = WebResourceExtractor(
        output_dir="test_results",
        log_level="DEBUG"
    )
    
    # Add Quran-specific patterns
    print("\n=== Adding Quran-specific extraction patterns...")
    
    # Add Islamic/Arabic download patterns
    extractor.download_patterns.extend([
        'تحميل',      # Download in Arabic
        'تنزيل',      # Download in Arabic  
        'حفظ',        # Save in Arabic
        'مصحف',       # Mushaf (Quran book)
        'قرآن',       # Quran in Arabic
        'script',     # For Quran script
        'text',       # For Quran text
        'mushaf',     # Mushaf in English
        'recitation', # Quran recitation
        'translation' # Quran translation
    ])
    
    # Add Islamic scholar/person indicators
    extractor.person_indicators.extend([
        'الشيخ',      # Sheikh
        'الدكتور',    # Doctor
        'الأستاذ',    # Professor
        'الإمام',     # Imam
        'المقرئ',     # Reciter
        'الحافظ',     # Hafiz
        'العالم',     # Scholar
        'sheikh',     # Sheikh in English
        'imam',       # Imam in English
        'reciter',    # Quran reciter
        'hafiz',      # Hafiz in English
        'scholar',    # Islamic scholar
        'translator', # Translator
        'authored',   # Authored by
        'compiled'    # Compiled by
    ])
    
    # Add Quran-specific file formats
    extractor.format_patterns.extend([
        r'\.uthmani',   # Uthmani script format
        r'\.qcf',       # Quran Complex Font
        r'\.ttf',       # TrueType fonts
        r'\.otf',       # OpenType fonts
        r'\.woff',      # Web fonts
        r'\.usx',       # USX format
        r'\.sqlite3',   # SQLite3 databases
    ])
    
    print("[SUCCESS] Added Quran-specific patterns")
    
    # Test each URL
    results = []
    for i, url_info in enumerate(urls, 1):
        print(f"\n{'='*20} Testing {i}/{len(urls)} {'='*20}")
        print(f"URL: {url_info['url']}")
        print(f"Type: {url_info['type']}")
        print(f"Description: {url_info['description']}")
        print()
        
        try:
            # Extract metadata
            metadata = extractor.extract_resource_metadata(url_info['url'])
            
            if metadata:
                print("[SUCCESS] EXTRACTION SUCCESSFUL!")
                print(f"   Page Title: {metadata.page_title}")
                print(f"   Resource Name: {metadata.resource_name}")
                print(f"   Associated Person: {metadata.associated_person}")
                print(f"   File Extension: {metadata.file_extension}")
                print(f"   Download URLs: {len(metadata.download_urls)} found")
                print(f"   Available Formats: {', '.join(metadata.available_formats)}")
                print(f"   Tags: {', '.join(metadata.tags[:10])}...")  # First 10 tags
                print(f"   Description: {metadata.description[:100]}...")  # First 100 chars
                
                # Add URL info to metadata for context
                metadata.metadata['url_type'] = url_info['type']
                metadata.metadata['url_description'] = url_info['description']
                
                results.append(metadata)
                
                # Save individual result
                filename = f"test_{url_info['type'].lower().replace('/', '_').replace(' ', '_')}.json"
                extractor.save_to_json([metadata], filename)
                print(f"   💾 Saved to: test_results/{filename}")
                
            else:
                print("❌ EXTRACTION FAILED - No metadata extracted")
                
        except Exception as e:
            print(f"❌ ERROR during extraction: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary and combined results
    print("📊 SUMMARY")
    print("=" * 30)
    print(f"✅ Successfully extracted: {len(results)}/{len(urls)} sites")
    
    if results:
        # Save combined results
        extractor.save_to_json(results, "combined_quran_sites.json")
        extractor.save_to_csv(results, "combined_quran_sites.csv")
        print("💾 Combined results saved to test_results/")
        
        # Analysis
        print("\n🔍 ANALYSIS")
        print("-" * 20)
        
        total_downloads = sum(len(r.download_urls) for r in results)
        total_formats = sum(len(r.available_formats) for r in results)
        total_tags = sum(len(r.tags) for r in results)
        
        print(f"📈 Total download URLs found: {total_downloads}")
        print(f"📈 Total file formats found: {total_formats}")
        print(f"📈 Total tags extracted: {total_tags}")
        
        print("\n📋 Formats found across all sites:")
        all_formats = set()
        for result in results:
            all_formats.update(result.available_formats)
        for fmt in sorted(all_formats):
            print(f"   • {fmt}")
        
        print("\n👥 People/Authors found:")
        for result in results:
            if result.associated_person:
                print(f"   • {result.associated_person}")
        
        print("\n🏷️ Most common tags:")
        tag_counts = {}
        for result in results:
            for tag in result.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"   • {tag}: {count}")
            
    else:
        print("❌ No successful extractions")
    
    return results


def analyze_structure():
    """Analyze the structure of extracted data for pattern improvement"""
    
    results_file = Path("test_results/combined_quran_sites.json")
    if not results_file.exists():
        print("❌ No results file found. Run test_quran_sites() first.")
        return
    
    print("\n🔬 DETAILED STRUCTURE ANALYSIS")
    print("=" * 40)
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, item in enumerate(data, 1):
        print(f"\n--- Site {i}: {item.get('url_type', 'Unknown')} ---")
        print(f"URL: {item['url']}")
        print(f"Page Title: {item['page_title']}")
        
        print(f"\nDownload URLs ({len(item['download_urls'])}):")
        for j, url in enumerate(item['download_urls'][:5], 1):  # Show first 5
            print(f"  {j}. {url}")
        if len(item['download_urls']) > 5:
            print(f"  ... and {len(item['download_urls']) - 5} more")
        
        print(f"\nMetadata keys found:")
        for key, value in item['metadata'].items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"  • {key}: {value}")
        
        print(f"\nTags ({len(item['tags'])}):")
        for tag in item['tags'][:10]:  # Show first 10
            print(f"  • {tag}")
        if len(item['tags']) > 10:
            print(f"  ... and {len(item['tags']) - 10} more")


def main():
    """Main function"""
    print("=== Quran Sites Testing Script ===")
    print("Testing extraction from QUL Tarteel and QuranEnc")
    
    try:
        # Test the sites
        results = test_quran_sites()
        
        # Analyze structure if we got results
        if results:
            analyze_structure()
            
        print("\n✅ Testing completed successfully!")
        print("📁 Check the 'test_results' directory for detailed output files")
        
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()