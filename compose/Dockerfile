FROM python:3.8

WORKDIR /app

# Install dependencies
COPY ../requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Copy your project files
COPY .. .

## Correct CMD syntax
#CMD ["celery", "-A", "src.eventManager", "worker", "--uid=nobody"]

