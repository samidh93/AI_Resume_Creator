from jinja2 import Environment, FileSystemLoader
from resume_parser import ResumeParser
import os
import asyncio
from pyppeteer import launch
from pathlib import Path
from googletrans import Translator

class ResumeGenerator:
    """Generates an HTML resume from a YAML data structure with dynamic translation."""

    def __init__(self, resume_path, output_dir, template_path, language="en"):
        self.resume_path = Path(resume_path)
        self.output_dir = Path(output_dir)
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.template = self.env.get_template("resume_template.html")
        self.translator = Translator()
        self.language = language

    async def _translate_text(self, text, target_lang):
        """Translate text asynchronously using Google Translate.
           Since googletrans is synchronous, we run it in an executor.
        """
        if target_lang == "en":
            return text  # No translation needed for English
        try:
            translation = await self.translator.translate( text, target_lang )
            return translation.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Fallback to original text if translation fails

    async def generate_html_async(self, resume_data, output_file=None):
        """Render resume data with dynamically translated labels and content."""
        # Define all static label keys with their default English texts.
        label_keys = {
            "personal_information": "Personal Information",
            "summary": "Summary",
            "experience": "Experience",
            "education": "Education",
            "skills": "Skills",
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

        # Translate each label asynchronously.
        labels = {}
        for key, value in label_keys.items():
            labels[key] = await self._translate_text(value, self.language)

        # Translate resume content fields as needed.
        if "personal_information" in resume_data:
            if "citizenship" in resume_data["personal_information"]:
                resume_data["personal_information"]["citizenship"] = await self._translate_text(resume_data["personal_information"]["citizenship"], self.language)
        
        if "summary" in resume_data:
            resume_data["summary"] = await self._translate_text(resume_data["summary"], self.language)

        if "experiences" in resume_data:
            for exp in resume_data["experiences"]:
                if "position" in exp:
                    exp["position"] = await self._translate_text(exp["position"], self.language)
#                if "company" in exp:
#                    exp["company"] = await self._translate_text(exp["company"], self.language)
                if "employment_period" in exp:
                    exp["employment_period"] = await self._translate_text(exp["employment_period"], self.language)
                if "location" in exp:
                    exp["location"] = await self._translate_text(exp["location"], self.language)
                if "key_responsibilities" in exp:
                    for res in exp["key_responsibilities"]:
                        if "description" in res:
                            res["description"] = await self._translate_text(res["description"], self.language)
                if "skills_acquired" in exp:
                    exp["skills_acquired"] = [await self._translate_text(skill, self.language) for skill in exp["skills_acquired"]]

        if "education" in resume_data:
            for edu in resume_data["education"]:
                if "degree" in edu:
                    edu["degree"] = await self._translate_text(edu["degree"], self.language)
                if "field_of_study" in edu:
                    edu["field_of_study"] = await self._translate_text(edu["field_of_study"], self.language)
                #if "university" in edu:
                #    edu["university"] = await self._translate_text(edu["university"], self.language)
                if "graduation_year" in edu:
                    edu["graduation_year"] = await self._translate_text(edu["graduation_year"], self.language)

        if "projects" in resume_data:
            for project in resume_data["projects"]:
                #if "name" in project:
                #    project["name"] = await self._translate_text(project["name"], self.language)
                if "role" in project:
                    project["role"] = await self._translate_text(project["role"], self.language)
                if "description" in project:
                    project["description"] = await self._translate_text(project["description"], self.language)
                # Links and URLs are left untranslated.

        if "certifications" in resume_data:
            for cert in resume_data["certifications"]:
                if "name" in cert:
                    cert["name"] = await self._translate_text(cert["name"], self.language)
                if "issuer" in cert:
                    cert["issuer"] = await self._translate_text(cert["issuer"], self.language)
                if "date" in cert:
                    cert["date"] = await self._translate_text(cert["date"], self.language)
                # URLs remain unchanged.

        if "interests" in resume_data:
            resume_data["interests"] = [await self._translate_text(interest, self.language) for interest in resume_data["interests"]]

        if "languages" in resume_data:
            for lang in resume_data["languages"]:
                if "language" in lang:
                    lang["language"] = await self._translate_text(lang["language"], self.language)
                if "proficiency" in lang:
                    lang["proficiency"] = await self._translate_text(lang["proficiency"], self.language)

        # Render the template with translated content.
        output_html = self.template.render(resume_data, labels=labels)
        html_file = output_file or (self.output_dir / self.resume_path.name.replace(".yaml", ".html"))
        with open(html_file, "w", encoding="utf-8") as file:
            file.write(output_html)
        print(f"Resume saved as {html_file}")
        return html_file

    def generate_html(self, resume_data):
        return asyncio.run(self.generate_html_async(resume_data))

    async def html_to_pdf_async(self, html_file):
        resume_file_name = html_file.name.replace(".html", ".pdf")
        resume_file_path = self.output_dir / resume_file_name
        if os.environ.get('CONTAINER'):
            executablePath = "/usr/bin/chromium"
            args = ['--no-sandbox', '--disable-setuid-sandbox']
            browser = await launch(headless=True, executablePath=executablePath, args=args)
        else:
            browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(f'file://{html_file}')
        #await page.pdf({'path': resume_file_path, 'format': 'A4'})
        await page.pdf({
            "path": resume_file_path,
            "format": 'A4',
            "printBackground": True,
            "preferCSSPageSize": True,
            "embedFonts": True # Ensure fonts are embedded
        })
        print(f"PDF resume saved as {resume_file_path}")
        await browser.close()

    def html_to_pdf(self, html_file):
        absolute_html_path = Path(html_file).resolve()
        return asyncio.run(self.html_to_pdf_async(absolute_html_path))

if __name__ == "__main__":
    resume_generator = ResumeGenerator(
        "/Users/sami/dev/AI_Resume_Creator/input/sami_dhiab_resume.yaml",
        "/Users/sami/dev/AI_Resume_Creator/output",
        "example/",
        language="de"  # Change this to your desired target language code (e.g. "fr", "es", etc.)
    )
    resume_parser = ResumeParser("input/sami_dhiab_resume.yaml")
    html_file = resume_generator.generate_html(resume_parser.data)
    resume_generator.html_to_pdf(html_file)
