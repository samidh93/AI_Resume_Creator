import yaml
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

class ResumeParser:
    """Loads and parses resume data from a YAML file."""

    def __init__(self, yaml_file):
        logger.info(f"Initializing ResumeParser with file: {yaml_file}")
        self.yaml_file = yaml_file
        try:
            self.data = self._load_yaml()
            self.text = self._load_plain_text()
            logger.info(f"Successfully loaded resume data from {yaml_file}")
        except Exception as e:
            logger.error(f"Failed to initialize ResumeParser: {e}")
            raise

    def _load_yaml(self):
        """Load YAML data from file."""
        logger.debug(f"Loading YAML data from {self.yaml_file}")
        try:
            with open(self.yaml_file, "r") as file:
                data = yaml.safe_load(file)
                logger.debug(f"Successfully loaded YAML data with {len(data)} top-level keys")
                return data
        except FileNotFoundError:
            logger.error(f"YAML file not found: {self.yaml_file}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {self.yaml_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading YAML file {self.yaml_file}: {e}")
            raise

    def _load_plain_text(self):
        """Load plain text data from file."""
        logger.debug(f"Loading plain text from {self.yaml_file}")
        try:
            with open(self.yaml_file, "r") as file:
                text = file.read()
                logger.debug(f"Successfully loaded {len(text)} characters of plain text")
                return text
        except Exception as e:
            logger.error(f"Error loading plain text from {self.yaml_file}: {e}")
            raise

    def get_resume_summary(self):
        """Combine sections into plain text for ATS analysis."""
        logger.debug("Extracting resume summary")
        try:
            summary = f"{self.data['summary']}"
            logger.debug(f"Successfully extracted summary: {len(summary)} characters")
            return summary
        except KeyError:
            logger.warning("Summary field not found in resume data")
            return ""
        except Exception as e:
            logger.error(f"Error extracting resume summary: {e}")
            return ""

    def get_resume_languages(self):
        """Combine sections into plain text for ATS analysis."""
        logger.debug("Extracting resume languages")
        try:
            languages = f"{self.data['languages']}"
            logger.debug(f"Successfully extracted languages: {languages}")
            return languages
        except KeyError:
            logger.warning("Languages field not found in resume data")
            return ""
        except Exception as e:
            logger.error(f"Error extracting resume languages: {e}")
            return ""

    def get_resume_experiences_skills_acquired(self):
        """Combine sections into plain text for ATS analysis."""
        logger.debug("Extracting skills acquired from experiences")
        try:
            skills_aqc = [exp["skills_acquired"] for exp in self.data["experiences"]]
            flattened_skills = [skill for sublist in skills_aqc for skill in sublist]
            logger.debug(f"Successfully extracted {len(flattened_skills)} skills from experiences")
            return f"{flattened_skills}"
        except KeyError as e:
            logger.warning(f"Required field not found in experiences: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error extracting experience skills: {e}")
            return ""

    def get_resume_skills(self):
        """Combine sections into plain text for ATS analysis."""
        logger.debug("Extracting resume skills")
        try:
            skills = f"{self.data['skills']}"
            logger.debug(f"Successfully extracted skills: {len(str(skills))} characters")
            return skills
        except KeyError:
            logger.warning("Skills field not found in resume data")
            return ""
        except Exception as e:
            logger.error(f"Error extracting resume skills: {e}")
            return ""

    def get_resume_project_skills(self):
        """Combine sections into plain text for ATS analysis."""
        logger.debug("Extracting project skills")
        try:
            projects = self.data['projects']
            project_skills = [proj['skills'] for proj in projects]
            logger.debug(f"Successfully extracted skills from {len(projects)} projects")
            return f"{project_skills}"
        except KeyError:
            logger.warning("Projects field or skills subfield not found in resume data")
            return ""
        except Exception as e:
            logger.error(f"Error extracting project skills: {e}")
            return ""

    def get_resume_interests(self):
        """Combine sections into plain text for ATS analysis."""
        logger.debug("Extracting resume interests")
        try:
            interests = f"{self.data['interests']}"
            logger.debug(f"Successfully extracted interests: {interests}")
            return interests
        except KeyError:
            logger.warning("Interests field not found in resume data")
            return ""
        except Exception as e:
            logger.error(f"Error extracting resume interests: {e}")
            return ""

    def get_required_fields_for_ats(self):
        """Combine sections into plain text for ATS analysis."""
        logger.info("Combining all resume fields for ATS analysis")
        try:
            combined_text = "\n".join((
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
            logger.info(f"Successfully combined resume fields: {len(combined_text)} characters")
            return combined_text
        except Exception as e:
            logger.error(f"Error combining resume fields for ATS: {e}")
            return ""

    def update_summary(self, new_summary):
        """Update the resume summary."""
        logger.info(f"Updating resume summary to: {new_summary[:50]}...")
        try:
            old_summary = self.data.get("summary", "")
            self.data["summary"] = new_summary
            logger.info(f"Successfully updated summary from {len(old_summary)} to {len(new_summary)} characters")
        except Exception as e:
            logger.error(f"Error updating resume summary: {e}")
            raise
    
    def update_skills(self, new_skills: list):
        """Update the resume skills."""
        logger.info(f"Adding {len(new_skills)} new skills to resume")
        try:
            original_count = len(self.data.get("skills", []))
            self.data["skills"] += new_skills
            new_count = len(self.data["skills"])
            logger.info(f"Successfully updated skills from {original_count} to {new_count} items")
        except Exception as e:
            logger.error(f"Error updating resume skills: {e}")
            raise

if __name__ == "__main__":
    resume_parser = ResumeParser("input/sami_dhiab_resume.yaml")
    print(resume_parser.get_resume_summary())
    print(resume_parser.get_resume_experiences_skills_acquired())
    print(resume_parser.get_resume_skills())
    print(resume_parser.get_resume_project_skills())
    print(resume_parser.get_resume_interests())