import argparse
import logging
from pathlib import Path
from resume_parser import ResumeParser
from resume_generator import ResumeGenerator
from resume_enhancer import ResumeEnhancer 
from job_description_interface import JobDescriptionInterface
from resume_analyzer import ResumeAnalyzer
import yaml
from langdetect import detect
def setup_logging(log_path: Path):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

def parse_arguments():
    parser = argparse.ArgumentParser(description='AI Resume Creator')
    parser.add_argument('--resume', type=str, default=None, help='Path to the resume YAML file')
    parser.add_argument('--output', type=str, default='output/', help='Output directory for generated files')
    parser.add_argument('--url', type=str, default=None, help='Job description Url')
    parser.add_argument('--language', type=str, default='auto', help='Language for the resume ')
    return parser.parse_args()

def main():
    try:
        args = parse_arguments()
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        log_path = output_dir / 'resume_generation.log'
        setup_logging(log_path)
        logging.info('Starting AI Resume Creator...')
        resume_path = Path(args.resume)
        # load ai_model and api_key from input/secrets.yaml
        secrets_path = Path('input/secrets.yaml')
        secrets = yaml.safe_load(open(secrets_path, 'r'))
        api_key = secrets['api_key']
        ai_model = secrets['ai_model']
        # Load resume
        resume_parser = ResumeParser(resume_path)
        resume_lang = args.language 
        # load job description        
        if args.url:
            job_description, company_name = JobDescriptionInterface(args.url).get_job_description(load_from_file=True, save_to_file=True)
            ra = ResumeAnalyzer(api_key, job_description, resume_parser)
            ats_result = ra.compare()
            resume_enhancer = ResumeEnhancer(api_key, resume_path, company_name) 
            resume_path = resume_enhancer.enhance_resume(ats_result)
            resume_parser = ResumeParser(resume_path)
            if resume_lang == 'auto':
                resume_lang = detect(job_description)
        # Generate resume
        example_dir = Path(__file__).parent.parent / "example"
        resume_generator = ResumeGenerator(resume_path, output_dir, example_dir, resume_lang)
        resume_html = resume_generator.generate_html(resume_parser.data)
        resume_generator.html_to_pdf(resume_html)
        logging.info('Resume generated successfully!')
    except Exception as e:
        logging.error(f'An error occurred: {e}')


if __name__ == '__main__':
    main()
