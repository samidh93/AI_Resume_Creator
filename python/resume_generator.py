import logging
from pathlib import Path
from .openai_interface import OpenAIInterface
import asyncio
from pyppeteer import launch
from .job_description_interface import JobDescriptionInterface
import os
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
        job_description = job_description_interface.get_text_job_description()
        logging.info('Job description: %s' % job_description)
        # switch AI model
        if ai_model == 'openai':
            self.generate_resume_using_gpt(api_key, job_description, language)
        if ai_model == 'gemini':
            self.generate_resume_using_gemini(api_key, job_description, language)

    def generate_resume_using_gpt(self, api_key, job_description="", language=""):
        # use open ai api to upload file in the prompt
        client = OpenAIInterface(api_key=api_key)
        # Prompt to create the resume using the yaml file and style file
        # Read the files
        with open(self.resume_path, "r") as resume_file:
            resume_content = resume_file.read()

        with open(self.style_path, "r") as style_file:
            style_content = style_file.read()
        prompt_html = f"""
        Act as an HR expert and generate an ATS-compliant resume in valid HTML format using the attached YAML content. The HTML output must exactly mirror the structure and formatting of the YAML input, preserving all keys, nested key-value pairs, and line breaks (each key-value pair on a new line). Use the provided CSS content for styling.

        Instructions:
        - Include city and country information.
        - Place the 'education' section after the 'experiences' section.
        - Sort all sections by date in descending order.
        - If a language is provided and is not empty, generate the resume in that language.
        - If a job description is provided and is not empty, tailor the resume to match it and highlight relevant skills.
        - If a job description is provided but no language is given, use the language of the job description.
        - Ensure all data from the YAML content is complete and valid.
        - Output only the HTML code for the resume; do not include any extra text or markdown formatting (skip code fences).

        ### YAML Resume Content
        {resume_content}

        ### CSS Style Content
        {style_content}

        ### Job Description
        {job_description}

        ### Language
        {language}
        """
        logging.info('Prompt: %s' % prompt_html)

        # Prepare the message for ChatCompletion
        messages = [
            {
                "role": "system",
                "content": "You are an expert HR professional skilled in creating ATS-compliant resumes."
            },
            {
                "role": "user",
                "content": prompt_html
            }
        ]

        # Send request to OpenAI API
        completion = client.prompt(messages)
        # Extract the HTML from the response
        resume_content = completion.choices[0].message.content
        resume_html = self.save_resume_html(resume_content)
        # get html file full path and pass it to html_to_pdf function
        absolute_html_path = Path(resume_html).resolve()  # Convert to absolute path
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