import os
import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth

class LinkedinJobDescription:
    def __init__(self, job_description_url):
        self.job_description_url = job_description_url
        self.job_description = None

    def get_job_description(self):
        return asyncio.run(self.get_job_description_via_pyppeteer())


    async def get_job_description_via_pyppeteer(self):
        browser = None
        try:
            print('Launching Chromium...')
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = await browser.newPage()
            await stealth(page)

            print(f'Fetching job description from: {self.job_description_url}')
            await page.goto(self.job_description_url, {'waitUntil': 'domcontentloaded'})

            print('Page loaded, waiting for job description...')

            # Close modal popup if exists
            try:
                await page.waitForSelector('.modal__dismiss', timeout=5000)
                await page.click('.modal__dismiss')
                print('Closed modal popup.')
            except Exception:
                print('No dismiss button found.')

            # Expand full job description if "Show More" button exists
            try:
                await page.waitForSelector('.show-more-less-html__button--more', timeout=5000)
                await page.click('.show-more-less-html__button--more')
                print('Expanded full job description.')
            except Exception:
                print('No "Show More" button found.')

            # Extract job description
            job_description = await page.evaluate('''() => {
                let desc = document.querySelector('.show-more-less-html__markup');
                return desc ? desc.innerText.trim() : null;
            }''')

            self.job_description = job_description if job_description else None
            print('Job description fetched successfully.')

        except Exception as e:
            print('An error occurred:', e)
            self.job_description = 'Error fetching job description.'

        finally:
            if browser:
                print("Closing browser and terminating all processes...")
                try:
                    await browser.close()
                except Exception as e:
                    print(f"Error while closing browser: {e}")

                # Manually kill Chrome processes if necessary
                os.system("pkill -f chromium")
                os.system("pkill -f chrome")

            print('Browser closed.')
        return self.job_description

if __name__ == '__main__':
    job_url_1 = "https://www.linkedin.com/jobs/view/4114686525"
    extract_job_description = LinkedinJobDescription(job_url_1)
    jd= extract_job_description.get_job_description()
    print("job description: ",jd)
