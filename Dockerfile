FROM python:3.7-buster
RUN apt-get update && apt-get -y upgrade

ARG APP_USER=appuser

RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

RUN mkdir -p /usr/src/app/fds

RUN mkdir -p /repo

COPY . /usr/src/app/fds

WORKDIR /usr/src/app/fds

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONPATH /usr/src/app/fds

# Change to a non-root user
USER ${APP_USER}:${APP_USER}

WORKDIR /repo

ENTRYPOINT ["python", "/usr/src/app/fds/fds/cli.py"]
