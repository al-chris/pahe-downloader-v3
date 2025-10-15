from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
import re
import os
import zipfile
import threading
from typing import List, Dict, Optional, Union, TypedDict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Episode(TypedDict):
    number: int
    link: str

class DownloadOption(TypedDict):
    res: str
    url: str

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

def get_episodes(siteLink: str, domain: str = "animepahe.si") -> List[Dict[str, Union[int, str]]]:
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    service = Service(executable_path='chromedriver-win64/chromedriver.exe')

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"DEBUG: Failed to initialize Chrome driver: {e}")
        return []

    url = f"https://{domain}/anime/{siteLink}"
    print(f"DEBUG: Fetching anime page with Selenium: {url}")

    try:
        driver.get(url)
        print("DEBUG: Page loaded, waiting for content...")

        # Wait for episode links to load with a longer timeout
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/play/']")))
        print("DEBUG: Episode links found")

        page_source = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page_source, 'html.parser')
        print(f"DEBUG: Page title: {soup.title.text if soup.title else 'No title'}")
        print(f"DEBUG: Total a tags: {len(soup.find_all('a'))}")

        ep_list = []
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
                            ep_link = f'https://{domain}' + a['href']
                            ep_list.append({'number': ep_num, 'link': ep_link})
                    except ValueError as e:
                        print(f"DEBUG: Failed to parse episode number from '{text}': {e}")
                        pass
                elif text.startswith('Episode '):
                    try:
                        ep_num = int(text.split()[1])
                        ep_link = f'https://{domain}' + a['href']
                        ep_list.append({'number': ep_num, 'link': ep_link})
                    except (ValueError, IndexError) as e:
                        print(f"DEBUG: Failed to parse episode number from '{text}': {e}")
                        pass

        print(f"DEBUG: Episodes found: {len(ep_list)}")
        return sorted(ep_list, key=lambda x: x['number'])

    except Exception as e:
        print(f"DEBUG: Exception in get_episodes: {e}")
        try:
            driver.quit()
        except:
            pass
        return []

def get_download_options(ep_link: str) -> List[Dict[str, str]]:
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path='chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    try:
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
        import time
        time.sleep(2)

        # Wait for download options to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dropdown-item")))
        print("DEBUG: Download options found")

        page_source = driver.page_source
        driver.quit()
        soup = BeautifulSoup(page_source, 'html.parser')
        options_list = []
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
                        options_list.append({'res': res, 'url': url, 'group': group})
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
    except Exception as e:
        print(f"Exception in get_download_options: {e}")
        driver.quit()
        return []

def get_download_link(pahe_win_url: str) -> Optional[str]:
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
    try:
        cookie = get_ddg_cookies(pahe_win_url)
        session.cookies.set('__ddg2', cookie, domain='.pahe.win')  # type: ignore
        response = session.get(pahe_win_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        redirect_link_elem = soup.find('a', text='Redirect me')
        if not redirect_link_elem:
            return None
        redirect_link = str(redirect_link_elem['href'])
        cookie = get_ddg_cookies(redirect_link)
        session.cookies.set('__ddg2', cookie, domain='.kwik.cx')  # type: ignore
        response = session.get(redirect_link)
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
    except:
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

    except Exception as e:
        return "Invalid URL format."

    episodes = get_episodes(anime_id, domain)
    selected = request.form.getlist('selected')
    selected_nums = [int(s) for s in selected]
    selected_eps = [ep for ep in episodes if ep['number'] in selected_nums]

    # Start download in background thread
    download_thread = threading.Thread(target=process_downloads, args=(selected_eps,))
    download_thread.start()

    return render_template('downloading.html', episode_count=len(selected_eps))

def process_downloads(selected_eps):
    download_dir = 'downloads'
    os.makedirs(download_dir, exist_ok=True)
    print(f"DEBUG: Created downloads directory: {download_dir}")
    print(f"DEBUG: Processing {len(selected_eps)} episodes")

    def download_ep(ep: Dict[str, Union[int, str]]) -> None:
        print(f"DEBUG: Processing episode {ep['number']}: {ep['link']}")
        options = get_download_options(str(ep['link']))
        print(f"DEBUG: Download options: {options}")

        if not options:
            print(f"DEBUG: No download options found for episode {ep['number']}")
            return

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

        print(f"DEBUG: Getting download link from: {pahe_url}")
        download_url = get_download_link(pahe_url)
        print(f"DEBUG: Final download URL: {download_url}")

        if not download_url:
            print(f"DEBUG: No download URL obtained for episode {ep['number']}")
            return

        filename = f"ep_{str(ep['number'])}.mp4"
        filepath = os.path.join(download_dir, filename)
        print(f"DEBUG: Downloading to: {filepath}")

        try:
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"DEBUG: Successfully downloaded {filename}")
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

if __name__ == '__main__':
    app.run(debug=True)