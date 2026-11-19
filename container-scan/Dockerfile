FROM aquasec/trivy:0.76.2@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb AS trivy

FROM python:3.15-alpine

WORKDIR /app
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scan.py .

# /work and /tmp are emptyDir volumes: the root filesystem is read-only.
ENV HOME=/work TRIVY_CACHE_DIR=/work/cache PYTHONDONTWRITEBYTECODE=1
USER 65532:65532
ENTRYPOINT ["python", "/app/scan.py"]
