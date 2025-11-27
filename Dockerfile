# Multi-stage Dockerfile for MBTI Processing Service Backend
FROM python:3.11-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime system dependencies for PDF processing and image libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for WeasyPrint HTML to PDF conversion
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    # Fonts for PDF generation
    fontconfig \
    libxrender1 \
    # Required for pdf2image (PDF to image conversion)
    poppler-utils \
    # Required for health checks
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN mkdir -p /app /app/output /app/backend/media /tmp/tmp_pdf

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ /app/backend/
COPY textfiles/ /app/textfiles/

# Set environment variables
ENV PROJECT_BASE_DIR=/app \
    OUTPUT_DIR=/app/output \
    INPUT_DIR=/app/input \
    MEDIA_DIR=/app/backend/media \
    PYTHONPATH=/app/backend/src:/app/backend/src/MBTInfo:/app/backend/src/MBTInterpret \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run the application (production mode - no reload)
CMD ["uvicorn", "backend.src.MBTInfo.server:app", "--host", "0.0.0.0", "--port", "3000"]

