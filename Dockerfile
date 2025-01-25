# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Copy the main application file
COPY main.py .

# Copy necessary directories and files into the container
COPY python/ python/
#COPY input/ input/
#COPY output/ output/
COPY tests/ tests/
COPY example/ example/
COPY README.md .
COPY javascript/ javascript/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
#ENTRYPOINT ["python", "main.py"]
#ENTRYPOINT ["python", "tests/test_pyppeteer_headless.py"]
# Set the entrypoint to keep the container alive
ENTRYPOINT ["bash", "-c", "while true; do sleep 30; done"]