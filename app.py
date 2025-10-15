from flask import Flask, request, render_template, send_file, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os
import zipfile
import threading
from typing import List, Dict, Optional, Union, TypedDict, Callable, Any, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import queue
import atexit
import urllib3

# Browser Manager for optimized resource usage
class BrowserManager:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.task_queue: queue.Queue[Tuple[int, Callable[..., Any], Tuple[Any, ...], Dict[str, Any]]] = queue.Queue()
        self.max_operations_per_driver = 50  # Restart after this many operations
        self.operation_count = 0
        self.worker_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.results: Dict[int, Dict[str, Any]] = {}  # Store results by task_id
        self.task_id_counter = 0
        self._initialize_driver()
        self._start_worker()

    def _initialize_driver(self):
        """Initialize Chrome driver with optimized options"""
        options = Options()
        # Headless mode for resource efficiency
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

        # Memory and performance optimizations
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")

        service = Service(executable_path='chromedriver-win64/chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.operation_count = 0
        print("DEBUG: BrowserManager initialized new Chrome driver")

    def _start_worker(self):
        """Start the worker thread to process queued tasks"""
        if self.worker_thread and self.worker_thread.is_alive():
            return

        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        print("DEBUG: BrowserManager worker thread started")

    def _process_queue(self):
        """Worker thread that processes tasks from the queue"""
        while self.is_running:
            try:
                task_id, task_func, args, kwargs = self.task_queue.get(timeout=1)
                try:
                    result = self.execute_task(task_func, *args, **kwargs)
                    self.results[task_id] = {'result': result, 'error': None}
                except Exception as e:
                    self.results[task_id] = {'result': None, 'error': str(e)}
                finally:
                    self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"DEBUG: Queue processing error: {e}")

    def _restart_driver_if_needed(self):
        """Restart driver if operation limit reached"""
        if self.operation_count >= self.max_operations_per_driver:
            print(f"DEBUG: Restarting driver after {self.operation_count} operations")
            self._quit_driver()
            self._initialize_driver()

    def _quit_driver(self):
        """Safely quit the current driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"DEBUG: Error quitting driver: {e}")
            self.driver = None

    def execute_task(self, task_func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a browser task, handling driver lifecycle"""
        self._restart_driver_if_needed()

        if not self.driver:
            raise Exception("Browser driver not available")

        try:
            result = task_func(self.driver, *args, **kwargs)
            self.operation_count += 1
            return result
        except Exception as e:
            print(f"DEBUG: Task execution failed: {e}")
            # If task fails, restart driver on next operation
            self._quit_driver()
            raise e

    def submit_task(self, task_func: Callable[..., Any], *args: Any, **kwargs: Any) -> int:
        """Submit a task to the queue and return a task ID"""
        task_id = self.task_id_counter
        self.task_id_counter += 1
        self.task_queue.put((task_id, task_func, args, kwargs))
        return task_id

    def get_result(self, task_id: int, timeout: float = 30) -> Any:
        """Get the result of a queued task"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if task_id in self.results:
                result = self.results.pop(task_id)
                if result['error']:
                    raise Exception(result['error'])
                return result['result']
            time.sleep(0.1)
        raise Exception(f"Task {task_id} timed out")

    def cleanup(self):
        """Cleanup resources"""
        print("DEBUG: Starting BrowserManager cleanup...")
        self.is_running = False
        
        # Wait for queue to finish processing
        try:
            self.task_queue.join()
        except Exception as e:
            print(f"DEBUG: Error waiting for queue: {e}")
        
        # Stop worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            try:
                self.worker_thread.join(timeout=5)
            except Exception as e:
                print(f"DEBUG: Error joining worker thread: {e}")
        
        # Quit driver
        self._quit_driver()
        print("DEBUG: BrowserManager cleanup complete")

# Global browser manager instance
browser_manager = BrowserManager()

# Register cleanup on exit
atexit.register(browser_manager.cleanup)

# Global download status
download_status: dict[str, Union[bool, int, str, float]] = {
    'is_downloading': False,
    'progress': 0,
    'current_episode': 0,
    'total_episodes': 0,
    'status_message': 'Initializing...',
    'completed': False
}

class Episode(TypedDict):
    number: int
    link: str

class DownloadOption(TypedDict):
    res: str
    url: str
    group: str

app = Flask(__name__)

def get_ddg_cookies(url: str) -> str:
    r = requests.get('https://check.ddos-guard.net/check.js', headers={'referer': url})
    r.raise_for_status()
    return r.cookies.get_dict()['__ddg2']

def get_string(content: str, s1: int, s2: int) -> str:
    slice_2 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"[0:s2]
    acc = 0
    for n, i in enumerate(content[::-1]):
        acc += int(i if i.isdigit() else 0) * s1**n
    k = ""
    while acc > 0:
        k = slice_2[int(acc % s2)] + k
        acc = (acc - (acc % s2)) / s2
    return k or "0"

def decrypt(full_string: str, key: str, v1: str, v2: str) -> str:
    v1_int, v2_int = int(v1), int(v2)
    r = ""
    i = 0
    while i < len(full_string):
        s = ""
        while full_string[i] != key[v2_int]:
            s += full_string[i]
            i += 1
        j = 0
        while j < len(key):
            s = s.replace(key[j], str(j))
            j += 1
        r += chr(int(get_string(s, v2_int, 10)) - v1_int)
        i += 1
    return r

def get_episodes_task(driver: webdriver.Chrome, siteLink: str, domain: str = "animepahe.si") -> List[Episode]:
    """Task function for getting episodes using the shared driver"""
    url = f"https://{domain}/anime/{siteLink}"
    print(f"DEBUG: Fetching anime page with Selenium: {url}")

    driver.get(url)
    print("DEBUG: Page loaded, waiting for content...")

    # Wait for episode links to load with a longer timeout
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/play/']")))
    print("DEBUG: Episode links found")

    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    print(f"DEBUG: Page title: {soup.title.text if soup.title else 'No title'}")
    print(f"DEBUG: Total a tags: {len(soup.find_all('a'))}")

    ep_list: List[Episode] = []
    for a in soup.find_all('a', href=True):
        if '/play/' in a['href'] and siteLink in a['href']:
            text = a.get_text().strip()
            print(f"DEBUG: Found episode link: {a['href']}, text: '{text}'")
            # Check for 'Watch - X Online' format
            if 'Watch' in text and 'Online' in text:
                try:
                    # Extract number between ' - ' and ' Online'
                    start = text.find(' - ') + 3
                    end = text.find(' Online')
                    if start > 2 and end > start:
                        ep_num = int(text[start:end])
                        ep_link = f'https://{domain}' + str(a['href'])
                        ep_list.append({'number': ep_num, 'link': ep_link})
                except ValueError:
                    print(f"DEBUG: Failed to parse episode number from '{text}'")
                    pass
            elif text.startswith('Episode '):
                try:
                    ep_num = int(text.split()[1])
                    ep_link = f'https://{domain}' + str(a['href'])
                    ep_list.append({'number': ep_num, 'link': ep_link})
                except (ValueError, IndexError):
                    print(f"DEBUG: Failed to parse episode number from '{text}'")
                    pass

    print(f"DEBUG: Episodes found: {len(ep_list)}")
    return sorted(ep_list, key=lambda x: x['number'])

def get_episodes(siteLink: str, domain: str = "animepahe.si") -> List[Episode]:
    """Get episodes using the browser manager"""
    try:
        task_id = browser_manager.submit_task(get_episodes_task, siteLink, domain)
        return browser_manager.get_result(task_id)
    except Exception as e:
        print(f"DEBUG: Exception in get_episodes: {e}")
        return []

def get_download_options_task(driver: webdriver.Chrome, ep_link: str) -> List[DownloadOption]:
    """Task function for getting download options using the shared driver"""
    driver.get(ep_link)
    print("DEBUG: Loaded episode page, waiting for download options...")

    # Wait for the page to load and find the download dropdown
    wait = WebDriverWait(driver, 30)

    # Try to find and click the download dropdown toggle
    try:
        # Look for common dropdown toggle selectors
        dropdown_selectors = [
            ".dropdown-toggle",
            "[data-toggle='dropdown']",
            ".download-toggle",
            "button[class*='download']",
            ".btn-download"
        ]

        dropdown_clicked = False
        for selector in dropdown_selectors:
            try:
                dropdown_toggle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                dropdown_toggle.click()
                print(f"DEBUG: Clicked dropdown toggle: {selector}")
                dropdown_clicked = True
                break
            except:
                continue

        if not dropdown_clicked:
            print("DEBUG: Could not find dropdown toggle, proceeding without clicking")

    except Exception as e:
        print(f"DEBUG: Error clicking dropdown: {e}")

    # Wait a bit for options to load
    time.sleep(2)

    # Wait for download options to load
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dropdown-item")))
    print("DEBUG: Download options found")

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    options_list: List[DownloadOption] = []
    for a in soup.find_all('a', class_='dropdown-item'):
        text = a.get_text().strip()
        print(f"DEBUG: Found download option: '{text}'")
        url = a['href']
        # Parse the text format like "SubsPlease · 720p (88MB)" or "Yameii · 1080p (139MB) eng"
        if '·' in text:
            parts = text.split('·')
            if len(parts) >= 2:
                group = parts[0].strip()
                quality_part = parts[1].strip()
                print(f"DEBUG: Parsing - Group: '{group}', Quality part: '{quality_part}'")

                # Extract resolution from quality part (e.g., "720p (88MB)" -> "720")
                import re
                print(f"DEBUG: Searching for resolution in: '{quality_part}'")
                res_match = re.search(r'(\d+)p', quality_part)
                print(f"DEBUG: Regex match result: {res_match}")
                if res_match:
                    res = res_match.group(1)
                    print(f"DEBUG: Extracted resolution: {res}")
                    options_list.append({'res': res, 'url': str(url), 'group': group})
                    print(f"DEBUG: Parsed option - Group: {group}, Res: {res}p, URL: {url}")
                else:
                    print(f"DEBUG: Could not extract resolution from: '{quality_part}' - no regex match")
            else:
                print(f"DEBUG: Not enough parts after splitting '{text}' by '·'")
        else:
            # Fallback for other formats
            print(f"DEBUG: Option doesn't contain '·': '{text}'")

    print(f"DEBUG: Total download options found: {len(options_list)}")
    return options_list

def get_download_options(ep_link: str) -> List[DownloadOption]:
    """Get download options using the browser manager"""
    try:
        task_id = browser_manager.submit_task(get_download_options_task, ep_link)
        return browser_manager.get_result(task_id)
    except Exception as e:
        print(f"Exception in get_download_options: {e}")
        return []

def get_download_link_task(driver: webdriver.Chrome, pahe_win_url: str) -> Optional[str]:
    """Task function for getting download link redirect URL using the shared driver"""
    print(f"DEBUG: Loading pahe.win page: {pahe_win_url}")
    driver.get(pahe_win_url)

    # Wait for the "Continue" link to appear (it appears after the countdown)
    continue_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Continue')]"))
    )
    redirect_url = continue_link.get_attribute('href')  # type: ignore
    if redirect_url is None:
        print("DEBUG: No redirect URL found")
        return None
    print(f"DEBUG: Found redirect URL: {redirect_url}")
    return redirect_url

def get_download_link(pahe_win_url: str) -> Optional[str]:
    """Get download link using the browser manager for the browser part, then requests for the rest"""
    try:
        # Use browser manager for the Selenium part
        task_id = browser_manager.submit_task(get_download_link_task, pahe_win_url)
        redirect_url = browser_manager.get_result(task_id)

        if not redirect_url:
            return None

        # Now proceed with the original logic using requests
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        session.headers.update(headers)

        cookie = get_ddg_cookies(redirect_url)
        session.cookies.set('__ddg2', cookie, domain='.kwik.cx')  # type: ignore
        response = session.get(redirect_url)
        match = re.search(r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)', response.text)
        if not match:
            return None
        full_key, key, v1, v2 = match.groups()
        decrypted = decrypt(full_key, key, v1, v2)
        action_match = re.search('action="(.+?)"', decrypted)
        token_match = re.search('value="(.+?)"', decrypted)
        if not action_match or not token_match:
            return None
        action = action_match.group(1)
        token = token_match.group(1)
        content = session.post(action, allow_redirects=False, data={"_token": token}, headers={"Referer": "https://kwik.cx/"})
        return content.headers.get("Location")

    except Exception as e:
        print(f"DEBUG: Exception in get_download_link: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    print(f"DEBUG: Received URL: {url}")

    # Extract domain and anime_id more flexibly
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_parts = parsed_url.path.strip('/').split('/')
        anime_id = path_parts[-1] if path_parts else ''

        print(f"DEBUG: Parsed domain: {domain}, anime_id: {anime_id}")

        if not anime_id:
            return "Invalid URL format. Please provide a complete anime page URL."

        # Use the domain from the user's URL instead of hardcoding animepahe.si
        full_url = f"https://{domain}/anime/{anime_id}"
        print(f"DEBUG: Full URL to fetch: {full_url}")

    except Exception as e:
        print(f"DEBUG: URL parsing error: {e}")
        return "Invalid URL format."

    print("DEBUG: Calling get_episodes...")
    episodes = get_episodes(anime_id, domain)
    print(f"DEBUG: Episodes found: {len(episodes)}")
    if not episodes:
        print("DEBUG: No episodes found, returning error message")
        return "No episodes found or invalid URL. Please check that the URL is correct and try again."
    print("DEBUG: Rendering select.html template")
    return render_template('select.html', episodes=episodes, url=url)

@app.route('/download_selected', methods=['POST'])
def download_selected():
    url = request.form['url']

    # Extract domain and anime_id more flexibly
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_parts = parsed_url.path.strip('/').split('/')
        anime_id = path_parts[-1] if path_parts else ''

        if not anime_id:
            return "Invalid URL format."

    except Exception:
        return "Invalid URL format."

    episodes = get_episodes(anime_id, domain)
    selected = request.form.getlist('selected')
    selected_nums = [int(s) for s in selected]
    selected_eps = [ep for ep in episodes if ep['number'] in selected_nums]

    # Initialize download status
    global download_status
    download_status = {
        'is_downloading': True,
        'progress': 0,
        'current_episode': 0,
        'total_episodes': len(selected_eps),
        'status_message': 'Starting download process...',
        'completed': False
    }

    # Start download in background thread
    download_thread = threading.Thread(target=process_downloads, args=(selected_eps,))
    download_thread.start()

    return render_template('downloading.html', episode_count=len(selected_eps))

def process_downloads(selected_eps: List[Episode]) -> None:
    global download_status
    download_dir = 'downloads'
    os.makedirs(download_dir, exist_ok=True)
    print(f"DEBUG: Created downloads directory: {download_dir}")
    print(f"DEBUG: Processing {len(selected_eps)} episodes")

    download_status['status_message'] = f'Processing {len(selected_eps)} episodes...'

    def download_ep(ep: Dict[str, Union[int, str]]) -> None:
        global download_status
        print(f"DEBUG: Processing episode {ep['number']}: {ep['link']}")
        download_status['status_message'] = f'Finding download options for episode {ep["number"]}...'
        
        options = get_download_options(str(ep['link']))
        print(f"DEBUG: Download options: {options}")

        if not options:
            print(f"DEBUG: No download options found for episode {ep['number']}")
            return

        download_status['status_message'] = f'Selecting quality for episode {ep["number"]}...'
        pahe_url = None

        # Prefer 720p, but fall back to highest available quality
        preferred_resolutions = ['720', '1080', '480', '360']
        for pref_res in preferred_resolutions:
            for opt in options:
                if opt['res'] == pref_res:
                    pahe_url = opt['url']
                    print(f"DEBUG: Selected {pref_res}p option: {pahe_url}")
                    break
            if pahe_url:
                break

        # If no preferred resolution found, take the first available
        if not pahe_url and options:
            pahe_url = options[0]['url']
            print(f"DEBUG: No preferred resolution found, using: {pahe_url}")

        if not pahe_url:
            print(f"DEBUG: No download URL found for episode {ep['number']}")
            return

        download_status['status_message'] = f'Getting download link for episode {ep["number"]}...'
        print(f"DEBUG: Getting download link from: {pahe_url}")
        download_url = get_download_link(pahe_url)
        print(f"DEBUG: Final download URL: {download_url}")

        if not download_url:
            print(f"DEBUG: No download URL obtained for episode {ep['number']}")
            return

        download_status['current_episode'] = ep['number']
        download_status['status_message'] = f'Downloading episode {ep["number"]}...'
        filename = f"ep_{str(ep['number'])}.mp4"
        filepath = os.path.join(download_dir, filename)
        print(f"DEBUG: Downloading to: {filepath}")

        try:
            # First attempt with SSL verification enabled
            try:
                with requests.get(download_url, stream=True, timeout=30, verify=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    episode_progress = (downloaded / total_size) * 100
                                    overall_progress = ((int(ep['number']) - 1) / len(selected_eps) * 100) + (episode_progress / len(selected_eps))
                                    download_status['progress'] = min(overall_progress, 90)
                print(f"DEBUG: Successfully downloaded {filename}")
            except requests.exceptions.SSLError as ssl_error:
                # SSL verification failed, retry with verification disabled
                print(f"DEBUG: SSL verification failed for {filename}, retrying with SSL verification disabled: {ssl_error}")
                # Suppress SSL warnings for this request
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                with requests.get(download_url, stream=True, timeout=30, verify=False) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    episode_progress = (downloaded / total_size) * 100
                                    overall_progress = ((int(ep['number']) - 1) / len(selected_eps) * 100) + (episode_progress / len(selected_eps))
                                    download_status['progress'] = min(overall_progress, 90)
                print(f"DEBUG: Successfully downloaded {filename} (SSL verification disabled)")
        except Exception as e:
            print(f"DEBUG: Download failed for {filename}: {e}")

    threads: List[threading.Thread] = []
    for ep in selected_eps:
        t = threading.Thread(target=download_ep, args=(ep,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # Create ZIP file
    download_status['status_message'] = 'Creating ZIP file...'
    zip_path = 'downloads.zip'
    files_to_zip = os.listdir(download_dir)
    print(f"DEBUG: Files in downloads directory: {files_to_zip}")

    with zipfile.ZipFile(zip_path, 'w') as zf:
        for file in files_to_zip:
            file_path = os.path.join(download_dir, file)
            if os.path.isfile(file_path):
                zf.write(file_path, file)
                print(f"DEBUG: Added {file} to ZIP")
            else:
                print(f"DEBUG: Skipping {file} (not a file)")

    zip_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
    print(f"DEBUG: ZIP file created successfully, size: {zip_size} bytes")
    
    download_status['progress'] = 100
    download_status['status_message'] = 'Download complete! Preparing file...'
    download_status['completed'] = True
    download_status['is_downloading'] = False

@app.route('/download_status')
def download_status_route():
    global download_status
    return jsonify(download_status)

@app.route('/check_download')
def check_download():
    zip_path = 'downloads.zip'
    if os.path.exists(zip_path):
        if request.method == 'HEAD':
            # For HEAD requests, just return success status
            return '', 200, {'Content-Type': 'application/zip', 'Content-Disposition': 'attachment; filename=anime_episodes.zip'}
        else:
            # For GET requests, return the actual file
            return send_file(zip_path, as_attachment=True, download_name='anime_episodes.zip')
    else:
        return "Download not ready yet. Please wait...", 202