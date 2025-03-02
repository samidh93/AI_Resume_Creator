# interface to get the correct job description based on url
import asyncio
from linkedin_job_description import LinkedinJobDescription

class JobDescriptionInterface:
    def __init__(self, job_description_url):
        self.job_description_url = job_description_url
        self.job_id = None
        self.job_description = None

    def get_job_description(self, load_from_file=False, save_to_file=False, job_dir="output/jobs"):
        # return the coroutine 
        platform = self.detect_the_platform()
        if load_from_file:
            try:
                with open(f"{job_dir}/{self.job_id}.txt", "r") as f:
                    job_description = f.read()
                    return job_description
            except FileNotFoundError:
                pass
        job_description =  platform.get_job_description()
        if save_to_file:
            with open(f"{job_dir}/{self.job_id}.txt", "w") as f:
                f.write(job_description)
        return job_description
    
    def detect_the_platform(self):
        if self.job_description_url.startswith("https://www.linkedin.com/jobs"):
            self.job_id = self.job_description_url.split("/")[-1]
            return LinkedinJobDescription(self.job_description_url)
        else:
            return None

if __name__ == '__main__':
    job_url_1 = "https://www.linkedin.com/jobs/view/4114686525"
    job_description_obj = JobDescriptionInterface(job_url_1)
    jd= job_description_obj.get_job_description(load_from_file=True, save_to_file=True)
    print("job description: ",jd)