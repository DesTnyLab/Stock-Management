FROM python:3.10.0-slim-buster

ENV APP_HOME=/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

LABEL maintainer='api.imperfect@gmail.com'
LABEL youtube="https://www.youtube.com/c/APIImperfect"
LABEL decription="Development image for Real Estate Project"

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=tirpura.settings

RUN apt-get update \
  && apt-get install -y build-essential \
  && apt-get install -y libpq-dev \
  && apt-get install -y gettext \
  && apt-get -y install netcat gcc postgresql \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

COPY ./requirements.txt /app/requirements.txt 

RUN pip3 install -r requirements.txt

COPY ./entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start




ENTRYPOINT [ "/entrypoint"]