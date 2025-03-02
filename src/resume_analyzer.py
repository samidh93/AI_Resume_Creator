import openai
import json 
import yaml
from pathlib import Path
from pydantic import BaseModel
from resume_parser import ResumeParser
from job_description_interface import JobDescriptionInterface
from resume_parser import ResumeParser
import re
class ATSResult(BaseModel):
    ats_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    suggested_improvements: str

class ResumeAnalyzer:
    def __init__(self, api_key, job_description:str, resume:ResumeParser):
        openai.api_key = api_key
        self.matched_skills = []
        self.missing_skills = []
        self.suggested_improvements = ""
        self.job_description_text = re.sub(r'\s+', ' ', job_description).strip()
        self.resume_text = resume.get_required_fields_for_ats()

    def compare(self) -> ATSResult:
        """Calculate the ATS score for the resume based on the job description."""
        prompt = f"""
                You are an Applicant Tracking System (ATS) that evaluates resumes based on job descriptions.
                Compare the following resume against the job description and calculate an ATS compatibility score.
                The score should be based on keyword matching, skill relevance, experience alignment, and formatting suitability.
                
                Provide the response in JSON format with the following keys:
                ###
                    "ats_score": <numeric_value_between_0_and_100>,
                    "matched_skills": ["skill1", "skill2", ...],
                    "missing_skills": ["skillA", "skillB", ...],
                    "suggested_improvements": "Detailed suggestions on how to improve the resume."
                ###

                Job Description:
                {self.job_description_text}
                
                Resume:
                {self.resume_text}
                
                Return only the JSON output without any explanation.
                """
        print(prompt)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=0,  # Ensures consistent results
            messages=[
                {"role": "system", "content": "You are an expert that evaluates resumes for ATS compatibility."},
                {"role": "user", "content": prompt}
            ]
        )

        response = response.choices[0].message.content
        return ATSResult(**json.loads(response))

if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    secrets = yaml.safe_load(open(secrets_path, 'r'))
    api_key = secrets['api_key']
    resume = ResumeParser("input/sami_dhiab_resume.yaml")
    job_url_1 = "https://www.linkedin.com/jobs/view/4114686525"
    job_description_obj = JobDescriptionInterface(job_url_1)
    job_desc = job_description_obj.get_job_description(load_from_file=True, save_to_file=True)
    ra = ResumeAnalyzer(api_key, job_desc, resume)
    ats_result = ra.compare()
    print(f"ATS Score: {ats_result.ats_score}")
    print(f"Matched Skills: {ats_result.matched_skills}")
    print(f"Missing Skills: {ats_result.missing_skills}")
    print(f"Suggested Improvements: {ats_result.suggested_improvements}")
