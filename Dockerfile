FROM python:3.8

WORKDIR /eventManager

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 6379

# Copy your project files
COPY . .

# Set the entrypoint or command to run Celery
CMD ["celery -A eventManager worker --uid=nobody"]
