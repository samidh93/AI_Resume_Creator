import openai
import yaml
from pathlib import Path

class AIEnhancer:
    """Uses OpenAI GPT to optimize resume content with ATS keywords."""

    def __init__(self, api_key):
        openai.api_key = api_key

    def enhance_summary(self, summary, job_description, keywords):
        """Enhances resume summary with AI-generated content."""
        prompt = f"""
        Improve the following resume summary by naturally incorporating these keywords: {', '.join(keywords)}.

        Resume:
        {summary}

        Optimized Resume:
        """

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert resume writer."},
                      {"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    secrets = yaml.safe_load(open(secrets_path, 'r'))
    api_key = secrets['api_key']
    ai = AIEnhancer(api_key=api_key)  # Replace with actual API key
    summary = "I am a software engineer with experience in Python, Java, and SQL."
    keywords = ["software engineering", "Cpp", "Javascript", "NOSQL"]
    job_description = "We are looking for a software engineer with expertise in Python, Java, and SQL."
    new_summary = ai.enhance_summary(summary, job_description, keywords)
    print(new_summary)