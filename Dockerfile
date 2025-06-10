# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, a fast Python package installer
RUN pip install uv

# Copy the dependency definition file
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --system --no-cache .

# Copy the rest of the application's source code
COPY ./src /app/src

# Expose port 8000 for the Uvicorn server
EXPOSE 8000

# Command to run the application
# Uvicorn will run the FastAPI app instance located in the 'app' variable inside the /app/src/main.py file.
# --host 0.0.0.0 is required to make the server accessible from outside the container.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 