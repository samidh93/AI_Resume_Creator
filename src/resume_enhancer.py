from pathlib import Path
from ruamel.yaml import YAML
from resume_analyzer import ATSResult
import openai
import yaml
import json
from ai_interface import AIInterface
import logging
import re

# Set up logger for this module
logger = logging.getLogger(__name__)

class ResumeEnhancer:
    def __init__(self, resume_path: str, company_name: str, job_title: str = ""):
        logger.info(f"Initializing ResumeEnhancer for resume: {resume_path}, company: {company_name}, job: {job_title}")
        
        try:
            # Create the AI interface
            self.model = AIInterface(
                    model_provider="ollama",
                    model_name="qwen2.5:3b",
                    temperature=0,
                    format="json"
                )
            logger.info("AI interface initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI interface: {e}")
            raise
            
        self.resume_path = Path(resume_path)
        self.company_name = company_name
        self.job_title = job_title
        
        try:
            self.yaml = YAML()
            self.yaml.preserve_quotes = True
            self.yaml.indent(mapping=2, sequence=4, offset=2)
            logger.debug("YAML processor configured")
            
            self.resume_data = self._load_resume()
            logger.info("ResumeEnhancer initialization completed successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ResumeEnhancer: {e}")
            raise
    
    def _load_resume(self) -> dict:
        """Loads the YAML resume file while preserving order."""
        logger.debug(f"Loading resume from {self.resume_path}")
        try:
            with open(self.resume_path, 'r') as file:
                data = self.yaml.load(file)
                logger.info(f"Successfully loaded resume with {len(data)} top-level sections")
                return data
        except FileNotFoundError:
            logger.error(f"Resume file not found: {self.resume_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading resume file {self.resume_path}: {e}")
            raise

    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename by replacing spaces and removing special characters."""
        # Replace spaces with underscores and remove special characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', text)  # Remove invalid filename chars
        sanitized = re.sub(r'\s+', '_', sanitized)      # Replace spaces with underscores
        return sanitized

    def _validate_summary(self, summary_text: str) -> str:
        """Validate and clean the AI-generated summary to remove meta-commentary."""
        logger.debug("Validating AI-generated summary for meta-commentary")
        
        # Define forbidden phrases that indicate meta-commentary
        forbidden_phrases = [
            "ats score", "enhance your", "could further", "would improve",
            "highlighting experience", "apis could", "technologies like",
            "further enhance", "ats compatibility", "resume optimization",
            "keyword optimization", "improve your chances"
        ]
        
        cleaned_summary = summary_text.strip()
        original_length = len(cleaned_summary)
        
        # Check for and remove sentences containing forbidden phrases
        sentences = cleaned_summary.split('. ')
        filtered_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            contains_forbidden = any(phrase in sentence_lower for phrase in forbidden_phrases)
            
            if contains_forbidden:
                logger.warning(f"Removing meta-commentary sentence: '{sentence[:50]}...'")
            else:
                filtered_sentences.append(sentence)
        
        # Reconstruct the summary
        if filtered_sentences:
            cleaned_summary = '. '.join(filtered_sentences)
            # Ensure proper ending punctuation
            if not cleaned_summary.endswith('.'):
                cleaned_summary += '.'
        else:
            logger.warning("All sentences contained meta-commentary, keeping original summary")
            return self.resume_data.get("summary", "")
        
        logger.info(f"Summary validation completed: {original_length} -> {len(cleaned_summary)} characters")
        return cleaned_summary
    
    def _filter_relevant_skills(self, missing_skills: list, job_description_text: str = "") -> list:
        """Filter missing skills to only include those relevant to the job description."""
        logger.debug(f"Filtering {len(missing_skills)} missing skills for relevance")
        
        if not job_description_text:
            # If no job description provided, return all skills
            logger.debug("No job description provided, returning all missing skills")
            return missing_skills
        
        relevant_skills = []
        job_description_lower = job_description_text.lower()
        
        for skill in missing_skills:
            if isinstance(skill, dict) and 'name' in skill:
                skill_name = skill['name'].lower()
                
                # Check if skill name appears in job description
                if skill_name in job_description_lower:
                    relevant_skills.append(skill)
                    logger.debug(f"Skill '{skill['name']}' found relevant to job description")
                else:
                    logger.debug(f"Skill '{skill['name']}' not found in job description, filtering out")
            else:
                logger.warning(f"Invalid skill format: {skill}")
        
        logger.info(f"Filtered skills: {len(missing_skills)} -> {len(relevant_skills)} relevant skills")
        return relevant_skills
    
    def _save_resume(self) -> str:
        """Saves the enhanced resume to a new YAML file in the company_resume directory."""
        # Create the company_resume directory path
        company_resume_dir = self.resume_path.parent / "company_resume"
        company_resume_dir.mkdir(exist_ok=True)
        
        # Build filename with job title if provided
        filename_parts = [self.resume_path.stem]
        
        if self.job_title:
            sanitized_job_title = self._sanitize_filename(self.job_title)
            filename_parts.append(sanitized_job_title)
        
        filename_parts.append(self.company_name)
        
        enhanced_filename = "_".join(filename_parts) + self.resume_path.suffix
        new_resume_path = company_resume_dir / enhanced_filename
        
        logger.info(f"Saving enhanced resume to {new_resume_path}")
        
        try:
            with open(new_resume_path, 'w') as file:
                self.yaml.dump(self.resume_data, file)
            logger.info(f"Enhanced resume successfully saved to {new_resume_path}")
            return str(new_resume_path)
        except Exception as e:
            logger.error(f"Failed to save enhanced resume to {new_resume_path}: {e}")
            raise
    
    def enhance_resume(self, ats_result: ATSResult) -> str:
        """Enhances the resume based on ATS findings while preserving structure and order."""
        logger.info(f"🚀 Starting resume enhancement with ATS score: {ats_result.ats_score}")
        logger.info(f"📋 Missing skills to add: {len(ats_result.missing_skills)}")
        
        # Log the missing skills details
        if ats_result.missing_skills:
            skill_details = []
            for skill in ats_result.missing_skills:
                try:
                    skill_info = f"{skill['name']} ({skill.get('category', 'Unknown')})"
                    skill_details.append(skill_info)
                except (KeyError, TypeError):
                    skill_details.append(str(skill))
            logger.info(f"📝 Skills identified as missing: {', '.join(skill_details)}")
        else:
            logger.info("✅ No missing skills identified by ATS analysis")
        
        try:
            # Filter skills to only include job-relevant ones
            # Note: We don't have direct access to job description here, so we use all skills
            # In a future enhancement, we could pass job description to this method
            filtered_skills = ats_result.missing_skills
            
            self._add_missing_skills(filtered_skills)
            self._update_summary(ats_result)
            enhanced_path = self._save_resume()
            logger.info("🎉 Resume enhancement completed successfully")
            return enhanced_path
        except Exception as e:
            logger.error(f"❌ Resume enhancement failed: {e}")
            raise
    
    def _update_summary(self, ats_result: ATSResult):
        """Updates the summary section of the resume."""
        logger.info("Starting summary update with AI enhancement")
        
        current_summary = self.resume_data.get("summary", "")
        logger.debug(f"Current summary length: {len(current_summary)} characters")
        
        # Extract only skill names from missing skills
        missing_skill_names = []
        for skill in ats_result.missing_skills:
            if isinstance(skill, dict) and 'name' in skill:
                missing_skill_names.append(skill['name'])
        
        missing_skills_text = ", ".join(missing_skill_names)
        
        prompt = f"""
        Rewrite this professional resume summary by naturally incorporating the missing skills listed below. 
        
        RULES:
        - Keep the same professional tone and structure
        - Only add the missing skills naturally into existing sentences
        - Do NOT add any meta-commentary, suggestions, or advice
        - Do NOT mention "ATS score" or similar phrases
        - Do NOT add explanatory text about what would improve anything
        - Return ONLY the improved summary text, nothing else
        
        Current Summary:
        {current_summary}
        
        Missing Skills to incorporate naturally:
        {missing_skills_text}
        
        Return only the JSON output with key "summary" and the enhanced summary as the value.
        """
        
        logger.debug(f"AI prompt prepared: {len(prompt)} characters")
        
        messages = [
            {"role": "system", "content": "You are a professional resume writer. Write only resume content, never include advice or meta-commentary."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            logger.debug("Sending request to AI model for summary enhancement")
            response = self.model.get_completion(messages)
            logger.debug(f"AI response received: {len(response)} characters")
            
            response_data = json.loads(response)
            new_summary = response_data["summary"]
            
            # Validate and clean the summary
            validated_summary = self._validate_summary(new_summary)
            
            self.resume_data["summary"] = validated_summary
            logger.info(f"Summary updated successfully: {len(current_summary)} -> {len(validated_summary)} characters")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Raw AI response: {response}")
            raise
        except KeyError as e:
            logger.error(f"Expected 'summary' key not found in AI response: {e}")
            logger.debug(f"AI response data: {response_data}")
            raise
        except Exception as e:
            logger.error(f"Error updating summary with AI: {e}")
            raise

    def _add_missing_skills(self, missing_skills: list[str]):
        """Adds missing skills while preserving the existing structure."""
        logger.info(f"Adding {len(missing_skills)} missing skills to resume")
        
        if "skills" not in self.resume_data:
            logger.warning("No 'skills' section found in resume data")
            self.resume_data["skills"] = []
            
        if not isinstance(self.resume_data["skills"], list):
            logger.error(f"Skills section is not a list: {type(self.resume_data['skills'])}")
            return
            
        # Check if skill already exists by name
        existing_skill_names = []
        try:
            existing_skill_names = [skill["name"].lower() for skill in self.resume_data["skills"]]
            logger.info(f"Found {len(existing_skill_names)} existing skills in resume: {', '.join(existing_skill_names)}")
        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing existing skills: {e}")
            existing_skill_names = []
        
        # Log the missing skills we're trying to add
        missing_skill_names = []
        try:
            missing_skill_names = [skill["name"] for skill in missing_skills]
            logger.info(f"Missing skills identified by ATS analysis: {', '.join(missing_skill_names)}")
        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing missing skills list: {e}")
        
        skills_added = 0
        skills_skipped = 0
        for skill in missing_skills:
            try:
                skill_name = skill["name"].lower()
                skill_display_name = skill["name"]
                
                if skill_name not in existing_skill_names:
                    self.resume_data["skills"].append(skill)
                    skills_added += 1
                    logger.info(f"✅ Added new skill: '{skill_display_name}' ({skill.get('category', 'Unknown')} - {skill.get('level', 'Unknown')})")
                else:
                    skills_skipped += 1
                    logger.info(f"⏭️  Skill already exists, skipping: '{skill_display_name}' (already in resume as one of: {', '.join(existing_skill_names)})")
            except (KeyError, TypeError) as e:
                logger.warning(f"❌ Error processing skill {skill}: {e}")
                continue
        
        logger.info(f"📊 Skill addition summary: {skills_added} added, {skills_skipped} skipped (already existed)")
        logger.info(f"Successfully added {skills_added} new skills to resume")

if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    #secrets = yaml.safe_load(open(secrets_path, 'r'))
    #api_key = secrets['api_key']
    resume_path = "input/sami_dhiab_resume.yaml"
    ats_result = ATSResult(
            ats_score=65
            ,missing_skills=[{'category': 'Programming Languages', 'name': 'C#', 'level': 'Advanced'}, {'category': 'Frameworks', 'name': 'Angular', 'level': 'Intermediate'}, {'category': 'Tools', 'name': 'Azure DevOps', 'level': 'Intermediate'}, {'category': 'Methodologies', 'name': 'SCRUM', 'level': 'Advanced'}]
            ,suggested_improvements="1. Include specific experience with C# and .Net, as these are critical for the role. 2. Highlight any experience with Angular and Azure DevOps, as these are mentioned in the job description. 3. Emphasize leadership experience and any direct involvement in SaaS product development. 4. Ensure that the resume is formatted clearly with distinct sections for skills, experience, and education to improve readability for ATS."
            )
    
    enhancer = ResumeEnhancer(resume_path, "Google", "Software Engineer")
    new_resume_path = enhancer.enhance_resume(ats_result)
    print(f"Resume successfully enhanced and saved at: {new_resume_path}")