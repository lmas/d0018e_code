
# Documentation: https://docs.docker.com/reference/dockerfile/

# Load a standard linux alpine image with python v3.11 preinstalled
FROM python:3.11-alpine

# Install dependencies
RUN apk add curl
RUN python -m pip install -r ./requirements.txt

# Copies the local source code to the image's filesystem
COPY . /app/

# Change current working dir
WORKDIR /app

# Runs periodic healthchecks on the app
HEALTHCHECK --interval=1m CMD curl -f "http://localhost:5000/" || exit 1

# Default to running the flask app server
# See https://flask.palletsprojects.com/en/stable/cli/ for more CLI options
CMD ["flask", "--app=./backend.py", "run", "--host=0.0.0.0", "--port=5000"]
