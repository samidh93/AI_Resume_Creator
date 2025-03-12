#!/bin/bash

# Build the Docker image
#docker build -t ai-resume-creator-python-image -f Dockerfile .

# Run the Docker container
docker run \
  -v $(pwd)/output/:/app/output/ \
  -v $(pwd)/input/:/app/input/ \
  ai-resume-creator-python-image \
  --resume /app/input/sami_dhiab_resume.yaml \
  --url "https://www.linkedin.com/jobs/view/4175141028"

# docker run -it \
#  --entrypoint /bin/bash \
#  -v $(pwd)/output/:/app/output/ \
#  -v $(pwd)/input/:/app/input/ \
#  ai-resume-creator-python-image



# Uncomment and adjust additional options as needed:
#  --name ai-resume-creator-python-container \
#  python main.py \
#  --output "/app/output/output-file.yaml" \
#  --language "en"
#  --url "https://www.linkedin.com/jobs/view/4114811878/"


# remove all containers
docker rm -f $(docker ps -a -q)
