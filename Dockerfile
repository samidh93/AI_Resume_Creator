# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary Chromium dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    nano \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    fonts-liberation \
    libgbm1 \
    libpango1.0-0 \
    xdg-utils \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# declare env variable to use later in python to choose which browser to use
ENV CONTAINER=true
# Copy the requirements file into the container
COPY requirements.txt .

# Copy the main application file
COPY main.py .

# Copy necessary directories and files into the container
COPY python/ python/

COPY tests/ tests/
COPY example/ example/
COPY README.md .
COPY javascript/ javascript/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
ENTRYPOINT ["python", "main.py"]
# test the application
#ENTRYPOINT ["python", "tests/test_pyppeteer_headless.py"]
