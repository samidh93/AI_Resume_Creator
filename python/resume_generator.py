import logging
from pathlib import Path
from .openai_interface import OpenAIInterface
import asyncio
from pyppeteer import launch
from .job_description_interface import JobDescriptionInterface

class ResumeGenerator:
    def __init__(self, resume_path: str, style_path: str, output_dir: Path):
        self.resume_path = resume_path
        self.style_path = style_path
        self.output_dir = output_dir

    def generate_resume(self, ai_model, api_key):
        logging.info('Generating resume...')
        # switch AI model
        if ai_model == 'openai':
            self.generate_resume_using_gpt(api_key)
        if ai_model == 'gemini':
            self.generate_resume_using_gemini(api_key)

    def generate_resume_with_job_description(self, ai_model, api_key, job_description=""):
        logging.info('Generating resume with job description...')
        # create job description interface
        job_description_interface = JobDescriptionInterface(job_description)
        job_description = job_description_interface.get_text_job_description()
        logging.info('Job description: %s' % job_description)
        # switch AI model
        if ai_model == 'openai':
            self.generate_resume_using_gpt(api_key, job_description=job_description)
        if ai_model == 'gemini':
            self.generate_resume_using_gemini(api_key, job_description=job_description)

    def generate_resume_using_gpt(self, api_key, job_description=""):
        # use open ai api to upload file in the prompt
        client = OpenAIInterface(api_key=api_key)
        # Prompt to create the resume using the yaml file and style file
        # Read the files
        with open(self.resume_path, "r") as resume_file:
            resume_content = resume_file.read()

        with open(self.style_path, "r") as style_file:
            style_content = style_file.read()
        # prompt
        prompt_html = f"""
                Act as an HR expert and create a resume that passes ATS checks using the attached Yaml Content.
                write city, country. place education after experiences. sort the data in all sections by date in descending order.
                Use the provided CSS Content for styling. Generate the resume in valid HTML format. Do not include any other text.
                If the job description is provided and not empty, tailor the resume to the job description and highlight relevant skills.
                return only the html code for the resume. skip the ``` html

                ### Yaml Resume Content
                {resume_content}

                ### CSS Style Content
                {style_content}

                ### Job Description
                {job_description}
                """
        logging.info('Prompt: %s' % prompt_html)
        # Prepare the message for ChatCompletion
        messages = [
            {
                "role": "system",
                "content": "You are an expert HR professional skilled in creating ATS-compliant resumes.",
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
        browser = await launch()
        page = await browser.newPage()
        await page.goto(f'file://{html_file}')  # Replace with your file path
        await page.pdf({'path': resume_file_path, 'format': 'A4'})
        await browser.close()





########### Gemini AI
    def generate_resume_using_gemini(self, api_key):
        pass