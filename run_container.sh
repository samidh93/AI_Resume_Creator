#!/bin/bash

# Build the Docker image
docker build -t ai-resume-creator-python-image -f Dockerfile .

# Run the Docker container
docker run \
  -v $(pwd)/output/:/app/output/ \
  -v $(pwd)/input/:/app/input/ \
  ai-resume-creator-python-image \
  --resume /app/input/sami_dhiab_resume.yaml \

# Uncomment and adjust additional options as needed:
#  --memory=2g --cpus=2 \
#  --name ai-resume-creator-python-container \
#  python main.py \
#  --style "some-style" \
#  --output "/app/output/output-file.yaml" \
#  --ai_model "model-name" \
#  --api_key "your-api-key" \
#  --language "en"
#  --url "https://www.linkedin.com/jobs/view/4114811878/"


# remove all containers
docker rm -f $(docker ps -a -q)
