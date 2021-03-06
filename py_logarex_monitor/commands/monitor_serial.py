import asyncio

import asyncio_mqtt
import serial_asyncio

from ..config import MqttConfig, ObisConfig, SerialPortConfig
from ..iec_62056_protocol.data_block import DataBlock
from ..utils.async_closing import async_closing
from ..utils.publish_subscribe_topic import PublishSubscribeTopic
from ..workers.iec_62056_data_serial_reader import read_iec_62056_data_from_serial
from ..workers.iec_62056_obis_data_set_logger import log_iec_62056_obis_data_sets


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

    serial_reader, serial_writer = await serial_asyncio.open_serial_connection(
        url=serial_config.port_url,
        baudrate=serial_config.baud_rate,
        bytesize=serial_config.byte_size,
        parity=serial_config.parity.value,
        stopbits=serial_config.stop_bits.value,
    )

    async with async_closing(serial_writer):
        async with asyncio_mqtt.Client(
            hostname=mqtt_config.broker.hostname,
            port=int(mqtt_config.broker.port) if mqtt_config.broker.port else None,
            username=mqtt_config.broker.username,
            password=mqtt_config.broker.password,
        ) as mqtt_client:
            await asyncio.gather(
                read_iec_62056_data_from_serial(
                    topic=data_blocks,
                    serial_stream_reader=serial_reader,
                    serial_stream_writer=serial_writer,
                    polling_delay=serial_config.polling_delay,
                    response_delay=serial_config.response_delay,
                    read_timeout=serial_config.read_timeout,
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
