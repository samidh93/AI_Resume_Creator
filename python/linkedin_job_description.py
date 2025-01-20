# class to fetch the text from a linkedin job description
import requests
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch

class LinkedinJobDescription:
    def __init__(self, job_description_url):
        self.job_description_url = job_description_url

    async def get_text_job_description_with_pyppeteer(self):
        browser = await launch(headless=False)
        page = await browser.newPage()
        try:
            await page.goto(self.job_description_url, timeout=60000)  # Increase timeout to 60 seconds
            print('Page loaded, waiting for job description...')
            # Click the dismiss button if it exists
            try:
                await page.waitForSelector('.modal__dismiss', timeout=5000)
                await page.click('.modal__dismiss')  # Click the dismiss button to close the popup
            except Exception as e:
                print('No dismiss button found.')
            await page.waitForSelector('.show-more-less-html__button--more', timeout=5000)
            await page.click('.show-more-less-html__button--more')  # Click the button to show more content
            content = await page.content()  # Get the full HTML content
            soup = BeautifulSoup(content, 'html.parser')
            self.job_description = soup.find('div', class_='show-more-less-html__markup')
            return self.job_description.get_text(strip=True) if self.job_description else 'Job description not found.'
        except Exception as e:
            print('An error occurred:', e)
            return 'Error fetching job description.'
        finally:
            await browser.close()


if __name__ == '__main__':
    # Example usage: create object and call get_text_job_description method
    job_url_1 = "https://www.linkedin.com/jobs/view/4117398597"
    job_url_2 = "https://www.linkedin.com/jobs/view/4114811878"
    job_url_3 = "https://www.linkedin.com/jobs/view/4105397342"
    extract_job_description = LinkedinJobDescription(job_url_1)
    print(asyncio.run(extract_job_description.get_text_job_description_with_pyppeteer()))
    extract_job_description = LinkedinJobDescription(job_url_2)
    print(asyncio.run(extract_job_description.get_text_job_description_with_pyppeteer()))
    extract_job_description = LinkedinJobDescription(job_url_3)
    print(asyncio.run(extract_job_description.get_text_job_description_with_pyppeteer()))

