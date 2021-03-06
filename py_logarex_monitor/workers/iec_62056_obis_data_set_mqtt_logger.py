import json
from logging import getLogger
from typing import Dict

import asyncio_mqtt

from ..config import MqttConfig, ObisDataSetConfig
from ..iec_62056_protocol.data_block import DataBlock
from ..iec_62056_protocol.obis_data_set import (
    ObisDataSet,
    ObisId,
    parse_obis_id_from_address,
)
from ..utils.publish_subscribe_topic import PublishSubscribeTopic


logger = getLogger(__package__)


async def mqtt_log_iec_62056_obis_data_sets(
    topic: PublishSubscribeTopic[DataBlock],
    mqtt_client: asyncio_mqtt.Client,
    mqtt_config: MqttConfig,
    obis_data_set_configs_by_id: Dict[ObisId, ObisDataSetConfig],
):
    configured_ids: set[ObisId] = set()

    async for frame in topic.items():
        for data_set in frame.data_lines:
            data_set_id = parse_obis_id_from_address(data_set.address)
            obis_data_set_config = obis_data_set_configs_by_id.get(data_set_id)

            if obis_data_set_config is None:
                logger.error(f"Failed to get obis data set config for id {data_set_id}")
                continue

            obis_data_set = (
                obis_data_set_config.obis_data_set_type.from_iec_62056_21_data_set(
                    data_set
                )
            )

            if data_set_id not in configured_ids:
                configuration_topic = get_configuration_topic(
                    mqtt_config, obis_data_set_config
                )
                configuration_payload = get_configuration_payload(
                    mqtt_config, obis_data_set_config, obis_data_set
                )
                await mqtt_client.publish(
                    topic=configuration_topic,
                    payload=configuration_payload,
                    retain=True,
                )
                configured_ids.add(data_set_id)

            state_topic = get_state_topic(mqtt_config, obis_data_set_config)
            state_payload = get_state_payload(obis_data_set)

            await mqtt_client.publish(
                topic=state_topic, payload=state_payload, retain=True
            )


def get_configuration_payload(
    mqtt_config: MqttConfig,
    obis_data_set_config: ObisDataSetConfig,
    obis_data_set: ObisDataSet,
):
    sensor_name = get_sensor_name(mqtt_config, obis_data_set_config)
    state_topic = get_state_topic(mqtt_config, obis_data_set_config)

    return json.dumps(
        {
            **{
                "name": sensor_name,
                "state_topic": state_topic,
                "value_template": "{{ value_json.value }}",
                "device": {
                    "identifiers": [mqtt_config.device.id],
                    "manufacturer": mqtt_config.device.manufacturer,
                    "model": mqtt_config.device.model,
                    "name": mqtt_config.device.name,
                },
                "unique_id": sensor_name,
            },
            **get_device_class(obis_data_set),
        }
    )


def get_state_payload(obis_data_set: ObisDataSet):
    return json.dumps(
        {"timestamp": obis_data_set.timestamp, "value": obis_data_set.value}
    )


def get_configuration_topic(
    mqtt_config: MqttConfig, obis_data_set_config: ObisDataSetConfig
):
    return mqtt_config.configuration_topic_template.format(
        device_id=get_sensor_name(mqtt_config, obis_data_set_config)
    )


def get_state_topic(mqtt_config: MqttConfig, obis_data_set_config: ObisDataSetConfig):
    return mqtt_config.state_topic_template.format(
        device_id=get_sensor_name(mqtt_config, obis_data_set_config)
    )


def get_sensor_name(mqtt_config: MqttConfig, obis_data_set_config: ObisDataSetConfig):
    return f"{mqtt_config.device.name} {obis_data_set_config.name}"


def get_device_class(obis_data_set: ObisDataSet):
    if obis_data_set.unit is None:
        return {}

    device_class = device_class_by_unit.get(obis_data_set.unit, None)

    return {
        "unit_of_measurement": obis_data_set.unit,
        **(
            {
                "device_class": device_class,
            }
            if device_class
            else {}
        ),
    }


device_class_by_unit = {
    "°C": "temperature",
    "W": "power",
    "kW": "power",
    "Wh": "energy",
    "kWh": "energy",
    "A": "current",
    "V": "voltage",
}
