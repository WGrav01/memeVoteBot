# Use a PyPy base image
FROM pypy:3.10-slim-bookworm

# Set the working directory
WORKDIR /usr/src/app

# Copy your bot's source code into the container
COPY . .

# Set up the token
ARG TOKEN

# Potential pip fix
RUN pip config --user set global.progress_bar off

# Install Pycord and other dependencies
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY . /opt/app

# Move back to main directory
WORKDIR /usr/src/app

# Set the entrypoint to run your bot
CMD ["pypy3", "main.py"]
