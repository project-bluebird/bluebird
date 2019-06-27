
FROM python:3.6

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mv bluesky/bluesky/* bluesky/ && \
    rm -r bluesky/bluesky && \
    find . -type d -name '__pycache__' -prune -exec rm -r {} \;

ENV FLASK_ENV=development
ENV BB_LOGS_ROOT="/var/log/bluebird"

CMD python ./run.py --bluesky_host=$BS_HOST --sim_mode=$SIM_MODE
