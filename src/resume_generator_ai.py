import logging
from pathlib import Path
import os
from .openai_interface import OpenAIInterface
import asyncio
from pyppeteer import launch
from .job_description_interface import JobDescriptionInterface

class ResumeGenerator:
    def __init__(self, resume_path: str, style_path: str, output_dir: Path):
        self.resume_path = resume_path
        self.style_path = style_path
        self.output_dir = output_dir

    def generate_resume(self, ai_model, api_key , language):
        logging.info('Generating resume...')
        # switch AI model
        if ai_model == 'openai':
            self.generate_resume_using_gpt(api_key, language)
        if ai_model == 'gemini':
            self.generate_resume_using_gemini(api_key, language)

    def generate_resume_with_job_description(self, ai_model, api_key, job_description="", language=""):
        logging.info('Generating resume with job description...')
        # create job description interface
        job_description_interface = JobDescriptionInterface(job_description)
        job_description = job_description_interface.get_job_description()
        logging.info('Job description: %s' % job_description)
        # switch AI model
        if ai_model == 'openai':
            self.generate_resume_using_gpt(api_key, job_description, language)
        if ai_model == 'gemini':
            self.generate_resume_using_gemini(api_key, job_description, language)

    def generate_resume_using_gpt(self, api_key, job_description="", language=""):
        client = OpenAIInterface(api_key=api_key)
        # Read the resume and style files
        with open(self.resume_path, "r") as resume_file:
            resume_content = resume_file.read()

        prompt_html = f"""
        Act as an HR expert and generate an ATS-compliant resume in valid HTML format using the YAML content provided below.
        
        Follow these strict rules:
        - **Structure:** Maintain the exact indentation of the YAML.
        - **Font-size:** Use a hierarchy from top-level keys (largest) to nested keys (smallest).
        - **Bold top-level keys**, *italicize nested keys*, and apply proper **coloring** using the provided CSS File.
        - **Preserve all keys and values** exactly as given in the YAML.
        - **Ensure valid HTML output** without markdown, code fences, or extra text.
        - **Sort experiences & education sections** in descending order by date.
        - **If language is provided, translate the resume** into that language.
        - **If a job description is provided**, optimize the resume for it.

        Ensure the output is **consistent across multiple calls**.

        ### YAML Resume Content
        {resume_content}

        ### CSS Style File 
        {self.style_path}

        ### Job Description
        {job_description}

        ### Language
        {language}
        """

        logging.info('Prompt: %s' % prompt_html)

        messages = [
            {
                "role": "system",
                "content": "You are an expert HR professional skilled in creating ATS-compliant resumes. Ensure deterministic formatting."
            },
            {
                "role": "user",
                "content": prompt_html
            }
        ]

        # Send request to OpenAI API with controlled randomness
        completion = client.prompt(messages, model="gpt-4o-mini", temperature=0)
        
        resume_content = completion.choices[0].message.content
        resume_html = self.save_resume_html(resume_content)
        
        # Convert to absolute path and generate PDF
        absolute_html_path = Path(resume_html).resolve()
        asyncio.get_event_loop().run_until_complete(self.html_to_pdf(absolute_html_path))


    def save_resume_html(self, resume_content):
        resume_file_name = self.resume_path.name.replace(".yaml", ".html")
        resume_file_path = self.output_dir / resume_file_name
        with open(resume_file_path, "w") as resume_file:
            resume_file.write(resume_content)
        resume_file.close()
        return resume_file_path

    async def html_to_pdf(self, html_file):
        resume_file_name = self.resume_path.name.replace(".yaml", ".pdf")
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





########### Gemini AI
    def generate_resume_using_gemini(self, api_key, job_description="", language=""):
        pass
