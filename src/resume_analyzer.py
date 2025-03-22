import openai
import json 
import yaml
from pathlib import Path
from pydantic import BaseModel
from resume_parser import ResumeParser
from job_description_interface import JobDescriptionInterface
from resume_parser import ResumeParser
import re
from ai_interface import AIInterface

class ATSResult(BaseModel):
    ats_score: int
    #matched_skills: list[str]
    missing_skills: list[dict]
    suggested_improvements: str

class ResumeAnalyzer:
    def __init__(self,  job_description:str, resume:ResumeParser):
        #openai.api_key = api_key
        # Create the AI interface
        self.model = AIInterface(
                model_provider="ollama",
                model_name="qwen2.5:3b",
                temperature=0,
                #max_tokens=100,
                format="json"
            )
        self.matched_skills = []
        self.missing_skills = []
        self.suggested_improvements = ""
        self.job_description_text = re.sub(r'\s+', ' ', job_description).strip()
        self.resume_text = resume.get_required_fields_for_ats()

    def compare(self) -> ATSResult:
        """Calculate the ATS score for the resume based on the job description."""
        prompt = f"""
        You are an Applicant Tracking System (ATS) that evaluates resumes against job descriptions.

        Assess the following resume based on:
        - Keyword matching
        - Skill relevance
        - Experience alignment
        - Formatting suitability

        Return **only** a JSON object with the following structure:
        ```json
        {{
            "ats_score": <numeric_value_between_0_and_100>,
            "missing_skills": [
                {{"category": "Programming Languages", "name": "Python", "level": "Advanced"}},  
                ...
            ], 
            "suggested_improvements": "Detailed suggestions on how to improve the resume."
        }}
        ```

        **Job Description:**
        {self.job_description_text}

        **Resume:**
        {self.resume_text}
        """

        print(prompt)  # Debugging (Remove in production)
        
        #response = openai.chat.completions.create(
        #    model="gpt-4o-mini",
        #    response_format={"type": "json_object"},
        #    temperature=0,  # Ensures consistent results
        #    messages=[
        #        {"role": "system", "content": "You are an ATS expert evaluating resumes for compatibility."},
        #        {"role": "user", "content": prompt}
        #    ]
        #)
        #response_content = response.choices[0].message.content
        messages=[
                {"role": "system", "content": "You are an ATS expert evaluating resumes for compatibility."},
                {"role": "user", "content": prompt}
            ]
        response_content = self.model.get_completion(messages)
        return ATSResult(**json.loads(response_content))


if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    #secrets = yaml.safe_load(open(secrets_path, 'r'))
    #api_key = secrets['api_key']
    resume = ResumeParser("input/sami_dhiab_resume.yaml")
    job_desc = """"
About the job
Du willst:



- arbeiten und verdienen wie ein Selbstständiger, aber risikofrei in Deutschland angestellt sein?

- Deine Arbeitszeiten selbst bestimmen?

- von zuhause aus arbeiten (remote)?

- den nächsten Schritt in Deiner Karriere gehen und lernen wie Vertrieb funktioniert und wie man sein eigenes Kundenportfolio aufbaut?

- Deine eigenen Produktideen im Team vorstellen und die technische Umsetzung verantworten?

- einen Arbeitgeber, der Dich leistungs- und ergebnisorientiert bezahlt (realistische Gehaltsrange im 1. Jahr inkl. Bonus: 130.000€ - 150.000€)?

- Dein Gehalt über Deine eigene Leistung selbst steuern können (Dein Bonus ist bei uns ungedeckelt -> Wir lieben das Leistungsprinzip, weil es fair ist und uns täglich motiviert)?

- die Möglichkeit haben, Dich über Mitarbeiterbeteiligungsprogramme am unternehmerischen Erfolg zu beteiligen?

- in einem Team arbeiten, welches Dich immer unterstützt und Dir dabei hilft Deine persönlichen Wachstumsziele zu erreichen?



Du:



- hast 8+ Jahre Erfahrung im Bereich DevOps & Cloud-Infrastruktur?

- entwickelst und automatisierst Cloud-Native-Infrastrukturen in AWS, Azure oder GCP?

- hast tiefes Know-how in IaC, Containerization, CI/CD, Monitoring & Security und siehst Dich als Experten?

- bist kommunikationsfreudig und arbeitest gerne mit Kunden zusammen?

- bist bereit als Projektleiter Verantwortung für Deine Kunden zu übernehmen?

- bist gesegnet mit einem Growth Mindset und willst immer weiterkommen?

- bist überzeugt, dass Dein Potenzial noch lange nicht ausgeschöpft ist?



Dann melde Dich bei uns!



Wir sind eine Gruppe von jungen und hungrigen Entwicklern, die gemeinsam die Firma betreiben, in der wir immer arbeiten wollten, die aber nicht existent war!



Wir:



- unterstützen unsere Kunden in Software Development und DevOps-Projekten

- bauen Startups und gründen sie aus

- geben Vollgas und gestalten unsere Firma 

- sind ein geiles Team



LET’S ROCK!
    """
    ra = ResumeAnalyzer( job_desc, resume)
    ats_result = ra.compare()
    print(f"ATS Score: {ats_result.ats_score}")
    #print(f"Matched Skills: {ats_result.matched_skills}")
    print(f"Missing Skills: {ats_result.missing_skills}")
    print(f"Suggested Improvements: {ats_result.suggested_improvements}")
