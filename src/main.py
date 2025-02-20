from resume_parser import ResumeParser
from keyword_extractor import KeywordExtractor
from ats_scorer import ATSScorer
from resume_generator import ResumeGenerator
from ai_enhancer import AIEnhancer  # Optional
from job_description_interface import JobDescriptionInterface
# Load resume
resume_parser = ResumeParser("input/sami.yaml")
resume_summary = resume_parser.get_resume_summary()
exp_skills = resume_parser.get_resume_experiences()
resume_skills = resume_parser.get_resume_skills()

# Get job description
job_description_link = input("Paste the job description link: ")
if not job_description_link:
    raise ValueError("Please provide a job description link")
job_description = JobDescriptionInterface(job_description_link).get_job_description()


# Extract keywords
resume_keywords = ",".join([resume_summary, exp_skills, resume_skills])

resume_extractor = KeywordExtractor(resume_keywords)
job_extractor = KeywordExtractor(job_description)
ats_scorer = ATSScorer()

# Compute ATS score
ats_score, matched_keywords = ats_scorer.calculate_score(resume_extractor, job_extractor)
print(f"ATS Score: {ats_score}%")
print(f"Matched Keywords: {', '.join(matched_keywords)}")

# Enhance resume summary with AI (Optional)
use_ai = input("Would you like AI to improve your resume summary? (yes/no): ").strip().lower()
if use_ai == "yes":
    ai = AIEnhancer(api_key="your-api-key")  # Replace with actual API key
    new_summary = ai.enhance_summary(resume_parser.data["summary"], job_description, matched_keywords)
    resume_parser.update_summary(new_summary)

# Generate resume
resume_parser.data["ats_score"] = ats_score
resume_parser.data["matched_keywords"] = ", ".join(matched_keywords)

resume_generator = ResumeGenerator("/Users/sami/dev/AI_Resume_Creator/example")
resume_generator.generate(resume_parser.data, output_file="output/resume.html")
