
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mv bluesky/bluesky/* bluesky/ && \
	rm -r bluesky/bluesky

ENV FLASK_ENV=development

CMD [ "python", "./run.py" ]
