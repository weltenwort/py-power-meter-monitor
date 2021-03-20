FROM python:3.9.2-alpine as base

RUN adduser --disabled-password py-logarex-monitor
USER py-logarex-monitor
WORKDIR /home/py-logarex-monitor

FROM base as build

ADD --chown=py-logarex-monitor https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py ./
RUN python get-poetry.py

RUN mkdir -p src/py_logarex_monitor
COPY py_logarex_monitor ./src/py_logarex_monitor/
COPY poetry.lock pyproject.toml default-config.toml ./src/
RUN cd ./src \
  && ~/.poetry/bin/poetry build --format wheel

FROM base

COPY --from=build "/home/py-logarex-monitor/src/dist/py_logarex_monitor-*-py3-none-any.whl" ./
RUN pip install --user $(ls py_*.whl)

ENTRYPOINT ["/home/py-logarex-monitor/.local/bin/py-logarex-monitor"]