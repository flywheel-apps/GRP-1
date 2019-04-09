#flywheel/csv-import

# Start with python 3
FROM python:3 as base
MAINTAINER Flywheel <support@flywheel.io>

# Copy the requirements file
COPY requirements.txt ./requirements.txt

# Install pandas
RUN pip install -r ./requirements.txt

# Flywheel spec (v0)
WORKDIR /flywheel/v0

# Copy executables into place
COPY spreadsheet_importer.py ./run.py

# Add a default command
CMD ["python run.py"]

# Make a target for testing locally
FROM base as testing
COPY tests ./tests
RUN pip install -r tests/requirements.txt

