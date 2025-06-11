# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv and curl (for health checks)
RUN pip install uv && \
    apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the dependency definition file
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --system --no-cache .

# Copy the rest of the application's source code
COPY ./src /app/src

# Set default environment variables (can be overridden at runtime)
ENV DATABASE_URL=sqlite:///app/data/burn_after_reading.db
ENV CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENV HOST=0.0.0.0
ENV PORT=8001

# Create data directory for database and set ownership
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app/data

# Change ownership of application files to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Create an entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the configured port
EXPOSE 8001

# Add health check
# The healthcheck is now defined in docker-compose.yml with a start_period for more robustness.

# Use the entrypoint script to run the application
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--root-path", "/api"] 