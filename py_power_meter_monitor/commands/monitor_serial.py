# pyright: reportUnknownMemberType=false
import asyncio
from logging import getLogger

import asyncio_mqtt  # type: ignore
from aioserial import AioSerial  # type: ignore

from ..config import MqttConfig, ObisConfig, SerialPortConfig
from ..iec_62056_protocol.data_block import DataBlock
from ..utils.publish_subscribe_topic import PublishSubscribeTopic
from ..workers.iec_62056_data_serial_reader import read_iec_62056_data_from_serial
from ..workers.iec_62056_obis_data_set_logger import log_iec_62056_obis_data_sets
from ..workers.iec_62056_obis_data_set_mqtt_logger import (
    mqtt_log_iec_62056_obis_data_sets,
)

logger = getLogger(__package__)


async def run_monitor_serial(
    serial_config: SerialPortConfig,
    mqtt_config: MqttConfig,
    obis_config: ObisConfig,
):
    data_blocks: PublishSubscribeTopic[DataBlock] = PublishSubscribeTopic()

    obis_data_set_configs_by_id = {
        obis_data_set_config.id: obis_data_set_config
        for obis_data_set_config in obis_config.data_sets
    }

    serial_port = AioSerial(
        port=serial_config.port_url,
        baudrate=serial_config.baud_rate,
        bytesize=serial_config.byte_size,
        parity=serial_config.parity.value,
        stopbits=serial_config.stop_bits.value,
    )

    logger.debug(
        f"Opened serial connection {serial_config.port_url} with {serial_config.baud_rate} baud."
    )

    with serial_port:
        async with asyncio_mqtt.Client(
            hostname=mqtt_config.broker.hostname,
            port=int(mqtt_config.broker.port) if mqtt_config.broker.port else None,
            username=mqtt_config.broker.username,
            password=mqtt_config.broker.password,
        ) as mqtt_client:
            await asyncio.gather(
                mqtt_log_iec_62056_obis_data_sets(
                    topic=data_blocks,
                    mqtt_client=mqtt_client,
                    mqtt_config=mqtt_config,
                    obis_data_set_configs_by_id=obis_data_set_configs_by_id,
                ),
                read_iec_62056_data_from_serial(
                    baud_rate=serial_config.baud_rate,
                    polling_delay=serial_config.polling_delay,
                    read_timeout=serial_config.read_timeout,
                    response_delay=serial_config.response_delay,
                    serial_port=serial_port,
                    topic=data_blocks,
                    write_timeout=serial_config.write_timeout,
                ),
                log_iec_62056_obis_data_sets(
                    topic=data_blocks,
                    obis_data_set_configs_by_id=obis_data_set_configs_by_id,
                )
                if True
                else async_noop(),
            )


async def async_noop():
    pass
