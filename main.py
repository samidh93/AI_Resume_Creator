import argparse
import logging
from pathlib import Path
from python.resume_generator import ResumeGenerator
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
    parser.add_argument('--style', type=str, default=None, help='Path to the CSS style file')
    parser.add_argument('--output', type=str, default='output', help='Output directory for generated files')
    parser.add_argument('--ai_model', type=str, default='openai', help='AI model to use (openai or gemini)')
    parser.add_argument('--api_key', type=str, default=None, help='API key for the AI model')
    parser.add_argument('--job_description_url', type=str, default=None, help='Job description Url')
    return parser.parse_args()

def main():
    try:
        args = parse_arguments()
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        log_path = output_dir / 'resume_generation.log'
        setup_logging(log_path)
        logging.info('Starting AI Resume Creator...')
        style_path = Path(args.style) if args.style else Path('input/style.css')
        resume_path = Path(args.resume) if args.resume else Path('input/resume.yaml')
        # load ai_model and api_key from input/secrets.yaml
        secrets_path = Path('input/secrets.yaml')
        secrets = yaml.safe_load(open(secrets_path, 'r'))
        api_key = args.api_key or secrets['api_key']
        ai_model = args.ai_model or secrets['ai_model']
        resume_generator = ResumeGenerator(resume_path, style_path, output_dir)
        if args.job_description_url:
            logging.info('job_description_url provided: %s' % args.job_description_url)
            resume_generator.generate_resume_with_job_description(ai_model, api_key, args.job_description_url)
        else:
            resume_generator.generate_resume(ai_model, api_key)

        logging.info('Resume generated successfully!')
    except Exception as e:
        logging.error(f'An error occurred: {e}')


if __name__ == '__main__':
    main()
