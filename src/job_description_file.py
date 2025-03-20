# interface to get the correct job description based on url
import os
from pathlib import Path

class JobDescriptionFile:
    def __init__(self, file_path):
        self.job_description_file = Path(file_path)
        self.job_description = None
    
    def get_job_description_from_file(self):
        try:
            with open(self.job_description_file, "r") as f:
                job_description = f.read()
                company_name = self.job_description_file.stem
                return job_description, company_name
        except FileNotFoundError:
            return None
       
if __name__ == '__main__':
    job_description_obj = JobDescriptionFile("/Users/sami/dev/AutoApplyApp/AI_Resume_Creator/output/jobs/eviden.txt")
    jd, company= job_description_obj.get_job_description_from_file()
    print("company name: ",company)
    print("job description: ",jd)
