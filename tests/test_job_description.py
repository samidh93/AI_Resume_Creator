import unittest
import asyncio
from ..src.linkedin_job_description import LinkedinJobDescription

class TestJobDescriptionExtraction(unittest.TestCase):

    def setUp(self):
        self.job_url = 'https://www.linkedin.com/jobs/view/4114811878/'  # Example job URL
        self.job_description_extractor = LinkedinJobDescription(self.job_url)

    def test_extract_job_description(self):
        # Test the extraction of job description
        job_description = asyncio.run(self.job_description_extractor.get_job_description())
        self.assertIsInstance(job_description, str)  # Check if the output is a string
        self.assertGreater(len(job_description), 0)  # Ensure job description is not empty

    def test_invalid_url(self):
        # Test handling of an invalid URL
        invalid_extractor = LinkedinJobDescription('https://invalid.url')
        job_description = asyncio.run(invalid_extractor.get_job_description())
        self.assertEqual(job_description, 'Error fetching job description.')  # Check for error message

if __name__ == '__main__':
    unittest.main()
