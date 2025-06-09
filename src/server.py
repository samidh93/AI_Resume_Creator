import os
import logging
import tempfile
import yaml
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from langdetect import detect
import uuid
import json
# Import the modules from main.py
from resume_parser import ResumeParser
from resume_generator import ResumeGenerator
from resume_enhancer import ResumeEnhancer 
from resume_analyzer import ResumeAnalyzer
from job_data import JobData
# Set up logger for this module
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure upload settings - use input directory for uploaded resumes
project_root = Path(__file__).parent.parent
INPUT_FOLDER = project_root / 'input'
ALLOWED_EXTENSIONS = {'yaml', 'yml', 'txt'}
app.config['INPUT_FOLDER'] = str(INPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

logger.info(f"Server configuration:")
logger.info(f"  - Project root: {project_root}")
logger.info(f"  - Input folder: {INPUT_FOLDER}")
logger.info(f"  - Allowed extensions: {ALLOWED_EXTENSIONS}")
logger.info(f"  - Max file size: {app.config['MAX_CONTENT_LENGTH']} bytes")

# Ensure required directories exist
try:
    INPUT_FOLDER.mkdir(exist_ok=True)
    (project_root / 'input' / 'company_resume').mkdir(exist_ok=True)
    (project_root / 'output' / 'generated_resume').mkdir(exist_ok=True)
    logger.info("Required directories created/verified successfully")
except Exception as e:
    logger.error(f"Failed to create required directories: {e}")
    raise

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

def allowed_file(filename):
    """Check if file extension is allowed"""
    logger.debug(f"Checking if file is allowed: {filename}")
    is_allowed = '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    logger.debug(f"File {filename} allowed: {is_allowed}")
    return is_allowed

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
    logger.debug(f"Health check request from IP: {client_ip}")
    
    response = {"status": "healthy", "message": "AI Resume Creator API is running"}
    logger.info("Health check completed successfully")
    return jsonify(response)

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    """
    Generate a resume based on uploaded resume file and job description
    Expects:
    - resume_file: YAML resume file
    - job_data: JSON string with format: {"job_id": "123", "job_title": "Software Engineer", "job_description": "...", "company_name": "Company"} (optional)
    - language: Language for resume (optional, defaults to 'auto')
    """
    request_id = str(uuid.uuid4())[:8]  # Short request ID for tracking
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
    
    logger.info(f"[{request_id}] Resume generation request started from IP: {client_ip}")
    
    # Log request details
    logger.debug(f"[{request_id}] Request details:")
    logger.debug(f"[{request_id}]   - Content type: {request.content_type}")
    logger.debug(f"[{request_id}]   - Content length: {request.content_length}")
    logger.debug(f"[{request_id}]   - Form data keys: {list(request.form.keys())}")
    logger.debug(f"[{request_id}]   - Files: {list(request.files.keys())}")
    
    resume_path = None
    
    try:
        # Check if resume file is provided
        logger.debug(f"[{request_id}] Validating resume file upload")
        if 'resume_file' not in request.files:
            logger.warning(f"[{request_id}] No resume file provided in request")
            return jsonify({"error": "No resume file provided"}), 400
        
        resume_file = request.files['resume_file']
        if resume_file.filename == '':
            logger.warning(f"[{request_id}] Empty filename provided")
            return jsonify({"error": "No resume file selected"}), 400
        
        logger.info(f"[{request_id}] Resume file received: {resume_file.filename}")
        
        if not allowed_file(resume_file.filename):
            logger.warning(f"[{request_id}] Invalid file type: {resume_file.filename}")
            return jsonify({"error": "Invalid file type. Only YAML files are allowed"}), 400
        
        logger.debug(f"[{request_id}] Saving uploaded resume file")
        filename = secure_filename(resume_file.filename)
        # Check if original filename exists and create backup if needed
        resume_path = Path(app.config['INPUT_FOLDER']) / filename
        try:
            resume_file.save(resume_path)
            logger.info(f"[{request_id}] Resume file saved successfully: {resume_path}")
        except Exception as e:
            logger.error(f"[{request_id}] Failed to save resume file: {e}")
            return jsonify({"error": f"Failed to save resume file: {str(e)}"}), 500
        
        # Get job data
        job_data = request.form.get('job_data')
        language = request.form.get('language', 'auto')
        
        logger.info(f"[{request_id}] Request parameters:")
        logger.info(f"[{request_id}]   - Job data: {job_data}")
        logger.info(f"[{request_id}]   - Language: {language}")
        
        # Parse job data from JSON string
        try:
            if job_data and job_data.strip():  # Check if job_data exists and is not empty
                job_data_dict = json.loads(job_data)
                logger.debug(f"[{request_id}] Job data parsed successfully: {job_data_dict}")
                
                # Validate required fields for JobData
                required_fields = ['job_id', 'job_title', 'job_description', 'company_name']
                missing_fields = [field for field in required_fields if field not in job_data_dict]
                
                if missing_fields:
                    logger.error(f"[{request_id}] Missing required job data fields: {missing_fields}")
                    return jsonify({"error": f"Missing required job data fields: {missing_fields}"}), 400
            else:
                job_data_dict = {}
                logger.warning(f"[{request_id}] No job data provided or empty")
                
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] Failed to parse job data JSON: {e}")
            return jsonify({"error": f"Invalid job data format: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"[{request_id}] Error processing job data: {e}")
            return jsonify({"error": f"Error processing job data: {str(e)}"}), 400
        
        # Create output directory - use generated_resume subdirectory
        logger.debug(f"[{request_id}] Setting up output directory")
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'output' / 'generated_resume'
        output_dir.mkdir(exist_ok=True)
        logger.debug(f"[{request_id}] Output directory ready: {output_dir}")
        
        logger.info(f'[{request_id}] Starting AI Resume Creator processing...')
        
        # Load resume
        logger.info(f"[{request_id}] Loading and parsing resume")
        try:
            resume_parser = ResumeParser(resume_path)
            logger.info(f"[{request_id}] Resume parsed successfully")
        except Exception as e:
            logger.error(f"[{request_id}] Failed to parse resume: {e}")
            return jsonify({"error": f"Failed to parse resume: {str(e)}"}), 500
        
        resume_lang = language
        # Process job description if provided
        if job_data_dict:
            job_data_object = JobData(**job_data_dict)
            job_id, job_title, job_description, company_name = job_data_object.get_job_data()
        else:
            # No job data provided - use default values
            job_id = None
            job_title = None
            job_description = None
            company_name = "Unknown Company"
            logger.info(f"[{request_id}] No job data provided - proceeding with basic resume generation")
        
        # If job description is provided, enhance the resume
        if job_description:
            logger.info(f"[{request_id}] Starting resume enhancement process")
            try:
                logger.debug(f"[{request_id}] Running ATS analysis")
                ra = ResumeAnalyzer(job_description, resume_parser)
                ats_result = ra.compare()
                logger.info(f"[{request_id}] ATS analysis completed - Score: {ats_result.ats_score}")
                
                logger.debug(f"[{request_id}] Enhancing resume based on ATS results")
                resume_enhancer = ResumeEnhancer(resume_path, company_name, job_title)
                enhanced_resume_path = resume_enhancer.enhance_resume(ats_result)
                logger.info(f"[{request_id}] Resume enhanced successfully: {enhanced_resume_path}")
                
                # Use enhanced resume for generation
                resume_parser = ResumeParser(enhanced_resume_path)
                
                if resume_lang == 'auto':
                    logger.debug(f"[{request_id}] Auto-detecting language from job description")
                    resume_lang = detect(job_description)
                    logger.info(f"[{request_id}] Language detected: {resume_lang}")
                    
            except Exception as e:
                logger.error(f"[{request_id}] Resume enhancement failed: {e}")
                return jsonify({"error": f"Resume enhancement failed: {str(e)}"}), 500
        
        # Generate resume using synchronous methods
        logger.info(f"[{request_id}] Starting resume generation")
        try:
            example_dir = Path(__file__).parent.parent / "example"
            logger.debug(f"[{request_id}] Using template directory: {example_dir}")
            
            actual_resume_path = enhanced_resume_path if job_description else resume_path
            resume_generator = ResumeGenerator(actual_resume_path, output_dir, example_dir, resume_lang)            
            # Generate HTML and PDF using synchronous methods with proper event loop handling
            logger.info(f"[{request_id}] Generating HTML resume")
            resume_html = resume_generator.generate_html(resume_parser.data)
            
            logger.info(f"[{request_id}] Converting HTML to PDF")
            pdf_path = resume_generator.html_to_pdf(resume_html)
            
            logger.info(f'[{request_id}] Resume generated successfully: {pdf_path}')
            
        except Exception as e:
            logger.error(f"[{request_id}] Resume generation failed: {e}")
            return jsonify({"error": f"Resume generation failed: {str(e)}"}), 500
        
        # Prepare response
        response_data = {
            "status": "success",
            "message": "Resume generated successfully",
            "pdf_path": str(pdf_path),
            "company_name": company_name,
            "language": resume_lang
        }
        
        logger.info(f'[{request_id}] Resume generation completed successfully!')
        logger.info(f'[{request_id}] Response: {response_data}')
        
        # Optional: Clean up uploaded file after successful processing
        # Uncomment the following lines if you want to remove uploaded files after processing
        # try:
        #     if resume_path and resume_path.exists():
        #         resume_path.unlink()
        #         logger.info(f"[{request_id}] Cleaned up uploaded file: {resume_path}")
        # except Exception as e:
        #     logger.warning(f"[{request_id}] Failed to clean up uploaded file: {e}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f'[{request_id}] Unexpected error occurred: {e}', exc_info=True)
        return jsonify({"error": str(e)}), 500

# Add request logging middleware
@app.before_request
def log_request_info():
    """Log incoming request details"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
    logger.debug(f"Incoming request: {request.method} {request.path} from {client_ip}")

@app.after_request
def log_response_info(response):
    """Log response details"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
    logger.debug(f"Response: {response.status_code} for {request.method} {request.path} to {client_ip}")
    return response

if __name__ == '__main__':
    logger.info("Initializing AI Resume Creator Flask Server...")
    
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    log_path = output_dir / 'resume_generation.log'
    
    setup_logging(log_path)
    logger.info("AI Resume Creator Flask Server starting...")
    
    # Log server configuration
    port = int(os.environ.get('PORT', 3000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Server configuration:")
    logger.info(f"  - Host: 0.0.0.0")
    logger.info(f"  - Port: {port}")
    logger.info(f"  - Debug mode: {debug_mode}")
    logger.info(f"  - Log file: {log_path}")
    
    # Run the Flask app
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug_mode
        )
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}")
        raise
