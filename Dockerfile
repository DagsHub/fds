FROM python:3.7-buster
RUN apt-get update && apt-get -y upgrade

ARG APP_USER=appuser

RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

RUN mkdir -p /usr/src/app/ff

WORKDIR /usr/src/app/ff

COPY . /usr/src/app/ff

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONPATH /usr/src/app/ff

# Change to a non-root user
USER ${APP_USER}:${APP_USER}

ENTRYPOINT ["python", "/usr/src/app/ff/ff/cli.py"]
