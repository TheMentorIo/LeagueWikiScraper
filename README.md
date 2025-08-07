# League of Legends Wiki Scraper

A comprehensive Python toolkit for scraping and downloading League of Legends data from the official wiki, including champion information, skins, images, audio files, and skill icons.

## 🎯 Features

### Core Functionality
- **Champion Data Scraping**: Extract all champion names and basic information
- **Skin/Cosmetics Scraping**: Download all champion skins and cosmetics data
- **Image Downloading**: Bulk download champion splash arts, loading screens, icons, and tiles
- **Audio File Downloading**: Extract and download champion voice lines and quotes
- **Skill Icon Scraping**: Download all ability icons for each champion
- **Data Organization**: Automatically organize downloaded content into structured folders

### Advanced Features
- **Smart Caching**: Only download files that have changed (hash-based comparison)
- **Multithreaded Downloads**: Fast parallel downloading with configurable thread limits
- **CSV Data Export**: Export all scraped data to CSV files for analysis
- **Error Logging**: Comprehensive error tracking and logging
- **File Sanitization**: Safe filename handling for Windows compatibility

## 📁 Project Structure

```
LeagueWikiScraper/
├── champion_scraper.py      # Core champion data extraction
├── cosmetics_scraper.py     # Skin and cosmetics scraping
├── champion_image_scraper.py # Image metadata scraping
├── image_downloader.py      # Bulk image downloading
├── auido_downloader.py      # Audio file downloading
├── skill_scraper.py         # Skill icon scraping
├── readSkinData.py          # Data processing and validation
├── boardermaker.py          # Image border processing utility
├── utils.py                 # Shared utility functions
└── data/                   # Downloaded content
    ├── champion_names.csv
    ├── cosmetic_links.csv
    ├── champion_images.csv
    └── [Champion Name]/
        ├── skins/
        │   └── [Skin Name]/
        │       ├── Splashes/
        │       ├── Loading/
        │       ├── Circles/
        │       ├── Squares/
        │       ├── Centered/
        │       └── Tiles/
        ├── skills/
        │   ├── passive/
        │   ├── q/
        │   ├── w/
        │   ├── e/
        │   └── r/
        ├── audio/
        │   └── [Category]/
        │       └── [Subcategory]/
        ├── info.csv
        ├── skills.csv
        └── audio_mapping.csv
```

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Dependencies
```bash
pip install requests beautifulsoup4 tqdm pillow
```

### Quick Setup
```bash
git clone https://github.com/yourusername/LeagueWikiScraper.git
cd LeagueWikiScraper
pip install -r requirements.txt
```

## 📖 Usage

### Basic Usage

#### 1. Scrape Champion Data
```python
from champion_scraper import ChampionScraper

scraper = ChampionScraper()
champions = scraper.get_champion_list()
scraper.save_champions_to_csv()
```

#### 2. Scrape Cosmetics/Skins
```python
from cosmetics_scraper import CosmeticsScraper

cosmetics_scraper = CosmeticsScraper()
cosmetics_links = cosmetics_scraper.scrape_all_cosmetics(champions)
cosmetics_scraper.save_cosmetics_to_csv()
```

#### 3. Scrape Image Metadata
```python
from champion_image_scraper import ChampionImageScraper

image_scraper = ChampionImageScraper()
champion_results = image_scraper.scrape_all_champions(cosmetics_links)
image_scraper.save_images_to_csv()
```

#### 4. Download Images
```python
from image_downloader import ImageDownloader

downloader = ImageDownloader()
downloader.download_all_images(champion_results)
```

#### 5. Download Audio Files
```python
from auido_downloader import AudioDownloader

audio_downloader = AudioDownloader(champions)
audio_downloader.run()
```

#### 6. Scrape Skill Icons
```python
from skill_scraper import SkillScraper

skill_scraper = SkillScraper(champions)
skill_scraper.run()
```

### Complete Pipeline Example

```python
import os
from champion_scraper import ChampionScraper
from cosmetics_scraper import CosmeticsScraper
from champion_image_scraper import ChampionImageScraper
from image_downloader import ImageDownloader
from auido_downloader import AudioDownloader
from skill_scraper import SkillScraper

# Initialize scrapers
champion_scraper = ChampionScraper()
cosmetics_scraper = CosmeticsScraper()
image_scraper = ChampionImageScraper()
image_downloader = ImageDownloader()
audio_downloader = AudioDownloader()
skill_scraper = SkillScraper()

# Check for existing data or scrape new data
csv_path = os.path.join("data", "champion_names.csv")
if os.path.exists(csv_path):
    print("📁 Using existing champion data...")
    champions = champion_scraper.read_champions_from_csv(csv_path)
else:
    print("🌐 Scraping champion data...")
    champions = champion_scraper.get_champion_list()
    champion_scraper.save_champions_to_csv()

# Similar pattern for cosmetics, images, etc.
# Each component checks for existing CSV files first
```

## 🔧 Configuration

### Threading Configuration
Most scrapers support configurable thread limits:

```python
# Example: Increase thread count for faster downloads
image_downloader = ImageDownloader(max_threads=20)
audio_downloader = AudioDownloader(max_threads=15)
```

### Output Directory
Customize output directory:

```python
scraper = ChampionScraper(output_dir="custom_data_folder")
```

## 📊 Data Output

### CSV Files Generated
- `champion_names.csv`: List of all champions
- `cosmetic_links.csv`: Champion skins and image URLs
- `champion_images.csv`: Detailed image metadata
- `[Champion]/info.csv`: Champion information
- `[Champion]/skills.csv`: Skill data and icon mappings
- `[Champion]/audio_mapping.csv`: Audio file mappings

### File Organization
```
data/
├── Ahri/
│   ├── skins/
│   │   ├── Classic/
│   │   │   ├── Splashes/
│   │   │   ├── Loading/
│   │   │   └── Circles/
│   │   └── Spirit Blossom/
│   ├── skills/
│   │   ├── passive/
│   │   ├── q/
│   │   ├── w/
│   │   ├── e/
│   │   └── r/
│   ├── audio/
│   │   ├── Movement/
│   │   ├── Combat/
│   │   └── Jokes/
│   ├── info.csv
│   ├── skills.csv
│   └── audio_mapping.csv
```

## 🛠️ Utility Scripts

### Data Processing (`readSkinData.py`)
```python
from readSkinData import SkinDataProcessor

processor = SkinDataProcessor()
processor.check_art_cat()  # Check missing art categories
processor.check_skill()    # Check missing skill icons
```

### Image Processing (`boardermaker.py`)
```python
# Add borders to images
from boardermaker import add_border_to_image
```

## ⚡ Performance Features

### Smart Caching
- Files are only downloaded if they've changed (SHA256 hash comparison)
- Saves bandwidth and time on subsequent runs

### Multithreading
- Configurable thread pools for parallel downloads
- Progress bars with `tqdm` for real-time feedback

### Error Handling
- Comprehensive error logging
- Graceful failure handling
- Retry mechanisms for network issues

## 🔍 Data Validation

The `readSkinData.py` script provides tools to:
- Check for missing art categories per skin
- Validate skill icon completeness
- Repair file naming issues
- Generate summary reports

## 📝 Logging

All scrapers include comprehensive logging:
- Download progress with file counts
- Error tracking with timestamps
- Success/failure statistics
- Network timeout handling

### Common Issues

1. **Network Timeouts**: Increase timeout values in the scraper classes
2. **Missing Files**: Run data validation scripts to check for missing content
3. **Permission Errors**: Ensure write permissions to the output directory
4. **Memory Issues**: Reduce thread count for large downloads
