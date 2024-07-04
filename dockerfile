# Use a PyPy base image
FROM pypy:3.10-slim-bullseye

# Set the working directory
WORKDIR /usr/src/app

# Copy your bot's source code into the container
COPY . .

# Set up the token
ARG TOKEN

# Potential pip fix
RUN pip config --user set global.progress_bar off

# Install Pycord and other dependencies
RUN pip install -r requirements.txt

# Set the entrypoint to run your bot
CMD ["pypy3", "main.py"]
