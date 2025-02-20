# AI Resume Creator
An intelligent resume generator that tailors your resume based on job descriptions using AI.

## Prerequisites
- Python 3
- pip (Python package installer)

## Getting Started
## How to Get OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/settings/organization/api-keys).
2. Log in to your OpenAI account.
3. Click on the "Create API Key" button to generate a new key.
4. Copy the generated API key and save it securely.

## How to Get Gemini API Key
1. Visit the Gemini API documentation or the respective platform.
2. Follow the registration process to create an account if you don't have one.
3. Once logged in, navigate to the API keys section.
4. Generate a new API key and copy it for use in your application.

## Copying Files from Example to Input
1. Locate the example files in the `example` directory.
2. Copy the necessary files to the `input` directory for processing.
3. Ensure that the files are correctly formatted as required by the application.

## Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/samidh93/AI_Resume_Creator.git
cd AI_Resume_Creator
```

### 2. Create and Activate Virtual Environment
#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

### 3. Install Dependencies
Once your virtual environment is activated, install the required packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python src/main.py
```
application arguments:
- --resume : Path to the resume YAML file
- --style : Path to the CSS style file
- --output : Output directory for generated files
- --ai_model : AI model to use (openai or gemini)
- --api_key : API key for the AI model
- --url : Job description Url
- --language : Language for the resume

### 5. Output
- resume files will be generated in the output directory.

### 6. Run the Application within a container
```bash
bash run_container.sh
```
open the script and choose the options to run the application in a container.
- --resume : Path to the resume YAML file
- --style : Path to the CSS style file
- --output : Output directory for generated files
- --ai_model : AI model to use (openai or gemini)
- --api_key : API key for the AI model
- --url : Job description Url
- --language : Language for the resume


## Vs code Extensions
- code runner extension
- Docker extension
