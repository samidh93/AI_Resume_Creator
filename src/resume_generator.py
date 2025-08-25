from jinja2 import Environment, FileSystemLoader
from resume_parser import ResumeParser
import os
import asyncio
from pyppeteer import launch
from pathlib import Path
from googletrans import Translator
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

class ResumeGenerator:
    """Generates an HTML resume from a YAML data structure with dynamic translation."""

    def __init__(self, resume_path, output_dir, template_path, language="en"):
        logger.info(f"Initializing ResumeGenerator with resume: {resume_path}, output: {output_dir}, template: {template_path}, language: {language}")
        
        self.resume_path = Path(resume_path)
        self.output_dir = Path(output_dir)
        self.language = language
        
        try:
            self.env = Environment(loader=FileSystemLoader(template_path))
            self.template = self.env.get_template("resume_template.html")
            logger.info(f"Successfully loaded template from {template_path}")
        except Exception as e:
            logger.error(f"Failed to load template from {template_path}: {e}")
            raise
            
        try:
            self.translator = Translator()
            logger.debug("Translator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize translator: {e}")
            raise
            
        logger.info("ResumeGenerator initialization completed successfully")

    async def _translate_text(self, text, target_lang):
        """Translate text asynchronously using Google Translate.
           Since googletrans is synchronous, we run it in an executor.
        """
        if target_lang == "en":
            logger.debug(f"Skipping translation for English text: {text[:50]}...")
            return text  # No translation needed for English
            
        logger.debug(f"Translating text to {target_lang}: {text[:50]}...")
        try:
            translation = await self.translator.translate(text, target_lang)
            logger.debug(f"Translation successful: {text[:30]}... -> {translation.text[:30]}...")
            return translation.text
        except Exception as e:
            logger.warning(f"Translation failed for text '{text[:50]}...': {e}")
            return text  # Fallback to original text if translation fails

    async def generate_html_async(self, resume_data, output_file=None):
        """Render resume data with dynamically translated labels and content."""
        logger.info(f"Starting HTML generation for language: {self.language}")
        
        # Define all static label keys with their default English texts.
        label_keys = {
            "personal_information": "Personal Information",
            "summary": "Summary",
            "experience": "Experience",
            "education": "Education",
            "skills": "Technical Skills",
            "languages": "Languages",
            "projects": "Projects",
            "certifications": "Certifications",
            "interests": "Interests",
            "key_responsibilities": "Key Responsibilities",
            "skills_acquired": "Skills Acquired",
            "field_of_study": "Field of Study",
            "institution": "Institution",
            "graduation_year": "Graduation Year",
            "role": "Role",
            "description": "Description",
            "year": "Year",
            "link": "Link",
            "view_project": "View Project",
            "issuer": "Issuer",
            "date_of_issuance": "Date of Issuance",
            "certificate": "Certificate",
            "view": "View",
            "lang": self.language  # Used to set the HTML lang attribute if desired
        }

        logger.debug(f"Translating {len(label_keys)} labels to {self.language}")
        # Translate each label asynchronously.
        labels = {}
        for key, value in label_keys.items():
            labels[key] = await self._translate_text(value, self.language)
        logger.info("Label translation completed")

        # Translate resume content fields as needed.
        logger.debug("Starting content translation")
        
        if "personal_information" in resume_data:
            logger.debug("Translating personal information")
            if "citizenship" in resume_data["personal_information"]:
                resume_data["personal_information"]["citizenship"] = await self._translate_text(resume_data["personal_information"]["citizenship"], self.language)
        
        if "summary" in resume_data:
            logger.debug("Translating summary")
            resume_data["summary"] = await self._translate_text(resume_data["summary"], self.language)

        if "experiences" in resume_data:
            logger.debug(f"Translating {len(resume_data['experiences'])} experiences")
            for i, exp in enumerate(resume_data["experiences"]):
                logger.debug(f"Translating experience {i+1}")
                if "employment_period" in exp:
                    exp["employment_period"] = await self._translate_text(exp["employment_period"], self.language)
                if "location" in exp:
                    exp["location"] = await self._translate_text(exp["location"], self.language)
                if "key_responsibilities" in exp:
                    logger.debug(f"Translating {len(exp['key_responsibilities'])} responsibilities")
                    for res in exp["key_responsibilities"]:
                        if "description" in res:
                            res["description"] = await self._translate_text(res["description"], self.language)
                if "skills_acquired" in exp:
                    logger.debug(f"Translating {len(exp['skills_acquired'])} skills")
                    exp["skills_acquired"] = [await self._translate_text(skill, self.language) for skill in exp["skills_acquired"]]

        if "education" in resume_data:
            logger.debug(f"Translating {len(resume_data['education'])} education entries")
            for edu in resume_data["education"]:
                if "field_of_study" in edu:
                    edu["field_of_study"] = await self._translate_text(edu["field_of_study"], self.language)
                if "graduation_year" in edu:
                    edu["graduation_year"] = await self._translate_text(edu["graduation_year"], self.language)

        if "projects" in resume_data:
            logger.debug(f"Translating {len(resume_data['projects'])} projects")
            for project in resume_data["projects"]:
                if "role" in project:
                    project["role"] = await self._translate_text(project["role"], self.language)
                if "description" in project:
                    project["description"] = await self._translate_text(project["description"], self.language)

        if "certifications" in resume_data:
            logger.debug(f"Translating {len(resume_data['certifications'])} certifications")
            for cert in resume_data["certifications"]:
                if "date" in cert:
                    cert["date"] = await self._translate_text(cert["date"], self.language)

        if "interests" in resume_data:
            logger.debug(f"Translating {len(resume_data['interests'])} interests")
            resume_data["interests"] = [await self._translate_text(interest, self.language) for interest in resume_data["interests"]]

        if "languages" in resume_data:
            logger.debug(f"Translating {len(resume_data['languages'])} language entries")
            for lang in resume_data["languages"]:
                if "language" in lang:
                    lang["language"] = await self._translate_text(lang["language"], self.language)
                if "proficiency" in lang:
                    lang["proficiency"] = await self._translate_text(lang["proficiency"], self.language)

        logger.info("Content translation completed")

        # Render the template with translated content.
        logger.debug("Rendering HTML template")
        try:
            output_html = self.template.render(resume_data, labels=labels)
            html_file = output_file or (self.output_dir / self.resume_path.name.replace(".yaml", ".html"))
            
            with open(html_file, "w", encoding="utf-8") as file:
                file.write(output_html)
            
            logger.info(f"HTML resume successfully saved as {html_file}")
            return html_file
        except Exception as e:
            logger.error(f"Failed to render or save HTML template: {e}")
            raise

    def generate_html(self, resume_data):
        logger.info("Starting synchronous HTML generation")
        try:
            # Always run in a separate thread to avoid signal handler issues in web server contexts
            import concurrent.futures
            import threading
            
            def run_in_thread():
                # Create a new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(self.generate_html_async(resume_data))
                finally:
                    new_loop.close()
            
            # Check if we're likely in a web server context by checking thread name
            current_thread = threading.current_thread()
            is_main_thread = isinstance(current_thread, threading._MainThread)
            
            logger.debug(f"Thread info: name='{current_thread.name}', is_main={is_main_thread}, type={type(current_thread)}")
            
            # For now, always use separate thread to avoid signal issues
            logger.debug("Using separate thread with new event loop to avoid signal handler issues")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                result = future.result()
            
            logger.info("Synchronous HTML generation completed successfully")
            return result
        except Exception as e:
            logger.error(f"Synchronous HTML generation failed: {e}")
            raise

    async def html_to_pdf_async(self, html_file):
        logger.info(f"Starting PDF generation from {html_file}")
        
        resume_file_name = html_file.name.replace(".html", ".pdf")
        resume_file_path = self.output_dir / resume_file_name
        
        logger.debug(f"PDF will be saved as: {resume_file_path}")
        
        try:
            # Browser setup with signal handling disabled
            if os.environ.get('CONTAINER'):
                logger.debug("Running in container mode - using Chromium")
                executablePath = "/usr/bin/chromium"
                args = ['--no-sandbox', '--disable-setuid-sandbox']
                browser = await launch(
                    headless=True, 
                    executablePath=executablePath, 
                    args=args,
                    handleSIGINT=False,
                    handleSIGTERM=False,
                    handleSIGHUP=False
                )
            else:
                logger.debug("Running in local mode - using default browser")
                browser = await launch(
                    headless=True,
                    handleSIGINT=False,
                    handleSIGTERM=False,
                    handleSIGHUP=False
                )
            
            logger.debug("Browser launched successfully")
            
            page = await browser.newPage()
            logger.debug("New page created")
            
            file_url = f'file://{html_file}'
            logger.debug(f"Loading HTML file: {file_url}")
            await page.goto(file_url)
            
            logger.debug("Generating PDF with settings")
            await page.pdf({
                "path": resume_file_path,
                "format": 'A4',
                "printBackground": True,
                "preferCSSPageSize": True,
                "embedFonts": True  # Ensure fonts are embedded
            })
            
            logger.info(f"PDF resume successfully saved as {resume_file_path}")
            await browser.close()
            logger.debug("Browser closed")
            
            return resume_file_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            try:
                await browser.close()
                logger.debug("Browser closed after error")
            except:
                pass
            raise

    def html_to_pdf(self, html_file):
        logger.info("Starting synchronous PDF generation")
        try:
            absolute_html_path = Path(html_file).resolve()
            logger.debug(f"Resolved HTML path: {absolute_html_path}")
            
            # Always run in a separate thread to avoid signal handler issues in web server contexts
            import concurrent.futures
            import threading
            
            def run_in_thread():
                # Create a new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(self.html_to_pdf_async(absolute_html_path))
                finally:
                    new_loop.close()
            
            # Check if we're likely in a web server context by checking thread name
            current_thread = threading.current_thread()
            is_main_thread = isinstance(current_thread, threading._MainThread)
            
            logger.debug(f"Thread info: name='{current_thread.name}', is_main={is_main_thread}, type={type(current_thread)}")
            
            # For now, always use separate thread to avoid signal issues
            logger.debug("Using separate thread with new event loop to avoid signal handler issues")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                result = future.result()
            
            logger.info("Synchronous PDF generation completed successfully")
            return result
        except Exception as e:
            logger.error(f"Synchronous PDF generation failed: {e}")
            raise


if __name__ == "__main__":

    resume = Path(__file__).parent.parent / "input" / "sami_dhiab_resume.yaml"
    output = Path(__file__).parent.parent / "output" 
    example = Path(__file__).parent.parent / "example"
    resume_generator = ResumeGenerator(
        resume_path=resume, 
        output_dir=output,
        template_path=example,
        language="en"  # Change this to your desired target language code (e.g. "fr", "es", etc.)
    )
    resume_parser = ResumeParser(resume)
    html_file = resume_generator.generate_html(resume_parser.data)
    resume_generator.html_to_pdf(html_file)
