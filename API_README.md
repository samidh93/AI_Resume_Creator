# AI Resume Creator Flask API

This Flask server provides REST API endpoints for the AI Resume Creator functionality from `main.py`.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the `input/secrets.yaml` file configured with your API keys.

## Running the Server

```bash
cd src
python server.py
```

The server will start on `http://localhost:3000` by default.

## API Endpoints

### 1. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Check if the API is running
- **Response**: 
```json
{
  "status": "healthy",
  "message": "AI Resume Creator API is running"
}
```

### 2. Generate Resume
- **URL**: `/generate-resume`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Description**: Generate an enhanced resume based on a job description
- **Parameters**:
  - `resume_file` (file, required): YAML resume file
  - `job_description_url` (string, optional): URL to job description
  - `job_description_text` (string, optional): Direct job description text
  - `language` (string, optional): Language for resume (default: 'auto')

- **Response**:
```json
{
  "status": "success",
  "message": "Resume generated successfully",
  "pdf_path": "output/resume.pdf",
  "company_name": "Company Name",
  "language": "en"
}
```

### 3. Download Resume
- **URL**: `/download-resume/<filename>`
- **Method**: `GET`
- **Description**: Download a generated resume PDF
- **Response**: PDF file download

### 4. Analyze Resume
- **URL**: `/analyze-resume`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Description**: Analyze resume against job description without generating a new resume
- **Parameters**:
  - `resume_file` (file, required): YAML resume file
  - `job_description_url` (string, optional): URL to job description
  - `job_description_text` (string, optional): Direct job description text

- **Response**:
```json
{
  "status": "success",
  "message": "Resume analysis completed",
  "analysis_result": {...},
  "company_name": "Company Name"
}
```

### 5. Extract Job Description
- **URL**: `/job-description`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Description**: Extract job description from a URL
- **Parameters**:
```json
{
  "job_url": "https://example.com/job-posting"
}
```

- **Response**:
```json
{
  "status": "success",
  "job_description": "Job description text...",
  "company_name": "Company Name"
}
```

## Example Usage

### Using curl to generate a resume:

```bash
curl -X POST http://localhost:5000/generate-resume \
  -F "resume_file=@path/to/resume.yaml" \
  -F "job_description_url=https://example.com/job" \
  -F "language=en"
```

### Using curl to analyze a resume:

```bash
curl -X POST http://localhost:5000/analyze-resume \
  -F "resume_file=@path/to/resume.yaml" \
  -F "job_description_text=Software Engineer position requiring Python..."
```

### Using curl to extract job description:

```bash
curl -X POST http://localhost:5000/job-description \
  -H "Content-Type: application/json" \
  -d '{"job_url": "https://example.com/job-posting"}'
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing parameters, invalid file type, etc.)
- `404`: Not Found (for file downloads)
- `500`: Internal Server Error

Error responses include a JSON object with an `error` field describing the issue.

## File Management

- Uploaded files are temporarily stored in the `temp_uploads` directory
- Generated resumes are saved in the `output` directory
- Temporary files are automatically cleaned up after processing 