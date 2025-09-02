#!/usr/bin/env python3
"""
QuranEnc.com Comprehensive Scraper
Downloads all available Quran translations and metadata from quranenc.com
"""

import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Any
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/quranenc_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QuranEncScraper:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_url = "https://quranenc.com"
        self.api_base = f"{self.base_url}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuranEnc Comprehensive Scraper - Academic Research'
        })
        
        # Statistics
        self.downloaded_files = []
        self.failed_downloads = []
        self.metadata = {
            'scrape_timestamp': datetime.now().isoformat(),
            'source_website': 'https://quranenc.com',
            'total_translations': 0,
            'total_files_downloaded': 0,
            'translations': [],
            'errors': []
        }
        
    def get_translations_list(self) -> List[Dict[str, Any]]:
        """Get list of all available translations from API"""
        logger.info("Fetching translations list from API...")
        try:
            response = self.session.get(f"{self.api_base}/translations/list")
            response.raise_for_status()
            data = response.json()
            translations = data.get('translations', [])
            logger.info(f"Found {len(translations)} translations")
            return translations
        except Exception as e:
            logger.error(f"Failed to get translations list: {e}")
            return []
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for Windows filesystem"""
        # Remove invalid characters for Windows
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace multiple underscores with single
        filename = re.sub(r'_+', '_', filename)
        # Remove trailing dots and spaces
        filename = filename.strip('. ')
        return filename
    
    def download_translation_data(self, translation: Dict[str, Any]) -> Dict[str, Any]:
        """Download all available data for a specific translation"""
        translation_key = translation.get('key', '')
        title = translation.get('title', 'unknown')
        description = translation.get('description', 'unknown')
        language_code = translation.get('language_iso_code', '')
        
        logger.info(f"Processing translation: {title} ({translation_key})")
        
        translation_metadata = {
            'key': translation_key,
            'title': title,
            'description': description,
            'language_code': language_code,
            'direction': translation.get('direction', ''),
            'version': translation.get('version', ''),
            'last_update': translation.get('last_update', ''),
            'files_downloaded': [],
            'api_data': {},
            'download_timestamp': datetime.now().isoformat()
        }
        
        # Create directory for this translation
        safe_key = self.sanitize_filename(translation_key)
        safe_title = self.sanitize_filename(title.replace(' - ', '_').replace(' ', '_'))
        translation_dir = self.base_dir / "translations" / f"{safe_key}_{safe_title}"
        translation_dir.mkdir(parents=True, exist_ok=True)
        
        # Download complete translation via API (all suras)
        self.download_complete_translation_json(translation_key, translation_dir, translation_metadata)
        
        # Download direct PDF/EPUB files if available
        self.download_direct_files(translation, translation_dir, translation_metadata)
        
        # Try to download other formats if available
        self.try_download_other_formats(translation_key, translation_dir, translation_metadata, title)
        
        return translation_metadata
    
    def download_complete_translation_json(self, translation_key: str, output_dir: Path, metadata: Dict):
        """Download complete translation in JSON format via API"""
        logger.info(f"Downloading complete JSON translation for {translation_key}")
        
        complete_translation = {
            'translation_key': translation_key,
            'suras': {}
        }
        
        # Download all 114 suras
        for sura_num in range(1, 115):
            try:
                time.sleep(0.1)  # Be respectful to the server
                response = self.session.get(f"{self.api_base}/translation/sura/{translation_key}/{sura_num}")
                
                if response.status_code == 200:
                    sura_data = response.json()
                    complete_translation['suras'][str(sura_num)] = sura_data
                    logger.debug(f"Downloaded sura {sura_num} for {translation_key}")
                else:
                    logger.warning(f"Failed to download sura {sura_num} for {translation_key}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error downloading sura {sura_num} for {translation_key}: {e}")
                metadata.setdefault('errors', []).append(f"Sura {sura_num}: {str(e)}")
        
        # Save complete translation
        json_file = output_dir / f"quranenc_{translation_key}_complete_translation.json"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(complete_translation, f, ensure_ascii=False, indent=2)
            
            file_size = json_file.stat().st_size
            file_info = {
                'filename': json_file.name,
                'format': 'json',
                'size_bytes': file_size,
                'source_url': f"{self.api_base}/translation/sura/{translation_key}/[1-114]",
                'download_success': True
            }
            metadata['files_downloaded'].append(file_info)
            metadata['api_data'] = complete_translation
            self.downloaded_files.append(str(json_file))
            
            logger.info(f"Saved complete translation: {json_file} ({file_size} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to save JSON translation {translation_key}: {e}")
            metadata.setdefault('errors', []).append(f"JSON save error: {str(e)}")
    
    def download_direct_files(self, translation: Dict[str, Any], output_dir: Path, metadata: Dict):
        """Download files with direct URLs provided by the API"""
        translation_key = translation.get('key', '')
        title = translation.get('title', 'unknown')
        
        # Map of URL keys to format info
        direct_files = {
            'pdf_url': {'format': 'pdf', 'type': 'standard'},
            'pdf_pure_url': {'format': 'pdf', 'type': 'pure'},  
            'pdf_mobile_url': {'format': 'pdf', 'type': 'mobile'},
            'epub_url': {'format': 'epub', 'type': 'standard'}
        }
        
        for url_key, file_info in direct_files.items():
            file_url = translation.get(url_key)
            if file_url:
                try:
                    logger.info(f"Downloading {file_info['format']} ({file_info['type']}) for {translation_key}")
                    response = self.session.get(file_url, timeout=60)
                    response.raise_for_status()
                    
                    if len(response.content) > 1000:  # Assume valid if > 1KB
                        # Create filename
                        safe_title = self.sanitize_filename(title.replace(' - ', '_').replace(' ', '_'))
                        type_suffix = f"_{file_info['type']}" if file_info['type'] != 'standard' else ""
                        filename = f"quranenc_{translation_key}_{safe_title}{type_suffix}.{file_info['format']}"
                        file_path = output_dir / filename
                        
                        # Save file
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        
                        file_size = file_path.stat().st_size
                        file_record = {
                            'filename': filename,
                            'format': file_info['format'],
                            'type': file_info['type'],
                            'size_bytes': file_size,
                            'source_url': file_url,
                            'download_success': True
                        }
                        metadata['files_downloaded'].append(file_record)
                        self.downloaded_files.append(str(file_path))
                        
                        logger.info(f"Downloaded {filename} ({file_size} bytes)")
                    else:
                        logger.warning(f"File too small, skipping: {file_url}")
                        
                except Exception as e:
                    logger.error(f"Failed to download {url_key} from {file_url}: {e}")
                    error_info = {
                        'url_key': url_key,
                        'url': file_url,
                        'error': str(e),
                        'translation_key': translation_key
                    }
                    metadata.setdefault('errors', []).append(error_info)
    
    def try_download_other_formats(self, translation_key: str, output_dir: Path, metadata: Dict, title: str):
        """Try to download other formats like XML, CSV for a translation"""
        formats_to_try = ['xml', 'csv', 'excel']
        
        for format_type in formats_to_try:
            # Common URL patterns for downloads
            download_urls = [
                f"{self.base_url}/en/home/download/{format_type}/{translation_key}",
                f"{self.base_url}/download/{format_type}/{translation_key}",
                f"{self.base_url}/files/{format_type}/{translation_key}.{format_type}",
            ]
            
            success = False
            for url in download_urls:
                try:
                    logger.debug(f"Trying download URL: {url}")
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200 and len(response.content) > 1000:  # Assume valid if > 1KB
                        # Determine file extension
                        ext_map = {'excel': 'xlsx', 'csv': 'csv', 'xml': 'xml'}
                        ext = ext_map.get(format_type, format_type)
                        
                        # Create filename
                        safe_title = self.sanitize_filename(title.replace(' - ', '_').replace(' ', '_'))
                        filename = f"quranenc_{translation_key}_{safe_title}_{format_type}.{ext}"
                        file_path = output_dir / filename
                        
                        # Save file
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        
                        file_size = file_path.stat().st_size
                        file_info = {
                            'filename': filename,
                            'format': format_type,
                            'size_bytes': file_size,
                            'source_url': url,
                            'download_success': True
                        }
                        metadata['files_downloaded'].append(file_info)
                        self.downloaded_files.append(str(file_path))
                        
                        logger.info(f"Downloaded {format_type}: {filename} ({file_size} bytes)")
                        success = True
                        break  # Success, don't try other URLs for this format
                        
                except Exception as e:
                    logger.debug(f"Failed to download from {url}: {e}")
                    continue
            
            if not success:
                logger.debug(f"No valid {format_type} download found for {translation_key}")
    
    def scrape_all_translations(self):
        """Main method to scrape all available translations"""
        logger.info("Starting comprehensive QuranEnc.com scrape...")
        
        # Get list of all translations
        translations = self.get_translations_list()
        if not translations:
            logger.error("No translations found. Exiting.")
            return
        
        self.metadata['total_translations'] = len(translations)
        
        # Process each translation
        for i, translation in enumerate(translations, 1):
            logger.info(f"Processing translation {i}/{len(translations)}")
            
            try:
                translation_metadata = self.download_translation_data(translation)
                self.metadata['translations'].append(translation_metadata)
                
                # Add delay between translations to be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to process translation {translation.get('key', 'unknown')}: {e}")
                error_info = {
                    'translation_key': translation.get('key', 'unknown'),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.metadata['errors'].append(error_info)
                self.failed_downloads.append(translation.get('key', 'unknown'))
        
        # Save metadata
        self.save_metadata()
        
        # Generate report
        self.generate_report()
    
    def save_metadata(self):
        """Save comprehensive metadata to JSON file"""
        self.metadata['total_files_downloaded'] = len(self.downloaded_files)
        self.metadata['scrape_completed'] = datetime.now().isoformat()
        
        metadata_file = self.base_dir / "metadata" / "quranenc_complete_metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"Metadata saved to: {metadata_file}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def generate_report(self):
        """Generate a comprehensive download report"""
        report = {
            'QuranEnc.com Comprehensive Scrape Report': {
                'Scrape Date': self.metadata['scrape_timestamp'],
                'Total Translations Found': self.metadata['total_translations'],
                'Total Files Downloaded': len(self.downloaded_files),
                'Failed Downloads': len(self.failed_downloads),
                'Success Rate': f"{((len(self.downloaded_files) - len(self.failed_downloads)) / max(1, len(self.downloaded_files))) * 100:.1f}%"
            },
            'Downloaded Files Summary': {},
            'Translation Coverage': {},
            'Errors': self.metadata['errors']
        }
        
        # Analyze downloaded files by format
        format_counts = {}
        for translation in self.metadata['translations']:
            for file_info in translation.get('files_downloaded', []):
                format_type = file_info.get('format', 'unknown')
                format_counts[format_type] = format_counts.get(format_type, 0) + 1
        
        report['Downloaded Files Summary'] = format_counts
        
        # Analyze language coverage
        language_counts = {}
        for translation in self.metadata['translations']:
            language = translation.get('language', 'unknown')
            language_counts[language] = language_counts.get(language, 0) + 1
        
        report['Translation Coverage'] = language_counts
        
        # Save report
        report_file = self.base_dir / "quranenc_download_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"Download report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        # Print summary
        logger.info("=== SCRAPE COMPLETED ===")
        logger.info(f"Translations processed: {self.metadata['total_translations']}")
        logger.info(f"Files downloaded: {len(self.downloaded_files)}")
        logger.info(f"Failed downloads: {len(self.failed_downloads)}")
        logger.info(f"Report saved to: {report_file}")

if __name__ == "__main__":
    # Set up base directory
    base_directory = Path(__file__).parent
    
    # Initialize and run scraper
    scraper = QuranEncScraper(base_directory)
    scraper.scrape_all_translations()