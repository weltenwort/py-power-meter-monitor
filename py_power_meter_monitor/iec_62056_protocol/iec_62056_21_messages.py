import re
from abc import abstractmethod
from asyncio.streams import StreamReader
from dataclasses import dataclass
from time import time
from typing import ClassVar, Type, TypeVar, Union

from .block_check_character import get_block_check_character
from .data_block import DataBlock
from .errors import ParsingError

message_encoding = "iso-8859-1"

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
        return b"/?%s!%s" % (
            self.device_address.encode(message_encoding),
            self.terminator,
        )

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> "RequestMessage":
        matches = cls.match_frame_or_raise(
            b"^/\\?(?P<device_address>[^!]*)!\r\n$",
            frame,
        )

        return cls(
            timestamp=timestamp,
            device_address=(matches.group("device_address") or b"").decode(
                message_encoding
            ),
        )


@dataclass
class IdentificationMessage(BaseMessage):
    manufacturer_id: str
    baud_rate_id: str
    mode_ids: str
    identification: str

    def __bytes__(self) -> bytes:
        return b"/%s%s%s%s" % (
            self.manufacturer_id.encode(message_encoding)[:3],
            self.baud_rate_id.encode(message_encoding)[:1],
            self.mode_ids.encode(message_encoding),
            self.identification.encode(message_encoding),
            self.terminator,
        )

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> "IdentificationMessage":
        matches = cls.match_frame_or_raise(
            b"^/(?P<manufacturer_id>\\w{3})(?P<baud_rate_id>[0-9A-Z])(?P<mode_ids>(?:\\\\[^\\\\/!])*)(?P<identification>[^\\/!\r\n]+)\r\n$",
            frame,
        )

        return cls(
            timestamp=timestamp,
            manufacturer_id=matches.group("manufacturer_id").decode(message_encoding),
            baud_rate_id=matches.group("baud_rate_id").decode(message_encoding),
            mode_ids=matches.group("mode_ids").decode(message_encoding),
            identification=matches.group("identification").decode(message_encoding),
        )


@dataclass
class AcknowledgementMessage(BaseMessage):
    protocol_control: str
    baud_rate_id: str
    mode_control: str

    def __bytes__(self) -> bytes:
        return b"\x06%s%s%s%s" % (
            self.protocol_control.encode(message_encoding)[:1],
            self.baud_rate_id.encode(message_encoding)[:1],
            self.mode_control.encode(message_encoding)[:1],
            self.terminator,
        )

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> "AcknowledgementMessage":
        matches = cls.match_frame_or_raise(
            b"^\x06(?P<protocol_control>\\d)(?P<baud_rate_id>[0-9A-Z])(?P<mode_control>[0-9A-Z])\r\n$",
            frame,
        )

        return cls(
            timestamp=timestamp,
            protocol_control=(matches.group("protocol_control") or b"").decode(
                message_encoding
            ),
            baud_rate_id=(matches.group("baud_rate_id") or b"").decode(
                message_encoding
            ),
            mode_control=(matches.group("mode_control") or b"").decode(
                message_encoding
            ),
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
    def from_bytes(cls, timestamp: float, frame: bytes) -> "DataMessage":
        matches = cls.match_frame_or_raise(
            b"^\x02(?P<data>[^!]*)!\r\n\x03(?P<block_check>.)$",
            frame,
        )

        block_check_character = get_block_check_character(
            b"%s!\r\n\x03" % matches.group("data")
        )

        if block_check_character != matches.group("block_check"):
            raise ParsingError(frame_type=cls, frame=frame)

        return cls(
            timestamp=timestamp,
            data=DataBlock.from_bytes(timestamp=timestamp, data=matches.group("data")),
        )


Iec6205621Message = Union[
    RequestMessage, IdentificationMessage, AcknowledgementMessage, DataMessage
]
