from dataclasses import dataclass, replace
import re
from typing import Optional

data_set_encoding = "iso-8859-1"

data_set_expression = re.compile(
    rb"""^
            (?P<address>[^(]+)
            \(
                (?P<value>[^()*/!]{1,32})?
                (?:\*(?P<unit>[^()/!]{1,16}))?
            \)
            (?:
                \(
                    (?:[^()*/!]{1,32})?
                    (?:\*[^()/!]{1,16})?
                \)
            )*
            $""",
    re.X,
)


@dataclass
class DataSet:
    timestamp: float
    address: str
    value: Optional[str]
    unit: Optional[str]

    def __bytes__(self) -> bytes:
        return b"%s(%s%s)" % (
            self.address.encode(data_set_encoding),
            self.value.encode(data_set_encoding) if self.value else b"",
            b"*%s" % (self.unit.encode(data_set_encoding)) if self.unit else b"",
        )

    @classmethod
    def from_bytes(cls, timestamp: float, line: bytes) -> "DataSet":
        matches = data_set_expression.match(line)

        if matches is None:
            raise ValueError(
                f"Failed to parse line into DataSet: {line.decode(data_set_encoding)}"
            )

        match_value = matches.group("value")
        match_unit = matches.group("unit")

        return cls(
            timestamp=timestamp,
            address=matches.group("address").decode(data_set_encoding),
            value=match_value.decode(data_set_encoding)
            if match_value is not None
            else None,
            unit=match_unit.decode(data_set_encoding)
            if match_unit is not None
            else None,
        )


@dataclass
class DataBlock:
    manufacturer_identification: str
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
            ],
            manufacturer_identification="",
        )

    def with_manufacturer_identification(self, manufacturer_identification: str):
        return replace(self, manufacturer_identification=manufacturer_identification)
