# interface to get the correct job description based on url
import asyncio
import linkedin_job_description

class JobDescriptionInterface:
    def __init__(self, job_description_url):
        self.job_description_url = job_description_url
    
    def get_text_job_description(self):
        # return the coroutine 
        platform = self.detect_the_platform()
        return asyncio.get_event_loop().run_until_complete(platform.get_text_job_description_with_pyppeteer())

    def detect_the_platform(self):
        if self.job_description_url.startswith("https://www.linkedin.com/jobs"):
            return linkedin_job_description.LinkedinJobDescription(self.job_description_url)
        else:
            return None

if __name__ == '__main__':
    job_url_1 = "https://www.linkedin.com/jobs/view/4117398597"
    job_description_obj = JobDescriptionInterface(job_url_1)
    print(job_description_obj.get_text_job_description())