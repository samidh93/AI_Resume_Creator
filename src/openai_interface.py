from openai import OpenAI

class OpenAIInterface:
    def __init__(self, api_key):
        self.openai = OpenAI(api_key=api_key)

    def upload_file(self, file_path):
        return self.openai.files.create(file=open(file_path, "rb"), purpose="assistants")
    
    def get_file_content(self, file_id):
        return self.openai.files.retrieve(file=file_id)
    
    def delete_file(self, file_id):
        return self.openai.files.delete(file=file_id)
    
    def list_files(self):
        return self.openai.files.list()

    # by name
    def get_file_id_by_name(self, file_name):
        files = self.list_files()
        for file in files:
            if file.name == file_name:
                return file.id
        return None
    
    def prompt(self, messages, model="gpt-4o-mini", temperature=0):
        return self.openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature  # Ensures consistency
        )