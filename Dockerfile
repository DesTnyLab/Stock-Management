# Use a modern base image to ensure updated libraries
FROM python:3.10-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=tirpura.settings

# Define the working directory
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       libpango1.0-dev \
       libcairo2-dev \
       gettext \
       netcat-openbsd \
       gcc \
       postgresql \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python pip
RUN pip install --upgrade pip

# Copy and install Python dependencies
COPY ./requirements.txt $APP_HOME/requirements.txt
RUN pip install -r requirements.txt

# Copy project files into the container
COPY . $APP_HOME

# Copy and configure entrypoint scripts
COPY ./entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ./start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

# Expose the application port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint"]
