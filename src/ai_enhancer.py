import openai

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

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert resume writer."},
                      {"role": "user", "content": prompt}]
        )

        return response["choices"][0]["message"]["content"].strip()
