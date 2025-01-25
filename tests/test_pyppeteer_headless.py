import asyncio
import logging
from pyppeteer import launch
import os
from pyppeteer.chromium_downloader import chromium_executable

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_headless_launch():
    logging.info("Starting headless browser launch...")
    print("Chromium executable path:", chromium_executable())

    try:
        browser = await launch(headless=True)
        assert browser is not None, "Browser failed to launch in headless mode"
        logging.info("Browser launched successfully.")
    except Exception as e:
        logging.error(f"Failed to launch browser: {e}")
        return

    logging.info("Creating a new page...")
    try:
        page = await browser.newPage()
        assert page is not None, "Page failed to launch in headless mode"
        logging.info("New page created successfully.")
    except Exception as e:
        logging.error(f"Failed to create new page: {e}")
        await browser.close()
        return

    try:
        await page.close()
        logging.info("Page closed successfully.")
    except Exception as e:
        logging.error(f"Failed to close page: {e}")

    try:
        await browser.close()
        logging.info("Browser closed successfully.")
    except Exception as e:
        logging.error(f"Failed to close browser: {e}")

if __name__ == '__main__':
    asyncio.run(test_headless_launch())
