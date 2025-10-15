# 🎬 Pahe Downloader

A modern, beautiful Flask-based web application for downloading anime episodes from animepahe.si. This tool features an intuitive interface for selecting and downloading multiple episodes in 720p quality.

![UI Preview](https://via.placeholder.com/800x400/6366f1/ffffff?text=Modern+Anime+Downloader+UI)

## ✨ Features

- 🎨 **Modern UI/UX**: Beautiful, responsive design with gradient backgrounds and smooth animations
- 📱 **Mobile-Friendly**: Fully responsive design that works on all devices
- 🎯 **Smart Episode Selection**: Visual episode cards with easy selection/deselection
- ⚡ **Real-time Progress**: Live progress tracking during downloads
- 🔄 **Concurrent Downloads**: Multiple episodes download simultaneously for faster processing
- 📦 **Auto-Zipping**: Downloads are automatically packaged into ZIP files
- 🛡️ **Bypass Protections**: Uses Selenium to handle site protections
- ⌨️ **Keyboard Shortcuts**: Ctrl+A to select/deselect all episodes
- 🎪 **Interactive Elements**: Hover effects, loading states, and smooth transitions

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- uv package manager (recommended)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/al-chris/pahe-downloader.git
   cd pahe-downloader
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

3. **Download ChromeDriver:**
   The app includes ChromeDriver for Windows 64-bit. For other platforms, download the appropriate version from [ChromeDriver downloads](https://chromedriver.chromium.org/downloads).

## 🎯 Usage

1. **Start the application:**
   ```bash
   uv run main.py
   ```
   Or:
   ```bash
   python main.py
   ```

2. **Open your browser:**
   Navigate to `http://127.0.0.1:5000/`

3. **Enter anime URL:**
   - Copy the full URL from animepahe.si, animepahe.ru, animepahe.com, or other AnimePahe domains
   - The URL field validates input and provides visual feedback
   - Make sure the URL contains "/anime/" in the path

4. **Select episodes:**
   - View all available episodes in a beautiful grid layout
   - Episodes are pre-selected by default
   - Click individual episodes or use "Select All" to toggle selection
   - Use Ctrl+A keyboard shortcut for quick selection

5. **Download:**
   - Click "📥 Download Selected Episodes"
   - Monitor real-time progress on the download page
   - Download completes automatically when ready

## 🎨 UI Features

### Homepage
- Gradient background with anime-themed styling
- Clean form with URL validation
- Helpful usage instructions
- Responsive design for all screen sizes

### Episode Selection
- Card-based layout for easy episode browsing
- Visual selection states with smooth animations
- Episode count display
- Bulk selection controls

### Download Progress
- Real-time progress bar
- Status messages throughout the process
- Automatic download initiation when complete
- Fallback handling for long downloads

## 🔧 How It Works

1. **URL Processing**: Extracts anime ID from the provided URL
2. **Episode Discovery**: Uses Selenium to scrape episode information
3. **Link Resolution**: Bypasses DDoS-Guard and resolves download links
4. **Concurrent Downloads**: Downloads multiple episodes simultaneously
5. **Packaging**: Creates a ZIP file containing all downloaded episodes
6. **Delivery**: Provides the ZIP file for download

## ⚠️ Disclaimer

This application is intended for **personal use only**. Downloading copyrighted content without permission may violate copyright laws and terms of service. Use at your own risk. The developers are not responsible for any misuse.

## 🛠️ Technical Details

- **Backend**: Flask web framework
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Web Scraping**: Selenium WebDriver
- **Styling**: Custom CSS with modern design principles
- **Icons**: Unicode emojis for lightweight iconography

## 📝 License

This project is provided as-is without any warranty. See individual dependencies for their respective licenses.