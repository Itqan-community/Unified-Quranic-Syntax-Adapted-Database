# Web Resource Metadata Extractor

A comprehensive Python tool for extracting detailed metadata from web pages containing downloadable resources. Designed specifically for the UQSAD (Unified Quranic Syntax Adapted Database) project to ensure 100% transparent and traceable data extraction.

## 🎯 Purpose

This tool addresses the need for comprehensive metadata extraction from web resources while maintaining full visibility into the scraping logic. Unlike AI-based extraction, this provides:

- **100% transparent logic** - Every extraction step is visible in code
- **No hallucination risk** - Only extracts what's actually present
- **Complete traceability** - Full logging of all extraction steps
- **Customizable patterns** - Adaptable to different website structures

## 🚀 Features

### Core Extraction Capabilities
- **Multi-format Download Detection**: Handles various download button scenarios
  - Direct download links
  - Context menus with format selection
  - Separate buttons for different formats
  - JavaScript-triggered downloads
- **Comprehensive Metadata Extraction**:
  - Resource names (display vs actual filename)
  - Associated person/author names
  - File formats and extensions
  - Tags and categories
  - Descriptions and abstracts
  - Complete URL mapping
- **Smart Person Detection**: Finds associated authors/creators from:
  - Nearby HTML elements
  - Meta tags
  - Structured data
  - Pattern matching in text

### Download Button Scenarios Supported

#### Scenario 1: Direct Download Links
```html
<a href="document.pdf">Download PDF</a>
```

#### Scenario 2: Context Menu Downloads
```html
<button onclick="showFormats()">Download</button>
<!-- Opens menu with format options -->
```

#### Scenario 3: Multiple Format Buttons
```html
<a href="doc.pdf" class="download-btn">PDF</a>
<a href="doc.docx" class="download-btn">Word</a>
<a href="doc.txt" class="download-btn">Text</a>
```

#### Scenario 4: JavaScript-triggered Downloads
```html
<button data-download-url="resource.zip" onclick="downloadFile()">Get File</button>
```

## 📋 Requirements

### Dependencies
Install required packages:
```bash
pip install -r requirements.txt
```

### Core Dependencies
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML processing
- `pandas` - Data handling (optional)

## 🔧 Installation

1. **Clone or download** the repository
2. **Navigate** to the `python-analysis` directory
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Basic Usage

```python
from web_resource_extractor import WebResourceExtractor

# Initialize extractor
extractor = WebResourceExtractor(
    output_dir="my_extractions",
    log_level="INFO"
)

# Extract from single URL
metadata = extractor.extract_resource_metadata("https://example.com/resource")

# Extract from multiple URLs
urls = ["https://site1.com/resource", "https://site2.com/resource"]
results = extractor.extract_multiple_resources(urls)

# Save results
extractor.save_to_json(results, "my_results.json")
extractor.save_to_csv(results, "my_results.csv")
```

### Advanced Configuration

```python
# Custom configuration for specific sites
extractor = WebResourceExtractor()

# Add Arabic download patterns
extractor.download_patterns.extend(['تحميل', 'تنزيل', 'حفظ'])

# Add Islamic scholar indicators
extractor.person_indicators.extend(['الشيخ', 'الدكتور', 'الإمام'])

# Add custom file formats
extractor.format_patterns.extend([r'\.epub', r'\.mobi'])
```

### Using Configuration File

```python
import json
from web_resource_extractor import WebResourceExtractor

# Load custom config
with open('config.json', 'r') as f:
    config = json.load(f)

extractor = WebResourceExtractor()
# Apply configuration...
```

## 📊 Output Data Structure

### ResourceMetadata Class
```python
@dataclass
class ResourceMetadata:
    url: str                    # Source page URL
    page_title: str            # Page title
    resource_name: str         # Display name of resource
    actual_filename: str       # Actual filename when downloaded
    file_extension: str        # File extension
    file_size: str            # File size (if available)
    download_urls: List[str]   # All download URLs found
    available_formats: List[str] # Available file formats
    associated_person: str     # Author/creator name
    tags: List[str]           # Tags and categories
    description: str          # Description/abstract
    metadata: Dict[str, str]  # Additional metadata
    extraction_timestamp: str # When extracted
```

### JSON Output Example
```json
{
  "url": "https://example.com/resource",
  "page_title": "Important Document",
  "resource_name": "Research Paper on Quranic Studies",
  "actual_filename": "quran_research_2024.pdf",
  "file_extension": ".pdf",
  "download_urls": ["https://example.com/download/123"],
  "available_formats": ["pdf", "docx", "epub"],
  "associated_person": "Dr. Ahmed Al-Scholar",
  "tags": ["quran", "research", "islamic-studies"],
  "description": "Comprehensive analysis of...",
  "metadata": {
    "author": "Dr. Ahmed Al-Scholar",
    "keywords": "quran, research",
    "dc.type": "text"
  },
  "extraction_timestamp": "2025-08-31T10:30:00"
}
```

## 🔍 Extraction Strategies

### 1. Download Element Detection
- **CSS Selectors**: `[class*="download"]`, `.btn-download`, etc.
- **Text Patterns**: "download", "get", "fetch", "retrieve"
- **URL Patterns**: File extensions in hrefs
- **JavaScript Events**: onclick handlers with download logic

### 2. Person/Author Extraction
- **Proximity Search**: Searches near download elements
- **Meta Tags**: `<meta name="author">`, etc.
- **Structured Data**: JSON-LD, microdata
- **Pattern Matching**: "By Author Name", "Dr. Name", etc.

### 3. Format Detection
- **URL Analysis**: File extensions in links
- **HTTP Headers**: Content-Disposition headers
- **Context Analysis**: Format mentions near downloads
- **Menu Options**: Dropdown/context menu items

### 4. Metadata Collection
- **Meta Tags**: Open Graph, Twitter Cards, Dublin Core
- **Structured Data**: JSON-LD, RDFa, microdata
- **HTML Elements**: Description, summary, abstract elements
- **Tag Elements**: Category, keyword, topic elements

## 🛠️ Customization

### Site-Specific Configuration
Add custom patterns for specific sites in `config.json`:

```json
{
  "site_specific_configs": {
    "yoursite.com": {
      "download_patterns": ["custom-download", "get-file"],
      "person_selectors": [".author-box", ".contributor-name"],
      "description_selectors": [".resource-summary"]
    }
  }
}
```

### Custom CSS Selectors
```python
# Add custom selectors
extractor.download_selectors.extend([
    '.my-custom-download-btn',
    '[data-resource-id]'
])
```

## 🔧 Configuration Options

### Extraction Settings
- `request_timeout`: HTTP request timeout
- `request_delay`: Delay between requests
- `max_retries`: Maximum retry attempts
- `output_directory`: Where to save results

### Pattern Customization
- `download_patterns`: Text patterns indicating downloads
- `file_format_patterns`: Regex patterns for file extensions
- `person_indicators`: Text patterns indicating person names

### Output Formats
- **JSON**: Structured data with full metadata
- **CSV**: Flattened data suitable for analysis
- **Custom**: Extend for additional formats

## 📝 Logging and Debugging

### Log Levels
- `DEBUG`: Detailed extraction steps
- `INFO`: High-level progress
- `WARNING`: Potential issues
- `ERROR`: Extraction failures

### Log Output
```
2025-08-31 10:30:00 - INFO - Fetching page: https://example.com
2025-08-31 10:30:01 - INFO - Successfully parsed page with 245 elements
2025-08-31 10:30:01 - INFO - Found 3 potential download elements
2025-08-31 10:30:01 - DEBUG - Found associated person: Dr. Ahmed Al-Scholar
2025-08-31 10:30:02 - INFO - Successfully extracted metadata for https://example.com
```

## 🎯 Use Cases

### Research Data Collection
- Academic papers and publications
- Research datasets
- Conference proceedings
- Thesis and dissertation collections

### Digital Archive Analysis
- Historical document collections
- Manuscript repositories
- Library digital collections
- Cultural heritage resources

### Content Audit and Analysis
- Website resource inventories
- Metadata quality assessment
- Accessibility compliance checking
- SEO content analysis

## 🚫 Ethical Considerations

### Respectful Scraping
- Built-in delays between requests
- Respects robots.txt (manual check recommended)
- No aggressive crawling
- Minimal server load

### Data Privacy
- No personal data collection beyond public metadata
- Transparent extraction logic
- User-controlled data retention
- Opt-out capabilities where applicable

## 🔬 Testing and Examples

### Run Examples
```bash
python example_usage.py
```

### Interactive Mode
```python
python -c "from example_usage import interactive_mode; interactive_mode()"
```

### Test with Your URLs
1. Modify `example_usage.py`
2. Add your URLs to the examples
3. Run and examine the output
4. Adjust configuration as needed

## 🐛 Troubleshooting

### Common Issues

#### No Download Elements Found
- Check if the site uses JavaScript for downloads
- Verify CSS selectors in config
- Add custom patterns for the specific site

#### Incorrect Person Names
- Adjust `person_indicators` patterns
- Add site-specific selectors
- Check proximity search radius

#### Missing File Formats
- Enable `file_format_patterns` debugging
- Check if formats are in JavaScript/AJAX calls
- Add custom format detection patterns

### Debug Mode
```python
extractor = WebResourceExtractor(log_level="DEBUG")
```

## 📈 Performance Optimization

### Batch Processing
- Process multiple URLs efficiently
- Built-in rate limiting
- Session reuse for better performance

### Memory Management
- Streaming for large datasets
- Configurable output batching
- Cleanup of temporary data

## 🔄 Updates and Maintenance

### Version History
- v1.0: Initial release with core functionality
- Future: Enhanced JavaScript handling, more formats

### Contributing
1. Test with your specific use cases
2. Submit issues for bugs or feature requests
3. Provide sample URLs for testing
4. Suggest pattern improvements

## 📧 Support

For issues specific to UQSAD project requirements:
1. Check the logs for detailed error messages
2. Test with the provided examples
3. Verify your URLs are publicly accessible
4. Review configuration for site-specific needs

---

**Note**: This tool is designed for legitimate research and analysis purposes. Always respect website terms of service and applicable laws when extracting data.