import argparse
import logging
from pathlib import Path
from resume_parser import ResumeParser
from resume_generator import ResumeGenerator
from resume_enhancer import ResumeEnhancer 
from job_description_interface import JobDescriptionInterface
from resume_analyzer import ResumeAnalyzer
from job_description_file import JobDescriptionFile
import yaml
from langdetect import detect

# Set up logger for this module
logger = logging.getLogger(__name__)

def setup_logging(log_path: Path):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    logger.info(f"Logging configured - log file: {log_path}")

def parse_arguments():
    logger.debug("Parsing command line arguments")
    parser = argparse.ArgumentParser(description='AI Resume Creator')
    parser.add_argument('--resume', type=str, default=None, help='Path to the resume YAML file')
    parser.add_argument('--output', type=str, default='output/', help='Output directory for generated files')
    parser.add_argument('--job_description_url', type=str, default=None, help='Job description Url')
    parser.add_argument('--language', type=str, default='auto', help='Language for the resume ')
    parser.add_argument('--job_description_file', type=str, default=None, help='Path to the job description file')
    args = parser.parse_args()
    
    logger.info(f"Arguments parsed:")
    logger.info(f"  - Resume: {args.resume}")
    logger.info(f"  - Output: {args.output}")
    logger.info(f"  - Job URL: {args.job_description_url}")
    logger.info(f"  - Job File: {args.job_description_file}")
    logger.info(f"  - Language: {args.language}")
    
    return args

def main():
    try:
        logger.info('Starting AI Resume Creator...')
        
        args = parse_arguments()
        
        # Setup output directory and logging
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        log_path = output_dir / 'resume_generation.log'
        setup_logging(log_path)
        
        logger.info('AI Resume Creator initialized successfully')
        
        # Validate resume path
        if not args.resume:
            logger.error("No resume file specified")
            raise ValueError("Resume file path is required")
            
        resume_path = Path(args.resume)
        if not resume_path.exists():
            logger.error(f"Resume file not found: {resume_path}")
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        
        logger.info(f"Using resume file: {resume_path}")
        
        # Load secrets (commented out but keeping structure)
        secrets_path = Path('input/secrets.yaml')
        if secrets_path.exists():
            logger.debug("Loading secrets configuration")
            secrets = yaml.safe_load(open(secrets_path, 'r'))
            logger.debug("Secrets loaded successfully")
        else:
            logger.warning(f"Secrets file not found: {secrets_path}")
        
        # Load resume
        logger.info("Loading and parsing resume")
        resume_parser = ResumeParser(resume_path)
        resume_lang = args.language 
        logger.info(f"Resume loaded successfully, language set to: {resume_lang}")
        
        # Process job description if provided
        job_description = None
        company_name = "Unknown Company"
        
        if args.job_description_url or args.job_description_file:
            logger.info("Job description provided - starting enhancement process")
            
            if args.job_description_file:
                logger.info(f"Loading job description from file: {args.job_description_file}")
                job_description, company_name = JobDescriptionFile(args.job_description_file).get_job_description_from_file()
            else:   
                logger.info(f"Fetching job description from URL: {args.job_description_url}")
                job_description, company_name = JobDescriptionInterface(args.job_description_url).get_job_description(load_from_file=True, save_to_file=True)
            
            logger.info(f"Job description obtained for company: {company_name}")
            
            # Analyze resume against job description
            logger.info("Starting ATS analysis")
            ra = ResumeAnalyzer(job_description, resume_parser)
            ats_result = ra.compare()
            logger.info(f"ATS analysis completed - Score: {ats_result.ats_score}")
            
            # Enhance resume
            logger.info("Starting resume enhancement process")
            resume_enhancer = ResumeEnhancer(resume_path, company_name, job_title)
            enhanced_resume_path = resume_enhancer.enhance_resume(ats_result)
            
            # Use enhanced resume for generation
            resume_path = Path(enhanced_resume_path)
            resume_parser = ResumeParser(resume_path)
            
            # Auto-detect language if needed
            if resume_lang == 'auto':
                logger.info("Auto-detecting language from job description")
                resume_lang = detect(job_description)
                logger.info(f"Language detected: {resume_lang}")
        else:
            logger.info("No job description provided - proceeding with basic resume generation")
        
        # Generate resume
        logger.info("Starting resume generation")
        example_dir = Path(__file__).parent.parent / "example"
        logger.debug(f"Using template directory: {example_dir}")
        
        resume_generator = ResumeGenerator(resume_path, output_dir, example_dir, resume_lang)
        
        logger.info("Generating HTML resume")
        resume_html = resume_generator.generate_html(resume_parser.data)
        
        logger.info("Converting HTML to PDF")
        pdf_path = resume_generator.html_to_pdf(resume_html)
        
        logger.info(f'Resume generated successfully! PDF saved at: {pdf_path}')
        
    except Exception as e:
        logger.error(f'An error occurred during resume generation: {e}', exc_info=True)
        raise


if __name__ == '__main__':
    main()
