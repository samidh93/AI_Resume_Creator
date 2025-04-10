import yaml

class ResumeParser:
    """Loads and parses resume data from a YAML file."""

    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.data = self._load_yaml()
        self.text = self._load_plain_text()

    def _load_yaml(self):
        """Load YAML data from file."""
        with open(self.yaml_file, "r") as file:
            return yaml.safe_load(file)
    def _load_plain_text(self):
        """Load plain text data from file."""
        with open(self.yaml_file, "r") as file:
            return file.read()

    def get_resume_summary(self):
        """Combine sections into plain text for ATS analysis."""
        return f"{self.data['summary']} " 

    def get_resume_languages(self):
        """Combine sections into plain text for ATS analysis."""
        return f"{self.data['languages']}"  

    
    def get_resume_experiences_skills_acquired(self):
        """Combine sections into plain text for ATS analysis."""
        skills_aqc= [exp["skills_acquired"] for exp in self.data["experiences"]]
        return f"{[skill for sublist in skills_aqc for skill in sublist]}"


    def get_resume_skills(self):
        """Combine sections into plain text for ATS analysis."""
        return f"{self.data['skills']}"

    def get_resume_project_skills(self):
        """Combine sections into plain text for ATS analysis."""
        projects = self.data['projects']
        try:
            return f"{[proj['skills'] for proj in projects]}"
        except KeyError:
            return ""

    def get_resume_interests(self):
        """Combine sections into plain text for ATS analysis."""
        return f"{self.data['interests']}"

    def get_required_fields_for_ats(self):
        """Combine sections into plain text for ATS analysis."""
        return "\n".join((
            "summary: ",
            self.get_resume_summary(),
            "experiences skills_acquired: ",
            self.get_resume_experiences_skills_acquired(),
            "skills: ",
            self.get_resume_skills(),
            "languages: ",
            self.get_resume_languages(),
            "side project skills: ",
            self.get_resume_project_skills(),
            "interests: ",
            self.get_resume_interests()
        ))


    def update_summary(self, new_summary):
        """Update the resume summary."""
        self.data["summary"] = new_summary
    
    def update_skills(self, new_skills:list):
        """Update the resume skills."""
        # append the skills to the previous skills
        self.data["skills"] += new_skills
        #skills = self.data['skills']
        #flat_list = [skill['name'] for skill in skills]
        #return ", ".join(flat_list)

if __name__ == "__main__":
    resume_parser = ResumeParser("input/sami_dhiab_resume.yaml")
    print(resume_parser.get_resume_summary())
    print(resume_parser.get_resume_experiences_skills_acquired())
    print(resume_parser.get_resume_skills())
    print(resume_parser.get_resume_project_skills())
    print(resume_parser.get_resume_interests())