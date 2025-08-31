# Unified Quranic Syntax Adapted Database - UQSAD 📖

A comprehensive collection and analysis toolkit for multiple Quran Mushaf databases, providing systematic exploration, comparison, and statistical analysis of different Quranic text layouts and publishers.

## What This Repository Contains

The **Unified Quranic Syntax Adapted Database - UQSAD** project contains **11 different Mushaf databases** representing various Quranic text layouts, scripts, and publishers. Each database stores the complete Quran text with detailed page-by-page and line-by-line organization.

### Database Collection

Our repository includes databases from:

- **Indo-Pak Script** (13, 15, and 16-line layouts)
- **QPC (Quran Printing Complex)** versions (v1, v2, v4 with Tajweed)
- **Uthmani Script** (traditional layout)
- **Digital Khatt** (modern digital font)
- **Nastaleeq Script** (elegant calligraphic style)
- **Various Publishers**: QPC, Taj Company, Qudratullah

## Repository Structure

This repository is organized into specialized directories for different types of analysis and data storage:

```
_UQSAD/
├── 📁 data/                      # Data storage directory
│   ├── 📁 Mushafs/              # Mushaf database files
│   │   ├── 01-indopak-13-lines-layout-qudratullah.db/
│   │   ├── 02-qpc-v1-15-lines.db/
│   │   ├── 03-uthmani-15-lines.db/
│   │   ├── 04-digital-khatt-15-lines.db/
│   │   ├── 05-indopak-13-lines-taj-company.db/
│   │   ├── 06-qpc-hafs-15-lines.db/
│   │   ├── 07-qpc-nastaleeq-15-lines.db/
│   │   ├── 08-qpc-v2-15-lines.db/
│   │   ├── 09-qudratullah-indopak-15-lines.db/
│   │   ├── 10-taj-indopak-16-lines.db/
│   │   └── 11-qpc-v4-tajweed-15-lines.db/
│   └── ...                      # Other data files
├── 📁 r-analysis/               # R-based analysis tools
│   ├── Main R Notebook.Rmd
│   ├── Main R Notebook.nb.html
│   ├── Mushaf Statistics Analysis.Rmd
│   └── Mushaf Statistics Analysis.nb.html
├── 📁 python-analysis/          # Python-based analysis tools (ready for implementation)
├── 📁 docs/                     # Documentation files (ready for use)
├── 📄 README.md                 # Project documentation
├── 📄 Quran-Hafs-Mushafs-References.xlsx  # Reference data
├── 📄 Unified-Quranic-Syntax-Adapted-Database-UQSAD.Rproj  # R project file
├── 🔒 renv/                     # R environment management
└── 🔒 renv.lock                 # R dependency lock file
```

### 📁 Directory Organization

#### `data/`
Contains all database files and datasets:
- **`Mushafs/`**: SQLite databases with detailed page layouts, word positioning, and Quranic text organization
- Additional data files and references

#### `r-analysis/`
R-based analysis notebooks and outputs:
- Statistical analysis and exploration scripts
- Generated HTML reports
- Database comparison tools

#### `python-analysis/`
Ready for Python-based analysis implementation:
- Data science and machine learning analysis
- Alternative statistical approaches
- Visualization tools

#### `docs/`
Documentation and additional resources:
- Technical documentation
- Research papers and references
- User guides

### 📊 Analysis Notebooks

#### 1. Main R Notebook ([View Full Notebook](./r-analysis/Main%20R%20Notebook.Rmd))

**Purpose**: Core database exploration and structure analysis

**What it does**:
- Connects to all 11 Mushaf databases systematically
- Explores database schemas and table structures  
- Extracts sample data from every table
- Performs comparative analysis across databases
- Provides comprehensive database connection management

**Key Features**:
- **Database Discovery**: Automatically detects and lists all tables in each database
- **Schema Analysis**: Uses SQLite PRAGMA commands to understand table structures
- **Safe Connections**: Implements error handling to prevent crashes from corrupted files
- **Data Sampling**: Shows first 5 rows from every table for content preview
- **Row Counting**: Compares data volume across different Mushaf versions





#### 2. Mushaf Statistics Analysis ([View Full Notebook](./r-analysis/Mushaf%20Statistics%20Analysis.Rmd))

**Purpose**: Deep statistical analysis and comparative metrics

**What it does**:
- Calculates total word counts using multiple verification methods
- Analyzes page-by-page word distributions
- Maps Surahs to their corresponding page numbers
- Compares layout efficiency across different scripts
- Generates comprehensive statistical reports

**Algorithms Included**:

1. **Word Counting Algorithm**
   - **Method 1**: Quick estimation using maximum `last_word_id`
   - **Method 2**: Precise calculation summing word ranges per line
   - Cross-validation between methods for accuracy

2. **Page Analysis Algorithm**
   - Calculates words per page using `(last_word_id - first_word_id + 1)`
   - Handles duplicate entries with `DISTINCT` queries
   - Generates min/max/average statistics

3. **Layout Comparison Algorithm**
   - Groups databases by lines per page (13, 15, 16 lines)
   - Compares script types (Indo-Pak, Uthmani, Nastaleeq)
   - Analyzes publisher differences

4. **Surah Mapping Algorithm**
   - Uses `line_type = 'surah_name'` for accurate detection
   - Handles duplicate surah markers in some databases
   - Creates start/end page ranges for each Surah

**Statistical Outputs**:
- Total words, pages, lines, and Surahs per database
- Words per page distribution analysis
- Cross-database consistency verification
- Layout efficiency comparisons

## Key Metrics Analyzed

### 📊 Quantitative Analysis
- **Total Words**: Complete word count for each Mushaf
- **Page Counts**: Total pages in each layout
- **Line Counts**: Total lines across all pages
- **Surah Distribution**: How Surahs are spread across pages

### 📏 Layout Analysis  
- **Words per Page**: Statistical distribution (min, max, average, median)
- **Lines per Page**: Comparison between 13, 15, and 16-line layouts
- **Script Efficiency**: How different scripts affect page count
- **Publisher Variations**: Differences between QPC, Taj, and Qudratullah

### 📖 Content Organization
- **Surah-to-Page Mapping**: Which Surahs appear on which pages
- **Page Range Analysis**: How many pages each Surah spans
- **Cross-Database Consistency**: Variations in organization between publishers

## Technical Implementation

### Database Structure
Each Mushaf database contains:
- **`pages` table**: Line-by-line text with word ID ranges
- **Word positioning**: `first_word_id` and `last_word_id` for each line
- **Page organization**: Page numbers and line types
- **Metadata**: Surah numbers, verse information

### Analysis Approach
- **Systematic Processing**: Each database is analyzed using consistent methods
- **Error Handling**: Robust error management for missing or corrupted data
- **Multiple Verification**: Cross-checking results using different calculation methods
- **Comprehensive Coverage**: Every table in every database is analyzed

### Dependencies
- **R Language**: Statistical computing environment
- **DBI & RSQLite**: Database connectivity and SQL operations
- **dplyr**: Data manipulation and transformation
- **Visualization**: ggplot2 for charts and graphs

## Key Insights

### Unified Schema

<img width="1071" height="331" alt="image" src="https://github.com/user-attachments/assets/a7579576-951a-42e1-a73f-2f28ebf54b5b" />

### Databases Configuration

<img width="2020" height="1016" alt="image" src="https://github.com/user-attachments/assets/575d8665-ff74-479f-8f58-324a5ffd7b21" />

### Databases Simple Discovery

<img width="1062" height="430" alt="image" src="https://github.com/user-attachments/assets/a9ed0544-3fc7-4aee-b62d-fa4cf38333fb" />

### Databases Inclusive Statistics Copmaprison
<img width="1944" height="817" alt="image" src="https://github.com/user-attachments/assets/143d53f0-6159-4ec5-bc66-6a868fdc2315" />

### Data Features Statistical Visualization

<img width="3400" height="909" alt="image" src="https://github.com/user-attachments/assets/f7e04df7-f918-471f-8ee4-05c1a7cfac99" />

## Getting Started

1. **Prerequisites**: Install R and required packages
   ```r
   install.packages(c("DBI", "RSQLite", "dplyr", "purrr", "stringr", "knitr", "tibble"))
   ```

2. **Run Analysis**: Open either notebook in RStudio
   - For exploration: [Main R Notebook.Rmd](./r-analysis/Main%20R%20Notebook.Rmd)
   - For statistics: [Mushaf Statistics Analysis.Rmd](./r-analysis/Mushaf%20Statistics%20Analysis.Rmd)

3. **View Results**: Generated HTML reports provide interactive analysis results

## Research Applications

This database collection enables research in:
- **Quranic Text Analysis**: Comparative study of different Mushaf layouts
- **Typography Studies**: Analysis of different Arabic scripts and fonts
- **Layout Optimization**: Understanding efficiency of different page arrangements
- **Digital Humanities**: Computational analysis of religious texts
- **Publishing Standards**: Comparison between different Quran publishing houses

## Dataset Comparison Inventory

We are creating systematic comparisons between various datasets to thoroughly inventory the pieces of information uploaded by different organizations. This comparative analysis helps identify unique features, commonalities, and variations across Mushaf layouts.

### QUL Mushafs Layout Mapping Data

| Comparison Aspect | Value | Description |
|-------------------|-------|-------------|
| **Line Data** | `first_word_id`, `last_word_id` | Indicates which words are in each line as per each Mushaf |
| **Ayah Data** | `line_type`, `page_number` | Shows how ayahs are distributed over lines per each Mushaf |

The database schema provides comprehensive mapping through key columns:
- **`first_word_id`**: Starting word identifier for each line
- **`last_word_id`**: Ending word identifier for each line  
- **`page_number`**: Page location within each Mushaf
- **`line_type`**: Content type classification (text, surah_name, etc.)

This structured approach enables precise cross-database comparisons and statistical analysis of different Mushaf layouts and publishing approaches.

## Data Quality

All databases contain:
- ✅ Complete Quranic text (6,236 verses across 114 Surahs)
- ✅ Accurate word positioning and page layouts
- ✅ Proper encoding for Arabic text
- ✅ Consistent database schemas
- ✅ Verified word counts and page numbers

---

**Note**: This is a research and educational project. All Quranic text databases are provided for academic study and comparative analysis purposes.
