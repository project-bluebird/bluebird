
# NOTE(rkm 2020-04-26) Until the next BlueBird docker release, this base image must be built first
FROM bluebird

RUN  apt-get update \
  && apt-get install -y apt-utils netcat sudo bash \
  && rm -rf /var/lib/apt/lists/*

COPY requirements-nats.txt .
COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./wait-for-it.sh

ARG NATS_PYPI_INDEX
ARG PYPIPWD_PORT

# NOTE(rkm 2020-04-26) One of these must be set
RUN test -n "$NATS_PYPI_INDEX" || test -n "$PYPIPWD_PORT"

RUN \
  if [ ! -z "$NATS_PYPI_INDEX" ]; then \
      pip install --extra-index-url "$NATS_PYPI_INDEX" -r requirements-nats.txt; \
  else \
      pip install -i $(nc 0.0.0.0 "$PYPIPWD_PORT") -r requirements-nats.txt; \
  fi

CMD python ./run.py --sim-type=machcoll --sim-host=$BS_HOST
