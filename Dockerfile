
FROM python:3.6

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mv bluesky/bluesky/* bluesky/ && \
	rm -r bluesky/bluesky

ENV FLASK_ENV=development

# BS_HOST is set if run through docker-compose. Otherwise need to set manually
CMD python ./run.py --bluesky_host=$BS_HOST
