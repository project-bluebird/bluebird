
FROM python:3

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["export", "FLASK_ENV=development"]
CMD [ "python", "./run.py" ]