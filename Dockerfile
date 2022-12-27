FROM python:3.11.1-alpine as base

RUN adduser --disabled-password py-power-meter-monitor
USER py-power-meter-monitor
WORKDIR /home/py-power-meter-monitor

FROM base as build

ADD --chown=py-power-meter-monitor https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py ./
RUN python get-poetry.py

RUN mkdir -p src/py_power-meter_monitor src/etc
COPY poetry.lock pyproject.toml ./src/
COPY etc ./src/etc/
COPY py_power_meter_monitor ./src/py_power_meter_monitor/
RUN cd ./src \
  && ~/.poetry/bin/poetry build --format wheel

FROM base

COPY --from=build "/home/py-power-meter-monitor/src/dist/py_power_meter_monitor-*-py3-none-any.whl" ./
RUN pip install --user $(ls py_*.whl)

ENTRYPOINT ["/home/py-power-meter-monitor/.local/bin/py-power-meter-monitor"]
