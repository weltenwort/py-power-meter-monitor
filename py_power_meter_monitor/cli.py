import asyncio
from logging import basicConfig
from pathlib import Path
from typing import Optional

import typer

from .commands.monitor_serial import run_monitor_serial
from .config import load_configuration_from_file_path, load_default_configuration

app = typer.Typer()


@app.command()
def run(
    config_file: Optional[Path] = typer.Option(
        None,
        dir_okay=False,
        exists=True,
    ),
):

    configuration = (
        load_configuration_from_file_path(config_file)
        if config_file
        else load_default_configuration()
    )

    basicConfig(level=configuration.logging.level.value)

    asyncio.run(
        run_monitor_serial(
            serial_config=configuration.serial_port,
            mqtt_config=configuration.mqtt,
            obis_config=configuration.obis,
        )
    )
