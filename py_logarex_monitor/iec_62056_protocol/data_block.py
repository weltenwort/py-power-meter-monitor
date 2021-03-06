from dataclasses import dataclass
import re
from typing import Optional


@dataclass
class DataSet:
    timestamp: float
    address: str
    value: Optional[str]
    unit: Optional[str]

    def __bytes__(self) -> bytes:
        return b"%s(%s%s)" % (
            self.address.encode("utf-8"),
            self.value.encode("utf-8") if self.value else b"",
            b"*%s" % (self.unit.encode("utf-8")) if self.unit else b"",
        )

    @classmethod
    def from_bytes(cls, timestamp: float, line: bytes) -> "DataSet":
        matches = re.match(
            b"^(?P<address>[^(]+)\\((?P<value>[^()*/!]{0,32})?(?:\\*(?P<unit>[^()/!]{0,16}))?\\)$",
            line,
        )

        if matches is None:
            raise ValueError(
                f"Failed to parse line into DataSet: {line.decode('utf-8')}"
            )

        match_value = matches.group("value")
        match_unit = matches.group("unit")

        return cls(
            timestamp=timestamp,
            address=matches.group("address").decode("utf-8"),
            value=match_value.decode("utf-8") if match_value is not None else None,
            unit=match_unit.decode("utf-8") if match_unit is not None else None,
        )


@dataclass
class DataBlock:
    data_lines: list[DataSet]

    def __bytes__(self) -> bytes:
        return b"".join(b"%s\r\n" % bytes(line) for line in self.data_lines)

    @classmethod
    def from_bytes(cls, timestamp: float, data: bytes) -> "DataBlock":
        return cls(
            data_lines=[
                DataSet.from_bytes(timestamp, line)
                for line in data.split(b"\r\n")
                if len(line) > 0
            ]
        )
