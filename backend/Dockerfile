FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn mysqlclient

COPY . .

EXPOSE 8000

# Run auto-alignment and migrations automatically before starting the server
CMD sh -c "python align_schema.py && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 config.wsgi:application"
