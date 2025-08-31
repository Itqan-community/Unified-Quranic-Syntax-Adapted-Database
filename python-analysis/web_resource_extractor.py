#!/usr/bin/env python3
"""
Web Resource Metadata Extractor

A comprehensive tool for extracting metadata from web pages containing downloadable resources.
Handles various download button scenarios, file formats, and associated metadata.

Features:
- Extracts file metadata (name, size, format, actual filename)
- Identifies associated person/author names from surrounding elements
- Handles different download button scenarios:
  * Single direct download links
  * Context menus with format selection
  * Separate buttons for different formats
- Comprehensive logging for full traceability
- Export to JSON/CSV for further analysis

Author: Generated for UQSAD Project
Date: 2025-08-31
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urljoin, urlparse
import re
import logging
from datetime import datetime
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ResourceMetadata:
    """Data class to store comprehensive resource metadata"""
    url: str
    page_title: str
    resource_name: str
    actual_filename: str
    file_extension: str
    file_size: str
    download_urls: List[str]
    available_formats: List[str]
    associated_person: str
    tags: List[str]
    description: str
    metadata: Dict[str, str]
    extraction_timestamp: str
    
    def to_dict(self):
        return asdict(self)


class WebResourceExtractor:
    """Main class for extracting web resource metadata"""
    
    def __init__(self, output_dir: str = "extracted_data", log_level: str = "INFO"):
        """
        Initialize the extractor
        
        Args:
            output_dir: Directory to save extracted data
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Session for consistent requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Patterns for different types of content
        self.download_patterns = [
            r'download',
            r'get',
            r'fetch',
            r'retrieve',
            r'save',
            r'export'
        ]
        
        self.format_patterns = [
            r'\.pdf', r'\.doc', r'\.docx', r'\.txt', r'\.rtf',
            r'\.xls', r'\.xlsx', r'\.csv',
            r'\.zip', r'\.rar', r'\.tar', r'\.gz',
            r'\.json', r'\.xml', r'\.html',
            r'\.sqlite', r'\.db', r'\.sql'
        ]
        
        self.person_indicators = [
            'author', 'by', 'creator', 'contributor', 'researcher',
            'scholar', 'writer', 'compiled', 'prepared', 'edited'
        ]

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self.logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            self.logger.info(f"Successfully parsed page with {len(soup.find_all())} elements")
            return soup
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    def find_download_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Find all potential download elements on the page
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of dictionaries containing download element info
        """
        download_elements = []
        
        # Strategy 1: Find direct download links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            
            # Check if it's a download link
            is_download = any(pattern in text for pattern in self.download_patterns)
            has_file_ext = any(re.search(pattern, href, re.IGNORECASE) for pattern in self.format_patterns)
            
            if is_download or has_file_ext:
                download_elements.append({
                    'element': link,
                    'type': 'direct_link',
                    'url': href,
                    'text': link.get_text(strip=True),
                    'attributes': dict(link.attrs)
                })
        
        # Strategy 2: Find download buttons
        for button in soup.find_all(['button', 'input'], type=['button', 'submit']):
            text = button.get_text(strip=True).lower()
            onclick = button.get('onclick', '')
            
            is_download = any(pattern in text or pattern in onclick for pattern in self.download_patterns)
            
            if is_download:
                download_elements.append({
                    'element': button,
                    'type': 'button',
                    'text': button.get_text(strip=True),
                    'onclick': onclick,
                    'attributes': dict(button.attrs)
                })
        
        # Strategy 3: Find elements with download-related classes/ids
        download_selectors = [
            '[class*="download"]', '[id*="download"]',
            '[class*="get"]', '[id*="get"]',
            '[data-download]', '[data-file]'
        ]
        
        for selector in download_selectors:
            for element in soup.select(selector):
                if element not in [de['element'] for de in download_elements]:
                    download_elements.append({
                        'element': element,
                        'type': 'css_selector',
                        'text': element.get_text(strip=True),
                        'attributes': dict(element.attrs)
                    })
        
        self.logger.info(f"Found {len(download_elements)} potential download elements")
        return download_elements

    def extract_file_formats(self, element, soup: BeautifulSoup) -> List[str]:
        """
        Extract available file formats from an element or its context
        
        Args:
            element: The download element
            soup: BeautifulSoup object of the page
            
        Returns:
            List of available formats
        """
        formats = []
        
        # Check the element itself
        text = element.get_text() if hasattr(element, 'get_text') else str(element)
        for pattern in self.format_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            formats.extend([match.lower() for match in matches])
        
        # Check parent and sibling elements
        if hasattr(element, 'parent'):
            parent = element.parent
            # Check siblings for format options
            for sibling in parent.find_all():
                sibling_text = sibling.get_text(strip=True).lower()
                for pattern in self.format_patterns:
                    matches = re.findall(pattern, sibling_text, re.IGNORECASE)
                    formats.extend([match.lower() for match in matches])
        
        # Look for dropdown menus or format lists nearby
        nearby_elements = soup.find_all(lambda tag: any(
            fmt in tag.get_text().lower() for fmt in ['pdf', 'doc', 'excel', 'csv', 'json', 'xml']
        ))
        
        for elem in nearby_elements:
            elem_text = elem.get_text(strip=True).lower()
            for pattern in self.format_patterns:
                matches = re.findall(pattern, elem_text, re.IGNORECASE)
                formats.extend([match.lower() for match in matches])
        
        return list(set(formats))  # Remove duplicates

    def find_associated_person(self, element, soup: BeautifulSoup) -> str:
        """
        Find person/author name associated with the resource
        
        Args:
            element: The download element
            soup: BeautifulSoup object of the page
            
        Returns:
            Associated person name or empty string
        """
        person_name = ""
        
        # Strategy 1: Check nearby elements for person indicators
        if hasattr(element, 'parent'):
            # Check parent and siblings
            search_area = element.parent
            text = search_area.get_text() if hasattr(search_area, 'get_text') else str(search_area)
            
            for indicator in self.person_indicators:
                pattern = rf'{indicator}[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    person_name = matches[0]
                    break
        
        # Strategy 2: Look for common person name patterns in the page
        if not person_name:
            # Look for patterns like "Dr. Name", "Prof. Name", etc.
            title_patterns = [
                r'(?:Dr\.?|Prof\.?|Mr\.?|Ms\.?|Mrs\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*(?:Ph\.?D\.?|M\.?A\.?|B\.?A\.?)'
            ]
            
            page_text = soup.get_text()
            for pattern in title_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    person_name = matches[0]
                    break
        
        # Strategy 3: Look in metadata tags
        if not person_name:
            author_meta = soup.find('meta', {'name': 'author'})
            if author_meta:
                person_name = author_meta.get('content', '')
        
        self.logger.debug(f"Found associated person: {person_name}")
        return person_name.strip()

    def extract_tags_and_metadata(self, soup: BeautifulSoup) -> Tuple[List[str], Dict[str, str]]:
        """
        Extract tags and metadata from the page
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Tuple of (tags list, metadata dict)
        """
        tags = []
        metadata = {}
        
        # Extract from meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '')
            property_name = meta.get('property', '')
            content = meta.get('content', '')
            
            if content:
                if name:
                    metadata[name] = content
                    if name in ['keywords', 'tags']:
                        tags.extend([tag.strip() for tag in content.split(',')])
                elif property_name:
                    metadata[property_name] = content
        
        # Look for tag-like elements
        tag_selectors = [
            '.tag', '.tags', '.category', '.categories',
            '[class*="tag"]', '[class*="category"]'
        ]
        
        for selector in tag_selectors:
            elements = soup.select(selector)
            for elem in elements:
                tag_text = elem.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
        
        # Extract structured data (JSON-LD, microdata)
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld:
            try:
                ld_data = json.loads(json_ld.string)
                metadata['json_ld'] = ld_data
                if isinstance(ld_data, dict) and 'keywords' in ld_data:
                    if isinstance(ld_data['keywords'], list):
                        tags.extend(ld_data['keywords'])
                    else:
                        tags.extend([tag.strip() for tag in str(ld_data['keywords']).split(',')])
            except json.JSONDecodeError:
                pass
        
        tags = list(set([tag for tag in tags if tag]))  # Remove duplicates and empty tags
        self.logger.debug(f"Extracted {len(tags)} tags and {len(metadata)} metadata entries")
        
        return tags, metadata

    def extract_resource_metadata(self, url: str) -> Optional[ResourceMetadata]:
        """
        Extract comprehensive metadata from a resource page
        
        Args:
            url: URL of the resource page
            
        Returns:
            ResourceMetadata object or None if extraction failed
        """
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # Basic page info
            page_title = soup.find('title')
            page_title = page_title.get_text(strip=True) if page_title else "Unknown"
            
            # Find download elements
            download_elements = self.find_download_elements(soup)
            if not download_elements:
                self.logger.warning(f"No download elements found on {url}")
                return None
            
            # Process the first/primary download element
            primary_element = download_elements[0]['element']
            
            # Extract file formats
            formats = self.extract_file_formats(primary_element, soup)
            
            # Extract download URLs
            download_urls = []
            for de in download_elements:
                if de.get('url'):
                    full_url = urljoin(url, de['url'])
                    download_urls.append(full_url)
            
            # Find associated person
            person = self.find_associated_person(primary_element, soup)
            
            # Extract tags and metadata
            tags, metadata = self.extract_tags_and_metadata(soup)
            
            # Try to determine resource name
            resource_name = ""
            if download_elements:
                resource_name = download_elements[0].get('text', '')
                if not resource_name and 'title' in download_elements[0].get('attributes', {}):
                    resource_name = download_elements[0]['attributes']['title']
            
            if not resource_name:
                resource_name = page_title
            
            # Try to extract actual filename from URL or headers
            actual_filename = ""
            if download_urls:
                try:
                    head_response = self.session.head(download_urls[0], timeout=10)
                    content_disp = head_response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disp:
                        actual_filename = content_disp.split('filename=')[1].strip('"\'')
                    else:
                        actual_filename = Path(urlparse(download_urls[0]).path).name
                except:
                    actual_filename = Path(urlparse(download_urls[0]).path).name if download_urls else ""
            
            # Determine file extension
            file_extension = ""
            if actual_filename:
                file_extension = Path(actual_filename).suffix
            elif formats:
                file_extension = formats[0] if not formats[0].startswith('.') else formats[0]
            
            # Extract description
            description = ""
            desc_selectors = ['.description', '.summary', '.abstract', '[name="description"]']
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    break
            
            # Create ResourceMetadata object
            resource_metadata = ResourceMetadata(
                url=url,
                page_title=page_title,
                resource_name=resource_name,
                actual_filename=actual_filename,
                file_extension=file_extension,
                file_size="",  # Would need to make request to get this
                download_urls=download_urls,
                available_formats=formats,
                associated_person=person,
                tags=tags,
                description=description,
                metadata=metadata,
                extraction_timestamp=datetime.now().isoformat()
            )
            
            self.logger.info(f"Successfully extracted metadata for {url}")
            return resource_metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {url}: {e}")
            return None

    def extract_multiple_resources(self, urls: List[str]) -> List[ResourceMetadata]:
        """
        Extract metadata from multiple resource URLs
        
        Args:
            urls: List of URLs to process
            
        Returns:
            List of ResourceMetadata objects
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing {i}/{len(urls)}: {url}")
            
            metadata = self.extract_resource_metadata(url)
            if metadata:
                results.append(metadata)
            
            # Be respectful to servers
            time.sleep(1)
        
        self.logger.info(f"Successfully extracted metadata from {len(results)}/{len(urls)} URLs")
        return results

    def save_to_json(self, results: List[ResourceMetadata], filename: str = None):
        """Save results to JSON file"""
        if not filename:
            filename = f"resource_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([result.to_dict() for result in results], f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {filepath}")

    def save_to_csv(self, results: List[ResourceMetadata], filename: str = None):
        """Save results to CSV file"""
        if not results:
            return
        
        if not filename:
            filename = f"resource_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.output_dir / filename
        
        # Flatten the data for CSV
        csv_data = []
        for result in results:
            row = result.to_dict()
            # Convert lists and dicts to strings for CSV
            row['download_urls'] = '; '.join(row['download_urls'])
            row['available_formats'] = '; '.join(row['available_formats'])
            row['tags'] = '; '.join(row['tags'])
            row['metadata'] = json.dumps(row['metadata'])
            csv_data.append(row)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
        
        self.logger.info(f"Results saved to {filepath}")


def main():
    """
    Example usage of the WebResourceExtractor
    """
    # Initialize extractor
    extractor = WebResourceExtractor(output_dir="extracted_data", log_level="INFO")
    
    # Example URLs (replace with your actual URLs)
    test_urls = [
        "https://example.com/resource1",
        "https://example.com/resource2"
    ]
    
    # Extract metadata
    results = extractor.extract_multiple_resources(test_urls)
    
    # Save results
    if results:
        extractor.save_to_json(results)
        extractor.save_to_csv(results)
        print(f"Extracted metadata from {len(results)} resources")
    else:
        print("No metadata extracted")


if __name__ == "__main__":
    main()