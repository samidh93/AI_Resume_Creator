# interface to get the correct job description based on url
import asyncio
from linkedin_job_description import LinkedinJobDescription

class JobDescriptionInterface:
    def __init__(self, job_description_url):
        self.job_description_url = job_description_url
    
    def get_job_description(self):
        # return the coroutine 
        platform = self.detect_the_platform()
        return platform.get_job_description()

    def detect_the_platform(self):
        if self.job_description_url.startswith("https://www.linkedin.com/jobs"):
            return LinkedinJobDescription(self.job_description_url)
        else:
            return None

if __name__ == '__main__':
    job_url_1 = "https://www.linkedin.com/jobs/view/4117398597"
    job_description_obj = JobDescriptionInterface(job_url_1)
    print(job_description_obj.get_job_description())