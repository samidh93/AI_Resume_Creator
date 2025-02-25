from jinja2 import Environment, FileSystemLoader
from resume_parser import ResumeParser
import os
import asyncio
from pyppeteer import launch
from pathlib import Path

class ResumeGenerator:
    """Generates an HTML resume from a YAML data structure."""

    def __init__(self, resume_path, output_dir, template_path):
        self.resume_path = Path(resume_path)
        self.output_dir = Path(output_dir)
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.template = self.env.get_template("resume_template.html")

    def generate_html(self, resume_data, output_file=None):
        """Render resume data into an HTML file."""
        output_html = self.template.render(resume_data)
        if output_file is None: html_file = self.output_dir / self.resume_path.name.replace(".yaml", ".html")
        else: html_file = output_file

        with open(html_file, "w") as file:
            file.write(output_html)
        file.close()
        print(f"Resume saved as {html_file}")
        return html_file

    async def html_to_pdf_async(self, html_file):
        resume_file_name = html_file.name.replace(".html", ".pdf")
        resume_file_path = self.output_dir / resume_file_name
        if os.environ.get('CONTAINER'):
            executablePath="/usr/bin/chromium"
            args=['--no-sandbox', '--disable-setuid-sandbox']
            browser = await launch(headless=True,executablePath=executablePath,args=args)
        else:
            browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(f'file://{html_file}')  # Replace with your file path
        await page.pdf({'path': resume_file_path, 'format': 'A4'})
        await browser.close()

    def html_to_pdf(self, html_file):
        absolute_html_path = Path(html_file).resolve()    
        asyncio.get_event_loop().run_until_complete(self.html_to_pdf_async(absolute_html_path))

if __name__ == "__main__":
    resume_generator = ResumeGenerator("/Users/sami/dev/AI_Resume_Creator/input/zayneb_dhieb_resume.yaml","/Users/sami/dev/AI_Resume_Creator/output", "example/")
    resume_parser = ResumeParser("input/zayneb_dhieb_resume.yaml")
    html_file = resume_generator.generate_html(resume_parser.data, output_file="output/zayneb_dhieb_resume.html")
    absolute_html_path = Path(html_file).resolve()    
    asyncio.get_event_loop().run_until_complete(resume_generator.html_to_pdf(absolute_html_path))
