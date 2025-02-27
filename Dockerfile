
# Documentation: https://docs.docker.com/reference/dockerfile/

# Load a standard linux alpine image with python v3.11 preinstalled
FROM python:3.11-alpine

# Change current working dir
WORKDIR /app

# Install dependencies
RUN apk add curl
COPY requirements.txt ./
RUN python -m pip install -r ./requirements.txt

# Copies the local source code to the image's filesystem
COPY . ./

# Runs periodic healthchecks on the app
HEALTHCHECK --interval=1m CMD curl -f "http://localhost:5000/" || exit 1

# Default to running the flask app server
# See https://flask.palletsprojects.com/en/stable/cli/ for more CLI options
CMD ["python3", "./backend.py"]
