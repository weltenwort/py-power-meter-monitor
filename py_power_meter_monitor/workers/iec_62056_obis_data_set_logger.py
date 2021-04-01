from logging import getLogger
from typing import Dict

from ..config import ObisDataSetConfig
from ..iec_62056_protocol.data_block import DataBlock
from ..iec_62056_protocol.obis_data_set import ObisId, parse_obis_id_from_address
from ..utils.publish_subscribe_topic import PublishSubscribeTopic


async def log_iec_62056_obis_data_sets(
    topic: PublishSubscribeTopic[DataBlock],
    obis_data_set_configs_by_id: Dict[ObisId, ObisDataSetConfig],
):
    logger = getLogger(__package__)

    async for data_block in topic.items():
        for data_set in data_block.data_lines:
            obis_data_set_config = obis_data_set_configs_by_id.get(
                parse_obis_id_from_address(data_set.address)
            )

            if obis_data_set_config is None:
                logger.debug(f"Unknown data set: {data_set}")
                continue

            obis_data_set = (
                obis_data_set_config.obis_data_set_type.from_iec_62056_21_data_set(
                    data_set
                )
            )

            logger.debug(
                f"Known data set '{obis_data_set_config.name}' {obis_data_set_config.id}: "
                f"{obis_data_set.value} {getattr(obis_data_set, 'unit', '')}"
            )
