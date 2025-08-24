import os
from pathlib import Path
import logging
import json

# Set up logger for this module
logger = logging.getLogger(__name__)

class JobData:
    def __init__(self,job_id, job_title, job_description, company_name):
        self.job_id = job_id
        self.job_title = job_title
        self.job_description = job_description
        self.company_name = company_name

    def get_job_data(self):
        return self.job_id, self.job_title, self.job_description, self.company_name
    
    def write_job_data_to_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.job_data, f)