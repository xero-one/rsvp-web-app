# Base image
FROM python:3.9

LABEL rsvp_app="Chips_Memorial"
LABEL maintainer="DesignBytes.co"
# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /rsvp_app

COPY requirements.txt /rsvp_app/requirements.txt

RUN pip3 --disable-pip-version-check --no-cache-dir install -r /rsvp_app/requirements.txt

COPY . /rsvp_app

ENV LOG_LEVEL debug

EXPOSE 8000

WORKDIR /rsvp_app/app

CMD ["python3", "run.py", "--env", "production"]