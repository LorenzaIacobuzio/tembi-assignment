FROM python:3.11-bullseye AS playwright-builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies needed for Playwright and Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      python3-dev \
      libffi-dev \
      libnss3 \
      libnspr4 \
      libatk1.0-0 \
      libatk-bridge2.0-0 \
      libcups2 \
      libxss1 \
      libasound2 \
      libxrandr2 \
      libgbm1 \
      libpangocairo-1.0-0 \
      libgtk-3-0 \
      libdbus-1-3 \
      libxcomposite1 \
      libxdamage1 \
      libxfixes3 \
      libdrm2 \
      libxkbcommon0 \
      libatspi2.0-0 \
      fonts-liberation \
      wget \
      ca-certificates \
      xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright Python and browsers with dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install playwright==1.35.0 \
    && python -m playwright install --with-deps

FROM python:3.11-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      libnss3 \
      libnspr4 \
      libatk1.0-0 \
      libatk-bridge2.0-0 \
      libcups2 \
      libxss1 \
      libasound2 \
      libxrandr2 \
      libgbm1 \
      libpangocairo-1.0-0 \
      libgtk-3-0 \
      libdbus-1-3 \
      libxcomposite1 \
      libxdamage1 \
      libxfixes3 \
      libdrm2 \
      libxkbcommon0 \
      libatspi2.0-0 \
      fonts-liberation \
      wget \
      ca-certificates \
      xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages and Playwright browsers from builder stage
COPY --from=playwright-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=playwright-builder /ms-playwright /ms-playwright

# Install Python requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir cryptography
RUN pip install --no-cache-dir alembic

# Copy application code
COPY src/ /app/src
COPY .env.example /app/.env
COPY scripts/wait_for_db.py /app/scripts/wait_for_db.py

ENV PYTHONPATH=/app

# Entry point
CMD ["bash", "-c", "python scripts/wait_for_db.py && alembic upgrade head && python src/scraper/main.py"]
