# class to fetch the text from a linkedin job description
import requests
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
import os
from pyppeteer_stealth import stealth
from requests_html import HTMLSession

class LinkedinJobDescription:
    def __init__(self, job_description_url):
        self.job_description_url = job_description_url
        self.job_description = None

    def get_job_description(self):
        session = HTMLSession()
        response = session.get(self.job_description_url)
        response.html.render(sleep=2)  # Renders the page, similar to a headless browser
        job_description = response.html.find('.show-more-less-html__markup', first=True)
        if job_description:
            return job_description.text
        else:  
            return None

    async def get_job_description_via_pyppeteer(self):
        if os.environ.get('CONTAINER'):
            print('Running in a container, using custom Chromium executable path.')
            executablePath = "/usr/bin/chromium"
            args = ['--no-sandbox', '--disable-setuid-sandbox']
            browser = await launch(headless=True, executablePath=executablePath, args=args)
        else:
            print('Running locally, using default Chromium executable path.')
            browser = await launch(headless=True)

        page = await browser.newPage()
        await stealth(page)  # Hide automation fingerprints

        try:
            print(f'Fetching job description from: {self.job_description_url}')
            await page.goto(self.job_description_url, {'waitUntil': 'domcontentloaded'})  

            print('Page loaded, waiting for job description...')
            
            # Handle modal dismiss button if exists
            try:
                await page.waitForSelector('.modal__dismiss', timeout=5000)
                await page.click('.modal__dismiss')
                print('Closed modal popup.')
            except Exception:
                print('No dismiss button found.')

            # Click 'Show More' button if exists
            try:
                await page.waitForSelector('.show-more-less-html__button--more', timeout=5000)
                await page.click('.show-more-less-html__button--more')
                print('Expanded full job description.')
            except Exception:
                print('No "Show More" button found.')

            # Extract job description text
            job_description = await page.evaluate('''() => {
                let desc = document.querySelector('.show-more-less-html__markup');
                return desc ? desc.innerText.trim() : null;
            }''')

            self.job_description = job_description if job_description else None

        except Exception as e:
            print('An error occurred:', e)
            return 'Error fetching job description.'
        finally:
            await browser.close()
            print('Browser closed.')
            return self.job_description


    # only when logged in
    async def get_job_requirements(self, page):
        try:
            requirements = await page.evaluate('''() => {
                let section = document.querySelector('section.ph5.pt5');
                if (!section) return [];

                let listItems = section.querySelectorAll('ul li a');
                return Array.from(listItems).map(el => el.innerText.trim());
            }''')

            return requirements or []
        except Exception as e:
            print('An error occurred while fetching job requirements:', e)
            return []

    # only when logged in
    async def get_skills_required(self, page):
        try:
            skills = await page.evaluate('''() => {
                let section = document.querySelector('section.ph5.pt5');
                if (!section) return [];

                let skillElements = section.querySelectorAll('.job-criteria__text.job-criteria__text--criteria');
                return Array.from(skillElements).map(el => el.innerText.trim());
            }''')

            return skills or []
        except Exception as e:
            print('An error occurred while fetching required skills:', e)
            return []

if __name__ == '__main__':
    # Example usage: create object and call get_job_description method
    job_url_1 = "https://www.linkedin.com/jobs/view/4121332725"
    job_url_2 = "https://www.linkedin.com/jobs/view/4114811878"
    job_url_3 = "https://www.linkedin.com/jobs/view/4105397342"
    extract_job_description = LinkedinJobDescription(job_url_1)
    extract_job_description.get_job_description_no_browser()
    #loop = asyncio.get_event_loop()
    #extracted = loop.run_until_complete(extract_job_description.get_job_description())
    #print(extracted)
    #extract_job_description = LinkedinJobDescription(job_url_2)
    #print(asyncio.run(extract_job_description.get_job_description()))
    #extract_job_description = LinkedinJobDescription(job_url_3)
    #print(asyncio.run(extract_job_description.get_job_description()))

