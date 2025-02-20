from jinja2 import Environment, FileSystemLoader

class ResumeGenerator:
    """Generates an HTML resume from a YAML data structure."""

    def __init__(self, template_path):
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.template = self.env.get_template("resume_template.html")

    def generate(self, resume_data, output_file="resume.html"):
        """Render resume data into an HTML file."""
        output_html = self.template.render(resume_data)

        with open(output_file, "w") as file:
            file.write(output_html)

        print(f"Resume saved as {output_file}")
