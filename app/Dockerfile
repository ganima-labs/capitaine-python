FROM python:3.11-slim
WORKDIR /srv
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install fastapi uvicorn[standard] httpx pydantic sqlite-utils python-multipart pytest pytest-cov
COPY app/backend /srv/backend
COPY app/frontend /srv/frontend
COPY tests /srv/tests
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/srv
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
