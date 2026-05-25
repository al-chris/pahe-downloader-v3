import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        url = "https://kwik.cx/f/MlTvUlRyiXdo"
        print(f"Navigating to {url}...")
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            print("Waiting for form to appear (up to 30s)...")
            try:
                form = await page.wait_for_selector("form", timeout=30000)
                if form:
                    print("Form found!")
                    content = await page.content()
                    with open("kwik_debug_success.html", "w", encoding="utf-8") as f:
                        f.write(content)
                else:
                    print("Form NOT found (waited 30s)!")
            except Exception as e:
                print(f"Form wait error: {e}")
                content = await page.content()
                with open("kwik_debug_failed.html", "w", encoding="utf-8") as f:
                    f.write(content)
            
            await page.screenshot(path="kwik_debug_stealth.png")
            
        except Exception as e:
            print(f"Navigation error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
