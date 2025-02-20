from fuzzywuzzy import fuzz
from keyword_extractor import KeywordExtractor

class ATSScorer:
    """Calculates an ATS score based on keyword match and text similarity."""

    def __init__(self):
        pass

    def calculate_score(self, resume_extractor:KeywordExtractor, job_extractor:KeywordExtractor):
        """Compute ATS score based on keyword overlap and text similarity."""
        job_keywords = job_extractor.extract()
        resume_keywords = resume_extractor.extract()
        print(f"Job keywords: {job_keywords}")
        print(f"Resume keywords: {resume_keywords}")
        keyword_overlap = set(resume_keywords) & set(job_keywords)
        keyword_score = len(keyword_overlap) / len(job_keywords) * 100 if job_keywords else 0

        text_similarity = fuzz.partial_ratio(job_extractor.text.lower(), resume_extractor.text.lower())

        ats_score = (0.6 * keyword_score) + (0.4 * text_similarity)

        return round(ats_score, 2), keyword_overlap
