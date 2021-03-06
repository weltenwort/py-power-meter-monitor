from abc import abstractmethod
from asyncio.streams import StreamReader
from dataclasses import dataclass
from time import time
from py_logarex_monitor.iec_62056_protocol.errors import ParsingError
import re
from typing import ClassVar, Optional, Type, TypeVar, Union

from .block_check_character import get_block_check_character
from .data_block import DataBlock


MessageT = TypeVar("MessageT", bound="BaseMessage")


@dataclass
class BaseMessage:
    timestamp: float
    terminator: ClassVar[bytes] = b"\r\n"
    extra_bytes_after_terminator: ClassVar[int] = 0

    @classmethod
    @abstractmethod
    def from_bytes(cls: Type[MessageT], timestamp: float, frame: bytes) -> MessageT:
        raise NotImplementedError()

    @classmethod
    async def read_from_stream(cls: Type[MessageT], reader: StreamReader) -> MessageT:
        frame = await reader.readuntil(cls.terminator)
        frame += await reader.readexactly(cls.extra_bytes_after_terminator)
        timestamp = time()

        return cls.from_bytes(timestamp=timestamp, frame=frame)

    @classmethod
    def match_frame_or_raise(
        cls: Type[MessageT], expression: bytes, frame: bytes
    ) -> re.Match[bytes]:
        matches = re.match(expression, frame)

        if matches is None:
            raise ParsingError(frame_type=cls, frame=frame)

        return matches


@dataclass
class RequestMessage(BaseMessage):
    device_address: str = ""

    def __bytes__(self) -> bytes:
        return b"/?%s!%s" % (self.device_address.encode("utf-8"), self.terminator)

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> Optional["RequestMessage"]:
        matches = cls.match_frame_or_raise(
            b"^/\\?(?P<device_address>[^!]*)!\r\n$",
            frame,
        )

        if matches is None:
            return None

        return cls(
            timestamp=timestamp,
            device_address=(matches.group("device_address") or b"").decode("utf-8"),
        )


@dataclass
class IdentificationMessage(BaseMessage):
    manufacturer_id: str
    baud_rate_id: str
    identification: str

    def __bytes__(self) -> bytes:
        return b"/%s%s%s%s" % (
            self.manufacturer_id.encode("utf-8")[:3],
            self.baud_rate_id.encode("utf-8")[:1],
            self.identification.encode("utf-8"),
            self.terminator,
        )

    @classmethod
    def from_bytes(
        cls, timestamp: float, frame: bytes
    ) -> Optional["IdentificationMessage"]:
        matches = cls.match_frame_or_raise(
            b"^/(?P<manufacturer_id>\\w{3})(?P<baud_rate_id>[0-9A-Z])(?P<identification>[^\r\n]+)\r\n$",
            frame,
        )

        if matches is None:
            return None

        return cls(
            timestamp=timestamp,
            manufacturer_id=matches.group("manufacturer_id").decode("utf-8"),
            baud_rate_id=matches.group("baud_rate_id").decode("utf-8"),
            identification=matches.group("identification").decode("utf-8"),
        )


@dataclass
class AcknowledgementMessage(BaseMessage):
    protocol_control: str
    baud_rate_id: str
    mode_control: str

    def __bytes__(self) -> bytes:
        return b"\x06%s%s%s%s" % (
            self.protocol_control.encode("utf-8")[:1],
            self.baud_rate_id.encode("utf-8")[:1],
            self.mode_control.encode("utf-8")[:1],
            self.terminator,
        )

    @classmethod
    def from_bytes(
        cls, timestamp: float, frame: bytes
    ) -> Optional["AcknowledgementMessage"]:
        matches = cls.match_frame_or_raise(
            b"^\x06(?P<protocol_control>\\d)(?P<baud_rate_id>[0-9A-Z])(?P<mode_control>[0-9A-Z])\r\n$",
            frame,
        )

        if matches is None:
            return None

        return cls(
            timestamp=timestamp,
            protocol_control=(matches.group("protocol_control") or b"").decode("utf-8"),
            baud_rate_id=(matches.group("baud_rate_id") or b"").decode("utf-8"),
            mode_control=(matches.group("mode_control") or b"").decode("utf-8"),
        )


@dataclass
class DataMessage(BaseMessage):
    data: DataBlock
    terminator: ClassVar[bytes] = b"!\r\n\x03"
    extra_bytes_after_terminator: ClassVar[int] = 1

    def __bytes__(self) -> bytes:
        encoded_data = b"%s%s" % (bytes(self.data), self.terminator)
        block_check_character = get_block_check_character(encoded_data)
        return b"\x02%s%s" % (encoded_data, block_check_character)

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> Optional["DataMessage"]:
        matches = cls.match_frame_or_raise(
            b"^\x02(?P<data>[^!]*)!\r\n\x03(?P<block_check>.)$",
            frame,
        )

        if matches is None:
            return None

        block_check_character = get_block_check_character(
            b"%s!\r\n\x03" % matches.group("data")
        )

        if block_check_character != matches.group("block_check"):
            return None

        return cls(
            timestamp=timestamp,
            data=DataBlock.from_bytes(timestamp=timestamp, data=matches.group("data")),
        )


Iec6205621Message = Union[
    RequestMessage, IdentificationMessage, AcknowledgementMessage, DataMessage
]
