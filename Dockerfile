FROM python:3.9.2-alpine
ARG py_logarex_monitor_version

RUN adduser --disabled-password py-logarex-monitor
USER py-logarex-monitor
WORKDIR /home/py-logarex-monitor

COPY "dist/py_logarex_monitor-${py_logarex_monitor_version}-py3-none-any.whl" "py_logarex_monitor-${py_logarex_monitor_version}-py3-none-any.whl"
RUN pip install --user "py_logarex_monitor-${py_logarex_monitor_version}-py3-none-any.whl"

ENTRYPOINT ["/home/py-logarex-monitor/.local/bin/py-logarex-monitor"]
