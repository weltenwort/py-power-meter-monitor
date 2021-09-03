# pyright: reportUnknownMemberType=false
import json
from logging import getLogger
import re
from typing import Dict

import asyncio_mqtt  # type: ignore

from ..config import MqttConfig, ObisDataSetConfig
from ..iec_62056_protocol.data_block import DataBlock
from ..iec_62056_protocol.obis_data_block import ObisDataBlock
from ..iec_62056_protocol.obis_data_set import (
    ObisDataSet,
    ObisId,
    UnknownObisDataSet,
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
        obis_data_block = ObisDataBlock.from_iec_62056_21_data_block(
            obis_data_set_configs=obis_data_set_configs_by_id, data_block=frame
        )

        for obis_data_set in obis_data_block.data_sets:
            obis_data_set_config = obis_data_set_configs_by_id.get(obis_data_set.id)

            if (
                isinstance(obis_data_set, UnknownObisDataSet)
                or obis_data_set_config is None
            ):
                logger.error(f"Unknown obis data set config for id {obis_data_set.id}")
                continue

            # configure entity upon first sighting
            if obis_data_set.id not in configured_ids:
                configuration_topic = get_configuration_topic(
                    mqtt_config, obis_data_set_config
                )
                configuration_payload = get_configuration_payload(
                    mqtt_config=mqtt_config,
                    obis_data_set_config=obis_data_set_config,
                    obis_data_block=obis_data_block,
                    obis_data_set=obis_data_set,
                )
                await mqtt_client.publish(
                    topic=configuration_topic,
                    payload=configuration_payload,
                    retain=True,
                )
                configured_ids.add(obis_data_set.id)

            # publish state
            state_topic = get_state_topic(mqtt_config, obis_data_set_config)
            state_payload = get_state_payload(obis_data_set)

            await mqtt_client.publish(
                topic=state_topic, payload=state_payload, retain=True
            )


def get_configuration_payload(
    mqtt_config: MqttConfig,
    obis_data_set_config: ObisDataSetConfig,
    obis_data_block: ObisDataBlock,
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
                    "identifiers": [obis_data_block.device_id],
                    "manufacturer": mqtt_config.device.manufacturer,
                    "model": (
                        obis_data_block.manufacturer_identification
                        or mqtt_config.device.model
                    ),
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
        entity_id=slugify_sensor_name(
            get_sensor_name(mqtt_config, obis_data_set_config)
        )
    )


def get_state_topic(mqtt_config: MqttConfig, obis_data_set_config: ObisDataSetConfig):
    return mqtt_config.state_topic_template.format(
        entity_id=slugify_sensor_name(
            get_sensor_name(mqtt_config, obis_data_set_config)
        )
    )


def get_sensor_name(mqtt_config: MqttConfig, obis_data_set_config: ObisDataSetConfig):
    return f"{mqtt_config.device.name} {obis_data_set_config.name}"


slug_replacement_expressions = re.compile(r"\W")


def slugify_sensor_name(sensor_name: str):
    return slug_replacement_expressions.sub("-", sensor_name)


def get_device_class(obis_data_set: ObisDataSet) -> dict[str, str]:
    if obis_data_set.unit is None:
        return {}

    device_class = device_class_by_unit.get(obis_data_set.unit, None)
    state_class = state_class_by_unit.get(obis_data_set.unit, None)

    return {
        "unit_of_measurement": obis_data_set.unit,
        **(
            {
                "device_class": device_class,
            }
            if device_class
            else {}
        ),
        **(
            {
                "state_class": state_class,
            }
            if state_class
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

state_class_by_unit = {
    "°C": "measurement",
    "W": "measurement",
    "kW": "measurement",
    "Wh": "total_increasing",
    "kWh": "total_increasing",
    "A": "measurement",
    "V": "measurement",
}
