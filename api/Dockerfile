FROM python:3.12-alpine
RUN pip install flask --no-cache-dir
WORKDIR /app
COPY api.py .
CMD ["python", "api.py"]
