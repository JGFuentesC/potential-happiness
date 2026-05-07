FROM python:3.12

# Node.js 22 + curl
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Backend deps (cached until pyproject.toml changes) ────────────────────────
COPY backend/pyproject.toml backend/
RUN pip install --no-cache-dir \
    "fastapi>=0.111" \
    "uvicorn[standard]>=0.29" \
    "sqlalchemy>=2.0" \
    "pydantic>=2.0" \
    "python-jose[cryptography]>=3.3" \
    "bcrypt>=4.0" \
    "python-multipart>=0.0.9"

# ── Frontend deps (cached until package*.json changes) ────────────────────────
COPY frontend/package*.json frontend/
RUN cd frontend && npm ci

# ── Source code ───────────────────────────────────────────────────────────────
COPY backend/ backend/
COPY frontend/ frontend/

# Build the React app — API URL resolves to localhost:8000 at runtime
RUN cd frontend && npm run build

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000 5173

ENTRYPOINT ["/entrypoint.sh"]
