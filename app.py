from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
import re
import os
import zipfile
import threading
from typing import List, Dict, Optional, Union, TypedDict

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

def get_episodes(siteLink: str) -> List[Dict[str, Union[int, str]]]:
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    session.headers.update(headers)
    ep_list: List[Dict[str, Union[int, str]]] = []
    page = 1
    while True:
        url = f"https://animepahe.ru/api?m=release&id={siteLink}&sort=episode_asc&page={page}"
        print(f"Fetching URL: {url}")
        try:
            cookie = get_ddg_cookies(url)
            session.cookies.set('__ddg2', cookie, domain='animepahe.ru')  # type: ignore
            response = session.get(url)
            print(f"Response status: {response.status_code}")
            data = response.json()
            print(f"Data: {data}")
            if not data.get('data'):
                print("No data in response")
                break
            for ep in data['data']:
                ep_link = f"https://animepahe.ru/play/{siteLink}/{ep['session']}"
                ep_list.append({'number': ep['episode'], 'link': ep_link})
            page += 1
        except Exception as e:
            print(f"Exception: {e}")
            break
    print(f"Total episodes: {len(ep_list)}")
    return ep_list

def get_download_options(ep_link: str) -> List[DownloadOption]:
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    session.headers.update(headers)
    try:
        cookie = get_ddg_cookies(ep_link)
        session.cookies.set('__ddg2', cookie, domain='animepahe.ru')  # type: ignore
        response = session.get(ep_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        options: List[DownloadOption] = []
        for a in soup.find_all('a', class_='dropdown-item'):
            text = a.get_text()
            if 'p' in text and 'MB' in text:
                res = text.split()[0]
                url = str(a['href'])
                options.append({'res': res, 'url': url})
        return options
    except:
        return []

def get_download_link(pahe_win_url: str) -> Optional[str]:
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    session.headers.update(headers)
    try:
        cookie = get_ddg_cookies(pahe_win_url)
        session.cookies.set('__ddg2', cookie, domain='pahe.win')  # type: ignore
        response = session.get(pahe_win_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        redirect_link_elem = soup.find('a', text='Redirect me')
        if not redirect_link_elem:
            return None
        redirect_link = str(redirect_link_elem['href'])
        cookie = get_ddg_cookies(redirect_link)
        session.cookies.set('__ddg2', cookie, domain='kwik.cx')  # type: ignore
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
    anime_id = url.split('/')[-1]
    print(f"Anime ID: {anime_id}")
    episodes = get_episodes(anime_id)
    print(f"Episodes found: {len(episodes)}")
    if not episodes:
        return "No episodes found or invalid URL"
    download_dir = 'downloads'
    os.makedirs(download_dir, exist_ok=True)
    
    def download_ep(ep: Dict[str, Union[int, str]]) -> None:
        options = get_download_options(str(ep['link']))
        pahe_url = None
        for opt in options:
            if '720' in opt['res']:
                pahe_url = opt['url']
                break
        if not pahe_url:
            return
        download_url = get_download_link(pahe_url)
        if not download_url:
            return
        filename = f"ep_{str(ep['number'])}.mp4"
        filepath = os.path.join(download_dir, filename)
        try:
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except:
            pass  # Skip failed downloads
    
    threads: List[threading.Thread] = []
    for ep in episodes[:5]:  # Limit to first 5 for testing
        t = threading.Thread(target=download_ep, args=(ep,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    
    # Zip
    zip_path = 'downloads.zip'
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for file in os.listdir(download_dir):
            zf.write(os.path.join(download_dir, file), file)
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)