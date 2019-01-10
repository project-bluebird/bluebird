
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# TODO Add .dockerignore for stuff we don't need
COPY . .

CMD [ "export", "FLASK_ENV=development" ]
CMD [ "python", "./run.py" ]