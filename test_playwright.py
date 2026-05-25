import sys
from playwright.sync_api import sync_playwright

def test_kwik():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        )
        url = "https://kwik.cx/f/3ARagPqidppx"
        print(f"Loading {url}...")
        page.goto(url, wait_until='domcontentloaded')
        
        try:
            print("Waiting for form...")
            form = page.wait_for_selector("form", timeout=30000)
            if form:
                print("Found form!")
                
                # Check what form it is
                print(form.evaluate("e => e.outerHTML"))
            else:
                print("No form found")
        except Exception as e:
            print(f"Error: {e}")
            
            # Print page content to see if we're on cloudflare
            content = page.content()
            if "Cloudflare" in content or "Just a moment" in content:
                print("Stuck on Cloudflare!")
            else:
                print("Not Cloudflare, something else.")

if __name__ == "__main__":
    test_kwik()