#!/usr/bin/env python3
"""
Example Usage Script for Web Resource Metadata Extractor

This script demonstrates how to use the WebResourceExtractor class
to extract metadata from web pages containing downloadable resources.

Usage Examples:
1. Single URL extraction
2. Multiple URLs batch processing
3. Custom configuration
4. Different export formats

Author: Generated for UQSAD Project
Date: 2025-08-31
"""

from web_resource_extractor import WebResourceExtractor, ResourceMetadata
import json
from pathlib import Path


def example_single_url():
    """Example: Extract metadata from a single URL"""
    print("=== Single URL Extraction Example ===")
    
    # Initialize extractor
    extractor = WebResourceExtractor(
        output_dir="examples_output", 
        log_level="INFO"
    )
    
    # URL to analyze (replace with your actual URL)
    url = "https://example.com/resource-page"
    
    # Extract metadata
    print(f"Analyzing: {url}")
    metadata = extractor.extract_resource_metadata(url)
    
    if metadata:
        print(f"✅ Successfully extracted metadata:")
        print(f"   Resource Name: {metadata.resource_name}")
        print(f"   Associated Person: {metadata.associated_person}")
        print(f"   Available Formats: {', '.join(metadata.available_formats)}")
        print(f"   Download URLs: {len(metadata.download_urls)} found")
        print(f"   Tags: {', '.join(metadata.tags[:5])}...")  # Show first 5 tags
        
        # Save individual result
        extractor.save_to_json([metadata], "single_url_result.json")
    else:
        print("❌ Failed to extract metadata")


def example_batch_processing():
    """Example: Process multiple URLs in batch"""
    print("\n=== Batch Processing Example ===")
    
    # Initialize extractor
    extractor = WebResourceExtractor(
        output_dir="batch_output",
        log_level="INFO"
    )
    
    # List of URLs to process (replace with your actual URLs)
    urls = [
        "https://example.com/resource1",
        "https://example.com/resource2",
        "https://example.com/resource3"
    ]
    
    print(f"Processing {len(urls)} URLs...")
    
    # Extract metadata from all URLs
    results = extractor.extract_multiple_resources(urls)
    
    print(f"✅ Successfully processed {len(results)}/{len(urls)} URLs")
    
    # Save results in multiple formats
    if results:
        extractor.save_to_json(results, "batch_results.json")
        extractor.save_to_csv(results, "batch_results.csv")
        
        # Print summary
        print("\n📊 Summary:")
        for result in results:
            print(f"   • {result.resource_name[:50]}...")
            print(f"     Person: {result.associated_person}")
            print(f"     Formats: {len(result.available_formats)}")
            print()


def example_custom_configuration():
    """Example: Using custom configuration for specific sites"""
    print("\n=== Custom Configuration Example ===")
    
    # Create extractor with custom settings
    extractor = WebResourceExtractor(
        output_dir="custom_output",
        log_level="DEBUG"  # More verbose logging
    )
    
    # You can customize patterns for specific sites
    # Add custom download patterns
    extractor.download_patterns.extend([
        r'تحميل',  # Arabic for "download"
        r'تنزيل',  # Arabic for "download"
        r'حفظ',    # Arabic for "save"
    ])
    
    # Add custom person name indicators
    extractor.person_indicators.extend([
        'الشيخ',   # Arabic for "Sheikh"
        'الدكتور', # Arabic for "Doctor"
        'الأستاذ', # Arabic for "Professor"
    ])
    
    # Add custom file format patterns
    extractor.format_patterns.extend([
        r'\.epub', r'\.mobi', r'\.azw3'  # E-book formats
    ])
    
    url = "https://example-arabic-site.com/resource"
    metadata = extractor.extract_resource_metadata(url)
    
    if metadata:
        print("✅ Custom extraction successful")
        extractor.save_to_json([metadata], "custom_result.json")
    else:
        print("❌ Custom extraction failed")


def example_analyze_results():
    """Example: Analyze extracted results"""
    print("\n=== Results Analysis Example ===")
    
    # Load previously extracted data
    results_file = Path("batch_output/batch_results.json")
    
    if results_file.exists():
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Analyzing {len(data)} extracted resources:")
        
        # Analyze file formats
        format_counts = {}
        person_counts = {}
        tag_counts = {}
        
        for item in data:
            # Count formats
            for fmt in item.get('available_formats', []):
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
            
            # Count persons
            person = item.get('associated_person', '').strip()
            if person:
                person_counts[person] = person_counts.get(person, 0) + 1
            
            # Count tags
            for tag in item.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print("\n📈 Most common file formats:")
        for fmt, count in sorted(format_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {fmt}: {count} resources")
        
        print("\n👤 Most frequent contributors:")
        for person, count in sorted(person_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {person}: {count} resources")
        
        print("\n🏷️ Most common tags:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {tag}: {count} resources")
            
    else:
        print("❌ No results file found. Run batch processing first.")


def interactive_mode():
    """Interactive mode for testing URLs"""
    print("\n=== Interactive Mode ===")
    print("Enter URLs to analyze (press Enter with empty line to finish):")
    
    urls = []
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)
    
    if urls:
        extractor = WebResourceExtractor(
            output_dir="interactive_output",
            log_level="INFO"
        )
        
        results = extractor.extract_multiple_resources(urls)
        
        if results:
            extractor.save_to_json(results, "interactive_results.json")
            print(f"✅ Results saved to interactive_output/interactive_results.json")
        else:
            print("❌ No results extracted")
    else:
        print("No URLs provided.")


def main():
    """Main function demonstrating all examples"""
    print("🔍 Web Resource Metadata Extractor - Example Usage")
    print("=" * 60)
    
    # Note: These are example URLs - replace with actual URLs for testing
    print("⚠️ Note: Replace example URLs with actual URLs for testing")
    print()
    
    # Run examples
    try:
        # Uncomment the examples you want to run:
        
        # example_single_url()
        # example_batch_processing()
        # example_custom_configuration()
        # example_analyze_results()
        
        # For interactive testing:
        interactive_mode()
        
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
    
    print("\n✅ Example usage completed")


if __name__ == "__main__":
    main()