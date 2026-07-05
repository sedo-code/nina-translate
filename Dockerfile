FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY app_cloud.py .

# Expose the default port (Hugging Face Spaces uses 7860 by default)
EXPOSE 7860

# Define the environment variable for Port
ENV PORT=7860

# Run the cloud server
CMD ["python", "app_cloud.py"]
