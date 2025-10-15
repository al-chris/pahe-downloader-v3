# Pahe Downloader

A Flask-based web application for downloading anime episodes from animepahe.si. This tool allows you to select and download multiple episodes in 720p quality for personal use.

## Features

- Web interface for easy anime URL input
- Automatic episode detection and selection
- Downloads episodes in 720p quality
- Concurrent downloads for faster processing
- Zipped output for easy file management
- Bypasses site protections using Selenium

## Installation

### Prerequisites

- Python 3.14 or higher
- Chrome browser (for Selenium WebDriver)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/al-chris/pahe-downloader.git
   cd pahe-downloader
   ```

2. Install dependencies using uv (recommended):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

## Usage

1. Run the application:
   ```bash
   uv run main.py
   ```
   Or:
   ```bash
   python main.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000/`

3. Paste the anime URL from animepahe.si (e.g., `https://animepahe.ru/anime/anime-name`)

4. Select the episodes you want to download (all are pre-selected by default)

5. Click "Download Selected Episodes" to start the download process

6. The app will download the selected episodes concurrently and provide a ZIP file for download

## How It Works

- The app uses Selenium to scrape episode information and bypass DDoS-Guard protections
- Downloads are handled via direct links with decryption
- Files are temporarily stored in the `downloads/` directory and zipped for delivery

## Disclaimer

This application is intended for personal use only. Downloading copyrighted content without permission may violate copyright laws and terms of service. Use at your own risk. The developers are not responsible for any misuse.

## License

This project is provided as-is without any warranty. See individual dependencies for their respective licenses.