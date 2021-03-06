from dataclasses import dataclass
import re
from typing import Optional, Tuple, Union

from .data_block import DataSet


ObisId = Tuple[int, int, int, int, int, int]


@dataclass
class BaseObisDataSet:
    timestamp: float
    id: ObisId
    unit: Optional[str]


@dataclass
class ObisIntegerDataSet(BaseObisDataSet):
    value: int

    @classmethod
    def from_iec_62056_21_data_set(cls, data_set: DataSet):
        return cls(
            timestamp=data_set.timestamp,
            id=parse_obis_id_from_address(data_set.address),
            value=int(data_set.value or "0", 10),
            unit=data_set.unit,
        )


@dataclass
class ObisFloatDataSet(BaseObisDataSet):
    value: float

    @classmethod
    def from_iec_62056_21_data_set(cls, data_set: DataSet):
        return cls(
            timestamp=data_set.timestamp,
            id=parse_obis_id_from_address(data_set.address),
            value=float(data_set.value or "0.0"),
            unit=data_set.unit,
        )


@dataclass
class ObisStringDataSet(BaseObisDataSet):
    value: str

    @classmethod
    def from_iec_62056_21_data_set(cls, data_set: DataSet):
        return cls(
            timestamp=data_set.timestamp,
            id=parse_obis_id_from_address(data_set.address),
            value=data_set.value or "",
            unit=None,
        )


ObisDataSet = Union[ObisIntegerDataSet, ObisFloatDataSet, ObisStringDataSet]


obis_id_expression = re.compile(r"^(\d+)-(\d+):(\d+)\.(\d+)\.(\d+)\*(\d+)$")


def parse_obis_id_from_address(address: str) -> ObisId:
    matches = obis_id_expression.match(address)

    if matches is None:
        raise ValueError(f"Failed to parse {address} as an OBIS id.")

    return tuple(int(group, 10) for group in matches.groups())
