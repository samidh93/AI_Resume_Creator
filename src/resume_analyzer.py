import openai
import json 
import yaml
from pathlib import Path
from resume_parser import ResumeParser
from job_description_interface import JobDescriptionInterface
class ResumeAnalyzer:

    def __init__(self, api_key):
        self.api_key = api_key

    def calculate_ats_score(self, job_description, resume_content):
        """Calculate the ATS score for the resume based on the job description."""
        prompt = f"""
        You are an Applicant Tracking System (ATS) that evaluates resumes based on job descriptions.
        Compare the following resume against the job description and calculate an ATS compatibility score.
        The score should be based on keyword matching, skill relevance, experience alignment, and formatting suitability.
        
        Provide the response in JSON format with the following key:
        {{
            "ats_score": <numeric_value_between_0_and_100>
        }}

        Job Description:
        """
        {job_description}
        """
        
        Resume:
        """
        {resume_content}
        """
        
        Return only the JSON output without any explanation.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an AI that evaluates resumes for ATS compatibility."},
                {"role": "user", "content": prompt}
            ]
        )

        response = response.choices[0].message.content
        return json.loads(response)['ats_score']

if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    secrets = yaml.safe_load(open(secrets_path, 'r'))
    api_key = secrets['api_key']
    resume = ResumeParser("input/sami_dhiab_resume.yaml")
    job_url_1 = "https://www.linkedin.com/jobs/view/4121332725"
    job_description_obj = JobDescriptionInterface(job_url_1)
    job_desc=job_description_obj.get_job_description()
    ra= ResumeAnalyzer(api_key=api_key)
    ats_score = ra.calculate_ats_score(job_desc,resume.text)
    print(f"ATS Score: {ats_score}")
