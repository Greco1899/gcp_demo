# Base image to use
FROM python:3.9-slim

# Expose Gradio port
EXPOSE 7860

# Copy and install requirements
COPY requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

# Copy all files to app directory
COPY . /app

# Change working directory
WORKDIR /app

# Run application
ENTRYPOINT ["python", "app.py"]