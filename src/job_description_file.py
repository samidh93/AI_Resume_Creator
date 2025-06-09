# interface to get the correct job description based on url
import os
from pathlib import Path
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

class JobDescriptionFile:
    def __init__(self, file_path):
        logger.info(f"Initializing JobDescriptionFile with file path: {file_path}")
        self.job_description_file = Path(file_path)
        self.job_description = None
        
        # Validate file path
        if not self.job_description_file.exists():
            logger.warning(f"Job description file does not exist: {file_path}")
        else:
            logger.debug(f"Job description file found: {file_path}")
    
    def get_job_description_from_file(self):
        logger.info(f"Reading job description from file: {self.job_description_file}")
        
        try:
            if not self.job_description_file.exists():
                logger.error(f"Job description file not found: {self.job_description_file}")
                return None, None
                
            with open(self.job_description_file, "r", encoding='utf-8') as f:
                job_description = f.read()
                company_name = self.job_description_file.stem
                
                logger.info(f"Successfully read job description from file:")
                logger.info(f"  - Company: {company_name}")
                logger.info(f"  - Content length: {len(job_description)} characters")
                
                return job_description, company_name
                
        except FileNotFoundError:
            logger.error(f"Job description file not found: {self.job_description_file}")
            return None, None
        except PermissionError:
            logger.error(f"Permission denied reading file: {self.job_description_file}")
            return None, None
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error reading file {self.job_description_file}: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected error reading job description file {self.job_description_file}: {e}")
            return None, None
       
if __name__ == '__main__':
    job_description_obj = JobDescriptionFile("/Users/sami/dev/AutoApplyApp/AI_Resume_Creator/output/jobs/eviden.txt")
    jd, company= job_description_obj.get_job_description_from_file()
    print("company name: ",company)
    print("job description: ",jd)
