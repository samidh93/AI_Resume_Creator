from pathlib import Path
from ruamel.yaml import YAML
from resume_analyzer import ATSResult
import openai
import yaml
import json
class ResumeEnhancer:
    def __init__(self, api_key, resume_path: str, company_name: str):
        openai.api_key = api_key
        self.resume_path = Path(resume_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.resume_data = self._load_resume()
        self.company_name = company_name
    
    def _load_resume(self) -> dict:
        """Loads the YAML resume file while preserving order."""
        with open(self.resume_path, 'r') as file:
            return self.yaml.load(file)
    
    def _save_resume(self) -> str:
        """Saves the enhanced resume to a new YAML file with '_ai' suffix."""
        new_resume_path = self.resume_path.with_stem(self.resume_path.stem + "_" + self.company_name)
        with open(new_resume_path, 'w') as file:
            self.yaml.dump(self.resume_data, file)
        return str(new_resume_path)
    
    def enhance_resume(self, ats_result: ATSResult) -> str:
        """Enhances the resume based on ATS findings while preserving structure and order."""
        self._add_missing_skills(ats_result.missing_skills)
        self._update_summary(ats_result)
        return self._save_resume()
    
    def _update_summary(self, ats_result: ATSResult):
        """Updates the summary section of the resume."""
        prompt = f"""
                improve this summary by naturally incorproating the following missing skills and suggested improvements.

                Summary:
                {self.resume_data["summary"]}
                
                missing_skills: {ats_result.missing_skills}
                suggested_improvements: {ats_result.suggested_improvements}
                
                Return only the JSON output without any explanation. 
                Key is summary and value is the updated summary.
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
        self.resume_data["summary"] = json.loads(response)["summary"]

    def _add_missing_skills(self, missing_skills: list[str]):
        """Adds missing skills while preserving the existing structure."""
        if "skills" in self.resume_data and isinstance(self.resume_data["skills"], list):
            # Check if skill already exists by name
            existing_skill_names = [skill["name"].lower() for skill in self.resume_data["skills"]]
            
            for skill in missing_skills:
                if skill["name"].lower() not in existing_skill_names:
                    # Determine appropriate category
                    self.resume_data["skills"].append(skill)
  

if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    secrets = yaml.safe_load(open(secrets_path, 'r'))
    api_key = secrets['api_key']
    resume_path = "input/sami_dhiab_resume.yaml"
    ats_result = ATSResult(
            ats_score=65
            ,missing_skills=[{'category': 'Programming Languages', 'name': 'C#', 'level': 'Advanced'}, {'category': 'Frameworks', 'name': 'Angular', 'level': 'Intermediate'}, {'category': 'Tools', 'name': 'Azure DevOps', 'level': 'Intermediate'}, {'category': 'Methodologies', 'name': 'SCRUM', 'level': 'Advanced'}]
            ,suggested_improvements="1. Include specific experience with C# and .Net, as these are critical for the role. 2. Highlight any experience with Angular and Azure DevOps, as these are mentioned in the job description. 3. Emphasize leadership experience and any direct involvement in SaaS product development. 4. Ensure that the resume is formatted clearly with distinct sections for skills, experience, and education to improve readability for ATS."
            )
    
    enhancer = ResumeEnhancer(api_key, resume_path)
    new_resume_path = enhancer.enhance_resume(ats_result)
    print(f"Resume successfully enhanced and saved at: {new_resume_path}")