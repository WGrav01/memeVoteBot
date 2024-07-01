# Use a PyPy base image
FROM pypy:3.10-bookworm

# Set the working directory
WORKDIR /usr/src/app

# Copy your bot's source code into the container
COPY . .

# Set up the token
ARG TOKEN

# Install Pycord and other dependencies
RUN pip install -r requirements.txt

# Set the entrypoint to run your bot
CMD ["pypy3", "main.py"]
