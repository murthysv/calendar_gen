import asyncio
from pyppeteer import launch
from pyppeteer.chromium_downloader import chromium_executable

async def test_browser():
    print(f"Chromium Path: {chromium_executable()}")

    try:
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        print("Browser launched successfully")
        await browser.close()
    except Exception as e:
        print(f"Browser test failed: {e}")

asyncio.run(test_browser())
