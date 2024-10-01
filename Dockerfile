FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV LOG_CONFIG="log.ini"

# Run app.py when the container launches
CMD ["uvicorn", "aws_image_manager.main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "log.ini"]