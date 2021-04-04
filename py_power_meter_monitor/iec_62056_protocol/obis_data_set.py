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


@dataclass
class UnknownObisDataSet(BaseObisDataSet):
    value: None = None

    @classmethod
    def from_iec_62056_21_data_set(cls, data_set: DataSet):
        return cls(
            timestamp=data_set.timestamp,
            id=parse_obis_id_from_address(data_set.address),
            unit=data_set.unit,
        )


ObisDataSet = Union[
    ObisIntegerDataSet, ObisFloatDataSet, ObisStringDataSet, UnknownObisDataSet
]


obis_id_expression = re.compile(
    r"""^
    (?:
        (?P<A>\d+)
        -
        (?P<B>\d+)
        :
    )?
    (?P<C>\d+|[CFLP])
    \.
    (?P<D>\d+|[CFLP])
    (?:
        \.
        (?P<E>\d+)
        (?:
            [*&.]
            (?P<F>\d+)
        )?
    )?
    $""",
    re.X,
)


obis_id_groups = ("A", "B", "C", "D", "E", "F")


def parse_obis_id_from_address(address: str) -> ObisId:
    matches = obis_id_expression.match(address)

    if matches is None:
        raise ValueError(f"Failed to parse {address} as an OBIS id.")

    return (
        parse_id_code(matches.group("A")),
        parse_id_code(matches.group("B")),
        parse_id_code(matches.group("C")),
        parse_id_code(matches.group("D")),
        parse_id_code(matches.group("E")),
        parse_id_code(matches.group("F")),
    )


def parse_id_code(code: Optional[str]) -> int:
    if code is None:
        return 0
    if code == "C":
        return 96
    elif code == "F":
        return 97
    elif code == "L":
        return 98
    elif code == "P":
        return 99

    return int(code, 10)
