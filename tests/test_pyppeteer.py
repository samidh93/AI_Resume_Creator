import asyncio
from pyppeteer import launch

async def test():
    browser = await launch(headless=True)
    print("Browser launched successfully!")
    await browser.close()
    print("Browser closed.")

if __name__ == "__main__":  
    asyncio.run(test())
