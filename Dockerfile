FROM python:3.8

WORKDIR /eventManager

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m pip install --upgrade pip

EXPOSE 6379

# Copy your project files
COPY . .

# Correct CMD syntax
CMD ["celery", "-A", "eventManager", "worker", "--uid=nobody"]

