FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (e.g. for building some python packages if needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Fix Windows CRLF line endings and make start.sh executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Expose port (Render ignores EXPOSE but good for local)
EXPOSE 8000

# Run the unified start script
CMD ["./start.sh"]
