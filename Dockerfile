
FROM python:3.7

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./bluesky/bluesky ./bluesky/bluesky
COPY .env run.py VERSION ./
COPY ./bluebird ./bluebird
RUN find . -type d -name '__pycache__' -prune -exec rm -r {} \;

ENV FLASK_ENV=development
ENV BB_LOGS_ROOT="/var/log/bluebird"

CMD python ./run.py --sim-host=$BS_HOST
