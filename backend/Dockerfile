FROM python:3.11-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY

# set proxies for apt & pip if needed
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    ca-certificates \
    curl \
    dnsutils \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Make sure corp-root-ca.crt is in the build context (same folder as Dockerfile)
COPY corp-root-ca.crt /usr/local/share/ca-certificates/corp-root-ca.crt

# Add CA to system store and update
RUN update-ca-certificates

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Append corporate CA to certifi bundle used by requests/transformers/etc.
RUN python -c "import certifi,shutil,sys; c=certifi.where(); print('certifi bundle:', c); \
    from pathlib import Path; p=Path('/usr/local/share/ca-certificates/corp-root-ca.crt'); \
    open(c,'ab').write(p.read_bytes()); print('Appended corp CA to certifi bundle')"
    
# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
