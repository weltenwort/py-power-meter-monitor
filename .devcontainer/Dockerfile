FROM localhost/archlinux-base:latest

ARG PYTHON_VERSION=3.9.4
ARG POETRY_VERSION=1.1.5

RUN source ~/.asdf/asdf.sh && \
  echo "python ${PYTHON_VERSION}" >> ~/.tool-versions && \
  echo "poetry ${POETRY_VERSION}" >> ~/.tool-versions && \
  pwd && cat ~/.tool-versions && \
  asdf plugin add python && asdf install python && \
  asdf plugin add poetry && asdf install poetry
