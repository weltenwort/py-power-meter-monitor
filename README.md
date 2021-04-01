# py-power-meter-monitor

[![license](https://img.shields.io/github/license/weltenwort/py-power-meter-monitor?style=flat-square)](LICENSE)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
![test-status](https://img.shields.io/github/workflow/status/weltenwort/py-power-meter-monitor/Run%20Tests?label=tests&style=flat-square)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/weltenwort/py-power-meter-monitor?sort=semver&style=flat-square)

A bridge between the serial interface (RS485 or infrared) of certain power meters and MQTT with Home Assistant support.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Background

This is intended to be deployed on a device that has a physical serial connection to a power meter manufactured. It has only been tested with the following models:

- [Logarex]: LK13BE803039

Please contribute experiences with this or other models in an [issue].

## Install

The application may be deployed from source or as a container.

### From source

To deploy from source use [poetry] to install or build a wheel.

### As a container

The included `Dockerfile` contains build instructions for an image based on Alpine Linux. The recommended way to build and deploy it is [podman]:

```
$ podman build --rm -t py-power-meter-monitor:latest .
$ podman run \
  --device /dev/ttyUSB0:/dev/ttyUSB0 \
  --volume $(pwd)/default-config.toml:/home/py-power-meter-monitor/config.toml:ro \
  localhost/py-power-meter-monitor:latest --config-file config.toml
```

## Usage

The configuration file allows for parameterization of various aspects:

- the serial connection
- the mqtt connection
- the OBIS data sets to send

## Contributing

I welcome requests, bug reports and PRs.

Small note: If editing the Readme, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

## License

[MIT](LICENSE)


[Logarex]: http://www.logarex.cz/en/homepage
[issue]: https://github.com/weltenwort/py-power-meter-monitor/issues/new
[poetry]: https://python-poetry.org/
[podman]: https://podman.io/
