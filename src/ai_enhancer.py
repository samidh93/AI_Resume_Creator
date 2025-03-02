import openai
import yaml
from pathlib import Path
import json

class AIEnhancer:
    """Uses OpenAI GPT to optimize resume content with ATS keywords."""

    def __init__(self, api_key):
        openai.api_key = api_key

    def enhance_summary(self, summary, keywords):
        """Enhances resume summary with AI-generated content and returns JSON output."""
        prompt = f"""
        Improve the following resume summary by naturally incorporating these keywords: {', '.join(keywords)}.

        Original Summary: {summary}

        Return only the optimized summary in JSON format with the key 'summary'.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},  # Corrected format
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Return responses strictly in JSON format."},
                {"role": "user", "content": prompt}
            ]
        )

        response= response.choices[0].message.content
        return json.loads(response)['summary']

    def enhance_skills(self, skills, keywords):
        """Enhances resume skills with AI-generated content and returns JSON output."""
        prompt = f"""
        Improve the following resume skills by naturally incorporating these keywords: {', '.join(keywords)}.

        Original skills: {skills}

        Return only the optimized skills in JSON format with the key 'skills'.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},  # Corrected format
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Return responses strictly in JSON format."},
                {"role": "user", "content": prompt}
            ]
        )

        response= response.choices[0].message.content
        return json.loads(response)['skills']
    
if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    secrets = yaml.safe_load(open(secrets_path, 'r'))
    api_key = secrets['api_key']
    
    ai = AIEnhancer(api_key=api_key)
    summary = "I am a software engineer with experience in Python, Java, and SQL."
    keywords = ["software engineering", "Cpp", "Javascript", "NOSQL"]
    
    #new_summary = ai.enhance_summary(summary, keywords)
    #print(new_summary)
    skills = ["Python", "Java", "SQL"]
    keywords = ["software engineering", "Cpp", "Javascript", "NOSQL"]
    new_skills = ai.enhance_skills(skills, keywords)
    print(new_skills)
