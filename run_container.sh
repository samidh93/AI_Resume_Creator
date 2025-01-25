# build the docker image
docker build -t ai-resume-creator-python-image -f Dockerfile .
# run the docker container
docker run --memory=2g --cpus=2 -v $(pwd)/output/:/app/output/ -v $(pwd)/input/:/app/input/ --name ai-resume-creator-python-container ai-resume-creator-python-image