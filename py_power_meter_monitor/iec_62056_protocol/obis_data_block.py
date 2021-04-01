from dataclasses import dataclass

from ..config import ObisDataSetConfig
from .data_block import DataBlock
from .obis_data_set import (
    ObisDataSet,
    ObisId,
    ObisStringDataSet,
    UnknownObisDataSet,
    parse_obis_id_from_address,
)


METERING_POINT_ID_OBIS_ID: ObisId = (1, 0, 96, 1, 0, 255)


@dataclass
class ObisDataBlock:
    data_sets: list[ObisDataSet]
    manufacturer_identification: str

    @property
    def device_id(self):
        return next(
            (
                data_set.value
                for data_set in self.data_sets
                if isinstance(data_set, ObisStringDataSet)
                and data_set.id == METERING_POINT_ID_OBIS_ID
            ),
            None,
        )

    @classmethod
    def from_iec_62056_21_data_block(
        cls,
        obis_data_set_configs: dict[ObisId, ObisDataSetConfig],
        data_block: DataBlock,
    ):
        def parse_data_set(data_set):
            data_set_id = parse_obis_id_from_address(data_set.address)
            obis_data_set_config = obis_data_set_configs.get(data_set_id)
            obis_data_set_type = (
                obis_data_set_config.obis_data_set_type
                if obis_data_set_config
                else UnknownObisDataSet
            )

            obis_data_set = obis_data_set_type.from_iec_62056_21_data_set(data_set)

            return obis_data_set

        return cls(
            data_sets=[parse_data_set(data_set) for data_set in data_block.data_lines],
            manufacturer_identification=data_block.manufacturer_identification,
        )
