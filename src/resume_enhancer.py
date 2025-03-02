from pathlib import Path
from ruamel.yaml import YAML
from resume_analyzer import ATSResult, ResumeAnalyzer

class ResumeEnhancer:
    def __init__(self, resume_path: str):
        self.resume_path = Path(resume_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.resume_data = self._load_resume()
    
    def _load_resume(self) -> dict:
        """Loads the YAML resume file while preserving order."""
        with open(self.resume_path, 'r') as file:
            return self.yaml.load(file)
    
    def _save_resume(self) -> str:
        """Saves the enhanced resume to a new YAML file with '_ai' suffix."""
        new_resume_path = self.resume_path.with_stem(self.resume_path.stem + "_ai")
        with open(new_resume_path, 'w') as file:
            self.yaml.dump(self.resume_data, file)
        return str(new_resume_path)
    
    def enhance_resume(self, ats_result: ATSResult) -> str:
        """Enhances the resume based on ATS findings while preserving structure and order."""
        self._add_missing_skills(ats_result.missing_skills)
        self._improve_experience(ats_result.suggested_improvements)
        return self._save_resume()
    
    def _add_missing_skills(self, missing_skills: list[str]):
        """Adds missing skills while preserving the existing structure."""
        if "skills" in self.resume_data and isinstance(self.resume_data["skills"], list):
            # Check if skill already exists by name
            existing_skill_names = [skill["name"].lower() for skill in self.resume_data["skills"]]
            
            for skill_name in missing_skills:
                if skill_name.lower() not in existing_skill_names:
                    # Determine appropriate category
                    category = self._determine_skill_category(skill_name)
                    # Add new skill with the same structure
                    new_skill = {
                        "category": category,
                        "name": skill_name,
                        "level": "Intermediate"  # Default level
                    }
                    self.resume_data["skills"].append(new_skill)
    
    def _determine_skill_category(self, skill_name: str) -> str:
        """Determine the appropriate category for a skill."""
        # Simple logic to categorize skills
        if skill_name in ["GCP", "AWS", "Azure"]:
            return "Cloud Services"
        elif skill_name in ["Infrastructure Automation", "Backup"]:
            return "Tools"
        elif "proficiency" in skill_name.lower() or "German" in skill_name:
            return "Languages"
        else:
            return "Other"  # Default category
    
    def _improve_experience(self, suggestions: str):
        """Enhances experience descriptions while preserving the structure."""
        if "experiences" in self.resume_data and isinstance(self.resume_data["experiences"], list):
            # Add the suggestion to the most recent job experience
            if self.resume_data["experiences"]:
                current_job = self.resume_data["experiences"][0]  # Most recent job
                
                # Add a new key_responsibility with the suggestion
                if "key_responsibilities" in current_job and isinstance(current_job["key_responsibilities"], list):
                    # Create a new description entry
                    new_responsibility = {
                        "description": suggestions
                    }
                    current_job["key_responsibilities"].append(new_responsibility)
                
                # Also add to skills_acquired if it exists
                if "skills_acquired" in current_job and isinstance(current_job["skills_acquired"], list):
                    for skill_phrase in suggestions.split('.'):
                        if skill_phrase.strip():
                            relevant_skills = self._extract_relevant_skills(skill_phrase)
                            for skill in relevant_skills:
                                if skill not in current_job["skills_acquired"]:
                                    current_job["skills_acquired"].append(skill)
    
    def _extract_relevant_skills(self, text: str) -> list[str]:
        """Extract relevant skills from a text phrase."""
        relevant_skills = []
        potential_skills = [
            "Multi-Cloud", "GCP", "Network Configuration", 
            "Backup Solutions", "Infrastructure Automation"
        ]
        
        for skill in potential_skills:
            if skill.lower() in text.lower():
                relevant_skills.append(skill)
                
        return relevant_skills

if __name__ == "__main__":
    resume_path = "input/sami_dhiab_resume.yaml"
    ats_result = ATSResult(
        ats_score=78,
        matched_skills=['AWS', 'Azure', 'Cloud Services', 'Linux', 'Network', 'Monitoring Tools', 'Team Collaboration'],
        missing_skills=['GCP', 'Backup', 'German B2 proficiency', 'Infrastructure Automation'],
        suggested_improvements="Add specific projects or experiences that highlight working in a Multi-Cloud environment and detail any experience with GCP. Ensure to mention your experience with network configurations and backup solutions. Since the job requires a B2 level of German, include any relevant German language training or usage in a professional setting. Incorporate actionable items demonstrating your experience in automating infrastructure operations."
    )
    
    enhancer = ResumeEnhancer(resume_path)
    new_resume_path = enhancer.enhance_resume(ats_result)
    print(f"Resume successfully enhanced and saved at: {new_resume_path}")