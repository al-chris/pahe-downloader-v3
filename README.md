# 🎬 Pahe Downloader

A modern, standalone desktop application for downloading anime episodes from animepahe.si. Built with Flask backend and PyWebView frontend, featuring intelligent file naming and automated browser driver management.

![UI Preview](https://via.placeholder.com/800x400/6366f1/ffffff?text=Modern+Anime+Downloader+UI)

## ✨ Features

- 🖥️ **Desktop Application**: Native desktop window using PyWebView - no browser required
- 🎨 **Modern UI/UX**: Beautiful, responsive design with gradient backgrounds and smooth animations
- 📱 **Mobile-Friendly**: Fully responsive design that works on all devices
- 🎯 **Smart Episode Selection**: Visual episode cards with easy selection/deselection
- ⚡ **Real-time Progress**: Live progress tracking during downloads
- 🔄 **Concurrent Downloads**: Multiple episodes download simultaneously for faster processing
- 📂 **Intelligent Naming**: Downloads named with anime title and episode number (e.g., "One Piece_Episode_1.mp4")
- 🔍 **Auto Extension Detection**: Automatically detects correct file extensions (.mp4, .mkv, .avi, etc.)
- 🤖 **Automated Driver Management**: webdriver-manager handles Chrome driver setup automatically
- 🛡️ **Bypass Protections**: Uses Selenium to handle site protections
- ⌨️ **Keyboard Shortcuts**: Ctrl+A to select/deselect all episodes
- 🎪 **Interactive Elements**: Hover effects, loading states, and smooth transitions
- 📦 **Single Executable**: Can be packaged as a standalone .exe file

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (automatically managed by webdriver-manager)
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

3. **No manual driver setup required:**
   webdriver-manager automatically downloads and manages Chrome drivers for your system.

## 🎯 Usage

1. **Start the application:**
   ```bash
   uv run main.py
   ```
   Or:
   ```bash
   python main.py
   ```

2. **Desktop window opens automatically:**
   The application will open in a native desktop window powered by PyWebView.

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
   - Files are saved to the `downloads/` folder with proper naming

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
- Files saved to `downloads/` folder with intelligent naming
- Automatic extension detection for proper file types

## 📁 File Naming & Organization

Downloads are automatically organized with descriptive filenames:
- **Format**: `{AnimeName}_Episode_{Number}.{extension}`
- **Examples**:
  - `One Piece_Episode_1.mp4`
  - `Attack on Titan_Episode_25.mkv`
  - `My Hero Academia_Episode_10.mp4`
- **Features**:
  - Anime name extracted from webpage title
  - Invalid characters automatically sanitized
  - Correct file extensions detected from server headers
  - Supports MP4, MKV, AVI, MOV, WMV, FLV, and WebM formats

## 🔧 How It Works

1. **URL Processing**: Extracts anime ID and title from the provided URL
2. **Episode Discovery**: Uses Selenium to scrape episode information and anime title
3. **Link Resolution**: Bypasses DDoS-Guard and resolves download links
4. **Extension Detection**: Analyzes HTTP headers to determine correct file extensions
5. **Intelligent Naming**: Creates filenames with anime title, episode number, and proper extension
6. **Concurrent Downloads**: Downloads multiple episodes simultaneously to `downloads/` folder
7. **Progress Tracking**: Real-time updates through the desktop interface

## 📦 Distribution

### Building Standalone Executable

To create a single executable file for easy distribution:

#### Option 1: Using the Build Script
```bash
# Install PyInstaller first
pip install pyinstaller

# Run the build script
python build.py
```

#### Option 2: Manual PyInstaller Command
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable with custom icon
pyinstaller --onefile --hidden-import=webdriver_manager --hidden-import=selenium --hidden-import=webview --hidden-import=webview.platforms.winforms --hidden-import=clr --hidden-import=pythonnet --hidden-import=flask --hidden-import=beautifulsoup4 --hidden-import=lxml --hidden-import=requests --hidden-import=urllib3 --name=pahe-downloader --clean --noconsole --icon=static/icon.png main.py
```

The executable will be created in the `dist/` folder as `pahe-downloader.exe` with the custom application icon.

#### Automated Releases

When you create a new release on GitHub, the CI/CD pipeline will automatically:
1. Build the executable using PyInstaller
2. Generate a SHA256 checksum for verification
3. Upload both files as release assets

Users can then download the standalone executable and run it without installing Python or any dependencies.

#### GitHub Releases

The project includes automated CI/CD that builds releases:

- **Trigger**: Creating a new release on GitHub automatically starts the build process
- **Platform**: Windows executables (built on `windows-latest` runners)
- **Artifacts**: 
  - `pahe-downloader.exe` - The standalone executable with custom icon
  - `pahe-downloader.exe.sha256` - SHA256 checksum for verification
- **Manual Trigger**: You can also trigger builds manually using the "Run workflow" button

## ⚠️ Disclaimer

This application is intended for **personal use only**. Downloading copyrighted content without permission may violate copyright laws and terms of service. Use at your own risk. The developers are not responsible for any misuse.

## 🛠️ Technical Details

- **Backend**: Flask web framework running locally
- **Frontend**: PyWebView desktop application wrapper
- **Web Scraping**: Selenium WebDriver with automated Chrome driver management
- **Driver Management**: webdriver-manager for cross-platform compatibility
- **File Handling**: Dynamic extension detection and intelligent naming
- **Styling**: Custom CSS with modern design principles
- **Icons**: Unicode emojis for lightweight iconography
- **Packaging**: PyInstaller-ready for single executable distribution

## 📝 License

This project is provided as-is without any warranty. See individual dependencies for their respective licenses.