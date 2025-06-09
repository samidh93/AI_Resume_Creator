import os
import asyncio
from pyppeteer import launch
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

class LinkedinJobDescription:
    def __init__(self, job_description_url):
        logger.info(f"Initializing LinkedinJobDescription with URL: {job_description_url}")
        self.job_description_url = job_description_url
        self.job_description = None
        self.company_name = None

    def get_job_description(self):
        logger.info("Starting synchronous job description extraction")
        try:
            result = asyncio.run(self.get_job_description_via_pyppeteer())
            logger.info("Synchronous job description extraction completed successfully")
            return result
        except Exception as e:
            logger.error(f"Synchronous job description extraction failed: {e}")
            raise

    async def get_job_description_via_pyppeteer(self):
        logger.info(f"Starting async job description extraction from: {self.job_description_url}")
        browser = None
        
        try:
            # Browser configuration
            headless = os.getenv('CONTAINER', 'false').lower() == 'true'
            args = ['--no-sandbox', '--disable-setuid-sandbox']

            if headless:
                args.append('--headless')
                executable_path = '/usr/bin/chromium'
                logger.debug("Running in container mode with Chromium")
            else:
                executable_path = None
                logger.debug("Running in local mode with default browser")

            logger.info(f'Launching browser... Headless: {headless}')
            browser = await launch(headless=headless, args=args, executablePath=executable_path)
            logger.debug("Browser launched successfully")

            page = await browser.newPage()
            logger.debug("New browser page created")

            logger.info(f'Navigating to job description URL: {self.job_description_url}')
            await page.goto(self.job_description_url, {'waitUntil': 'domcontentloaded'})
            logger.debug('Page loaded successfully')

            # Close modal popup if exists
            try:
                logger.debug("Checking for modal popup")
                await page.waitForSelector('.modal__dismiss', timeout=5000)
                await page.click('.modal__dismiss')
                logger.info('Modal popup closed successfully')
            except Exception:
                logger.debug('No modal dismiss button found or timeout reached')

            # Extract company name
            logger.debug("Extracting company name")
            self.company_name = await self._get_company_name(page)
            logger.info(f'Company name extracted: {self.company_name}')
            
            # Expand full job description if "Show More" button exists
            try:
                logger.debug("Looking for 'Show More' button")
                await page.waitForSelector('.show-more-less-html__button--more', timeout=5000)
                await page.click('.show-more-less-html__button--more')
                logger.info('Job description expanded successfully')
            except Exception:
                logger.debug('No "Show More" button found or timeout reached')

            # Extract job description
            logger.debug("Extracting job description content")
            job_description = await page.evaluate('''() => {
                let desc = document.querySelector('.show-more-less-html__markup');
                return desc ? desc.innerText.trim() : null;
            }''')

            if job_description:
                self.job_description = job_description
                logger.info(f'Job description extracted successfully: {len(job_description)} characters')
            else:
                self.job_description = 'No job description found.'
                logger.warning('No job description content found on the page')

        except Exception as e:
            logger.error(f'Error occurred during job description extraction: {e}', exc_info=True)
            self.job_description = 'Error fetching job description.'
            self.company_name = 'Error fetching company name'

        finally:
            if browser:
                logger.debug("Closing browser and cleaning up processes")
                try:
                    await browser.close()
                    logger.debug("Browser closed successfully")
                except Exception as e:
                    logger.warning(f"Error while closing browser: {e}")

                # Manually kill Chrome processes if necessary
                logger.debug("Killing any remaining browser processes")
                os.system("pkill -f chromium")
                os.system("pkill -f chrome")
                logger.debug("Browser cleanup completed")

        logger.info(f"Job description extraction completed - Company: {self.company_name}, Content: {len(str(self.job_description))} characters")
        return self.job_description, self.company_name

    async def _get_company_name(self, page) -> str | None:
        """Extracts the company name from a LinkedIn job posting."""
        logger.debug("Starting company name extraction")
        
        try:
            # Wait for the company name element to load
            logger.debug("Waiting for company name element")
            await page.waitForSelector("span.topcard__flavor a.topcard__org-name-link")

            # Extract the text content of the company name
            company_name = await page.evaluate('''
                document.querySelector("span.topcard__flavor a.topcard__org-name-link")?.textContent.trim()
            ''')

            if company_name:
                logger.debug(f"Company name successfully extracted: {company_name}")
                return company_name
            else:
                logger.warning("Company name element found but no text content")
                return "Unknown Company"

        except Exception as e:
            logger.error(f"Error extracting company name: {e}")
            return "Error fetching company name"

if __name__ == '__main__':
    job_url_1 = "https://www.linkedin.com/jobs/view/4114686525"
    extract_job_description = LinkedinJobDescription(job_url_1)
    jd, company= extract_job_description.get_job_description()
    print("company: ",company)
    print("job description: ",jd)
