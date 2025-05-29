import os
import logging
import tempfile
import yaml
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from langdetect import detect

# Import the modules from main.py
from resume_parser import ResumeParser
from resume_generator import ResumeGenerator
from resume_enhancer import ResumeEnhancer 
from job_description_interface import JobDescriptionInterface
from resume_analyzer import ResumeAnalyzer
from job_description_file import JobDescriptionFile

app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'yaml', 'yml', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def setup_logging():
    """Setup logging for the Flask app"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_secrets():
    """Load secrets from input/secrets.yaml"""
    try:
        secrets_path = Path('input/secrets.yaml')
        if secrets_path.exists():
            return yaml.safe_load(open(secrets_path, 'r'))
        return {}
    except Exception as e:
        logging.warning(f"Could not load secrets: {e}")
        return {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "AI Resume Creator API is running"})

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    """
    Generate a resume based on uploaded resume file and job description
    Expects:
    - resume_file: YAML resume file
    - job_description_url: URL to job description (optional)
    - job_description_text: Direct job description text (optional)
    - language: Language for resume (optional, defaults to 'auto')
    """
    try:
        # Check if resume file is provided
        if 'resume_file' not in request.files:
            return jsonify({"error": "No resume file provided"}), 400
        
        resume_file = request.files['resume_file']
        if resume_file.filename == '':
            return jsonify({"error": "No resume file selected"}), 400
        
        if not allowed_file(resume_file.filename):
            return jsonify({"error": "Invalid file type. Only YAML files are allowed"}), 400
        
        # Save uploaded resume file
        filename = secure_filename(resume_file.filename)
        resume_path = Path(app.config['UPLOAD_FOLDER']) / filename
        resume_file.save(resume_path)
        
        # Get other parameters
        job_description_url = request.form.get('job_description_url')
        job_description_text = request.form.get('job_description_text')
        language = request.form.get('language', 'auto')
        
        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_path = output_dir / 'resume_generation.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        
        logging.info('Starting AI Resume Creator via API...')
        
        # Load secrets
        secrets = load_secrets()
        
        # Load resume
        resume_parser = ResumeParser(resume_path)
        resume_lang = language
        
        # Process job description if provided
        job_description = None
        company_name = "Unknown Company"
        
        if job_description_text:
            job_description = job_description_text
            company_name = "Provided Company"
        elif job_description_url:
            job_description, company_name = JobDescriptionInterface(job_description_url).get_job_description(load_from_file=True, save_to_file=True)
        
        # If job description is provided, enhance the resume
        if job_description:
            ra = ResumeAnalyzer(job_description, resume_parser)
            ats_result = ra.compare()
            resume_enhancer = ResumeEnhancer(resume_path, company_name)
            enhanced_resume_path = resume_enhancer.enhance_resume(ats_result)
            resume_parser = ResumeParser(enhanced_resume_path)
            
            if resume_lang == 'auto':
                resume_lang = detect(job_description)
        
        # Generate resume
        example_dir = Path(__file__).parent.parent / "example"
        resume_generator = ResumeGenerator(resume_path, output_dir, example_dir, resume_lang)
        resume_html = resume_generator.generate_html(resume_parser.data)
        pdf_path = resume_generator.html_to_pdf(resume_html)
        
        # Clean up uploaded file
        os.remove(resume_path)
        
        logging.info('Resume generated successfully via API!')
        
        return jsonify({
            "status": "success",
            "message": "Resume generated successfully",
            "pdf_path": str(pdf_path),
            "company_name": company_name,
            "language": resume_lang
        })
        
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        # Clean up uploaded file if it exists
        if 'resume_path' in locals() and resume_path.exists():
            os.remove(resume_path)
        return jsonify({"error": str(e)}), 500

@app.route('/download-resume/<filename>', methods=['GET'])
def download_resume(filename):
    """Download generated resume PDF"""
    try:
        output_dir = Path('output')
        file_path = output_dir / filename
        
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logging.error(f'Error downloading file: {e}')
        return jsonify({"error": str(e)}), 500

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    """
    Analyze resume against job description without generating a new resume
    Expects:
    - resume_file: YAML resume file
    - job_description_url: URL to job description (optional)
    - job_description_text: Direct job description text (optional)
    """
    try:
        # Check if resume file is provided
        if 'resume_file' not in request.files:
            return jsonify({"error": "No resume file provided"}), 400
        
        resume_file = request.files['resume_file']
        if resume_file.filename == '':
            return jsonify({"error": "No resume file selected"}), 400
        
        if not allowed_file(resume_file.filename):
            return jsonify({"error": "Invalid file type. Only YAML files are allowed"}), 400
        
        # Save uploaded resume file
        filename = secure_filename(resume_file.filename)
        resume_path = Path(app.config['UPLOAD_FOLDER']) / filename
        resume_file.save(resume_path)
        
        # Get job description
        job_description_url = request.form.get('job_description_url')
        job_description_text = request.form.get('job_description_text')
        
        if not job_description_text and not job_description_url:
            os.remove(resume_path)
            return jsonify({"error": "Job description is required for analysis"}), 400
        
        # Load resume
        resume_parser = ResumeParser(resume_path)
        
        # Get job description
        if job_description_text:
            job_description = job_description_text
            company_name = "Provided Company"
        else:
            job_description, company_name = JobDescriptionInterface(job_description_url).get_job_description(load_from_file=True, save_to_file=True)
        
        # Analyze resume
        ra = ResumeAnalyzer(job_description, resume_parser)
        ats_result = ra.compare()
        
        # Clean up uploaded file
        os.remove(resume_path)
        
        return jsonify({
            "status": "success",
            "message": "Resume analysis completed",
            "analysis_result": ats_result.model_dump(),
            "company_name": company_name
        })
        
    except Exception as e:
        logging.error(f'An error occurred during analysis: {e}')
        # Clean up uploaded file if it exists
        if 'resume_path' in locals() and resume_path.exists():
            os.remove(resume_path)
        return jsonify({"error": str(e)}), 500

@app.route('/job-description', methods=['POST'])
def get_job_description():
    """
    Extract job description from URL
    Expects:
    - job_url: URL to job description
    """
    try:
        data = request.get_json()
        if not data or 'job_url' not in data:
            return jsonify({"error": "Job URL is required"}), 400
        
        job_url = data['job_url']
        job_description, company_name = JobDescriptionInterface(job_url).get_job_description(load_from_file=True, save_to_file=True)
        
        return jsonify({
            "status": "success",
            "job_description": job_description,
            "company_name": company_name
        })
        
    except Exception as e:
        logging.error(f'Error extracting job description: {e}')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    setup_logging()
    logging.info("Starting AI Resume Creator Flask Server...")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 3000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
