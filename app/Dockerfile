FROM python:3.11-slim
WORKDIR /srv
RUN pip install fastapi uvicorn[standard] httpx pydantic sqlite-utils python-multipart
COPY backend /srv/backend
COPY frontend /srv/frontend
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/srv
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
