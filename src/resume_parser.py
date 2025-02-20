import yaml

class ResumeParser:
    """Loads and parses resume data from a YAML file."""

    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.data = self._load_yaml()

    def _load_yaml(self):
        """Load YAML data from file."""
        with open(self.yaml_file, "r") as file:
            return yaml.safe_load(file)

    def get_resume_summary(self):
        """Combine sections into plain text for ATS analysis."""
        return f"{self.data['summary']} " 

    def get_resume_experiences(self):
        """Combine sections into plain text for ATS analysis."""
        skills_aqc= [exp["skills_acquired"] for exp in self.data["experiences"]]
        # Flatten the list
        flat_list = [skill for sublist in skills_aqc for skill in sublist]

        # Join into a single string
        return ", ".join(flat_list)

    def get_resume_skills(self):
        """Combine sections into plain text for ATS analysis."""
        skills = self.data['skills']
        flat_list = [skill['name'] for skill in skills]
        return ", ".join(flat_list)
    
    def update_summary(self, new_summary):
        """Update the resume summary."""
        self.data["summary"] = new_summary
