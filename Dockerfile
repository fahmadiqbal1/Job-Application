# ── Stage 1: Build frontend + install Node scripts ───────────────────────────
FROM node:20-slim AS node-builder

WORKDIR /build

# Install scripts dependencies (playwright for PDF generation)
COPY scripts/package.json scripts/package-lock.json* ./scripts/
RUN cd scripts && npm ci

# Build React frontend
COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm ci

COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# ── Stage 2: Python runtime ───────────────────────────────────────────────────
FROM python:3.11-slim

# System deps for Playwright
RUN apt-get update && apt-get install -y \
    nodejs npm curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright chromium for portal scanning
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Copy built frontend from stage 1
COPY --from=node-builder /build/frontend/dist ./frontend/dist

# Copy scripts with their node_modules
COPY --from=node-builder /build/scripts/node_modules ./scripts/node_modules

# Create data directories
RUN mkdir -p data/reports data/output data/batch/tracker-additions \
    && mkdir -p data/jds

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
