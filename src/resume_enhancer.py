import yaml
from pathlib import Path
from pydantic import BaseModel
from ats_score_prompt import ATSResult  # Assuming ATSResult is in a separate module

class ResumeEnhancer:
    def __init__(self, resume_path: str):
        self.resume_path = Path(resume_path)
        self.resume_data = self._load_resume()
    
    def _load_resume(self) -> dict:
        """Loads the YAML resume file."""
        with open(self.resume_path, 'r') as file:
            return yaml.safe_load(file)
    
    def _save_resume(self):
        """Saves the enhanced resume back to YAML format."""
        with open(self.resume_path, 'w') as file:
            yaml.safe_dump(self.resume_data, file, default_flow_style=False, allow_unicode=True)
    
    def enhance_resume(self, ats_result: ATSResult):
        """Enhances the resume based on ATS findings."""
        self._add_missing_skills(ats_result.missing_skills)
        self._improve_experience(ats_result.suggested_improvements)
        self._add_projects_section(ats_result.missing_skills)
        self._save_resume()
    
    def _add_missing_skills(self, missing_skills: list[str]):
        """Adds missing skills to the Skills section."""
        if "skills" not in self.resume_data:
            self.resume_data["skills"] = []
        
        for skill in missing_skills:
            if skill not in self.resume_data["skills"]:
                self.resume_data["skills"].append(skill)
    
    def _improve_experience(self, suggestions: str):
        """Enhances experience descriptions based on AI suggestions."""
        if "experience" in self.resume_data:
            for job in self.resume_data["experience"]:
                job["enhanced_description"] = suggestions  # Adding improvements suggested by AI
    
    def _add_projects_section(self, missing_skills: list[str]):
        """Adds a Projects section if missing skills require additional demonstration."""
        if "projects" not in self.resume_data:
            self.resume_data["projects"] = []
        
        for skill in missing_skills:
            if skill == "GCP":
                self.resume_data["projects"].append({
                    "name": "Multi-Cloud Deployment Using Terraform",
                    "description": "Designed and deployed a hybrid AWS-GCP cloud architecture using Terraform. Configured automated backup solutions."
                })
            elif skill == "Backup":
                self.resume_data["projects"].append({
                    "name": "Cloud Backup Implementation",
                    "description": "Implemented automated backup and disaster recovery solutions using AWS Backup and GCP Cloud Storage."
                })
    
if __name__ == "__main__":
    resume_path = "input/sami_dhiab_resume.yaml"
    ats_result = ATSResult(
        ats_score=78,
        matched_skills=['AWS', 'Azure', 'Cloud Services', 'Linux', 'Network', 'Monitoring Tools', 'Team Collaboration'],
        missing_skills=['GCP', 'Backup', 'German B2 proficiency', 'Infrastructure Automation'],
        suggested_improvements="Add specific projects or experiences that highlight working in a Multi-Cloud environment and detail any experience with GCP. Ensure to mention your experience with network configurations and backup solutions. Since the job requires a B2 level of German, include any relevant German language training or usage in a professional setting. Incorporate actionable items demonstrating your experience in automating infrastructure operations."
    )
    
    enhancer = ResumeEnhancer(resume_path)
    enhancer.enhance_resume(ats_result)
    print("Resume successfully enhanced!")
