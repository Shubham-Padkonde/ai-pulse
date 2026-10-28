FROM node:24-slim AS web
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_URL="" VITE_PUBLIC_DEMO="true"
RUN npm run build

FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 STATIC_DIR=/app/web
WORKDIR /app/backend
COPY backend/requirements.txt backend/constraints.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=web /build/dist /app/web
COPY scripts/serve.py /app/scripts/serve.py
RUN mkdir -p /data
EXPOSE 8000
# Railway's mounted volume is root-owned. This small pilot uses one process;
# real employee rollout requires the operational hardening in DEPLOYMENT.md.
CMD ["python", "/app/scripts/serve.py"]
