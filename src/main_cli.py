import argparse
import logging
from pathlib import Path
from resume_parser import ResumeParser
from keyword_extractor import KeywordExtractor
from ats_scorer import ATSScorer
from resume_generator import ResumeGenerator
from ai_enhancer import AIEnhancer  # Optional
from job_description_interface import JobDescriptionInterface
import yaml
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
        resume_summary = resume_parser.get_resume_summary()
        resume_exp_skills = resume_parser.get_resume_experiences_skills_acquired()
        resume_skills = resume_parser.get_resume_skills()
        resume_projects_skills = resume_parser.get_resume_project_skills()
        resume_interests = resume_parser.get_resume_interests()
        # Extract keywords
        resume_keywords = ",".join([resume_summary, resume_skills, resume_exp_skills, resume_projects_skills, resume_interests])
        resume_extractor = KeywordExtractor(resume_keywords)

        if args.url:
            job_description = JobDescriptionInterface(args.url).get_job_description()
            job_extractor = KeywordExtractor(job_description)
            ats_scorer = ATSScorer()
            # Compute ATS score
            ats_score, matched_keywords = ats_scorer.calculate_score(resume_extractor, job_extractor)
            print(f"ATS Score: {ats_score}%")
            print(f"Matched Keywords: {', '.join(matched_keywords)}")

            resume_parser.data["ats_score"] = ats_score
            resume_parser.data["matched_keywords"] = ", ".join(matched_keywords)
        # Generate resume
        resume_generator = ResumeGenerator(resume_path, output_dir, "example/")
        resume_html = resume_generator.generate_html(resume_parser.data)
        resume_generator.html_to_pdf(resume_html)

        logging.info('Resume generated successfully!')
    except Exception as e:
        logging.error(f'An error occurred: {e}')


if __name__ == '__main__':
    main()
