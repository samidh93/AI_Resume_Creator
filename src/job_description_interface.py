# interface to get the correct job description based on url
import asyncio
from linkedin_job_description import LinkedinJobDescription
import os
from pathlib import Path
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

class JobDescriptionInterface:
    def __init__(self, job_description_url):
        logger.info(f"Initializing JobDescriptionInterface with URL: {job_description_url}")
        self.job_description_url = job_description_url
        self.job_id = None
        self.job_description = None

    def get_job_description(self, load_from_file=False, save_to_file=False, job_dir="../output/jobs"):
        logger.info(f"Getting job description - load_from_file: {load_from_file}, save_to_file: {save_to_file}")
        
        # return the coroutine 
        platform = self.detect_the_platform()
        if not platform:
            logger.error("No supported platform detected for the provided URL")
            raise ValueError("Unsupported job description URL platform")
        
        # full path to the job dir
        job_dir = Path(__file__).parent / job_dir
        job_file = Path(f"{job_dir}/{self.job_id}.txt")
        logger.debug(f"Job file path: {job_file}")
        
        if load_from_file:
            logger.debug("Attempting to load job description from file")
            try:
                # check if job_file exists
                if os.path.exists(job_file):
                    logger.info(f"Loading job description from existing file: {job_file}")
                    with open(job_file, "r") as f:
                        company_name = f.readline().strip()
                        job_description = f.read()
                        logger.info(f"Successfully loaded job description from file - Company: {company_name}, Length: {len(job_description)} characters")
                        return job_description, company_name
                else:
                    logger.debug(f"Job file does not exist: {job_file}")
            except FileNotFoundError:
                logger.warning(f"Job file not found: {job_file}")
            except Exception as e:
                logger.error(f"Error reading job file {job_file}: {e}")
        
        logger.info("Fetching job description from platform")
        try:
            job_description, company_name = platform.get_job_description()
            logger.info(f"Successfully fetched job description - Company: {company_name}, Length: {len(job_description)} characters")
        except Exception as e:
            logger.error(f"Failed to fetch job description from platform: {e}")
            raise
        
        if save_to_file:
            logger.info(f"Saving job description to file: {job_file}")
            try:
                # Ensure directory exists
                job_dir.mkdir(parents=True, exist_ok=True)
                
                with open(job_file, "w") as f:
                    f.write(company_name + "\n" + job_description)
                logger.info(f"Successfully saved job description to file: {job_file}")
            except Exception as e:
                logger.error(f"Failed to save job description to file {job_file}: {e}")
        
        return job_description, company_name
    
    def detect_the_platform(self):
        logger.debug(f"Detecting platform for URL: {self.job_description_url}")
        
        if self.job_description_url.startswith("https://www.linkedin.com/jobs"):
            self.job_id = self.job_description_url.split("/")[-1]
            logger.info(f"Detected LinkedIn platform - Job ID: {self.job_id}")
            return LinkedinJobDescription(self.job_description_url)
        else:
            logger.warning(f"No supported platform detected for URL: {self.job_description_url}")
            return None

if __name__ == '__main__':
    job_url_1 = "https://www.linkedin.com/jobs/view/4114686525"
    job_description_obj = JobDescriptionInterface(job_url_1)
    jd= job_description_obj.get_job_description(load_from_file=True, save_to_file=True)
    print("job description: ",jd)