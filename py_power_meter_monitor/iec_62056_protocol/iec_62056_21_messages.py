import asyncio
import re
from abc import abstractmethod
from asyncio.streams import StreamReader
from dataclasses import dataclass
from logging import getLogger
from time import time
from typing import ClassVar, Optional, Pattern, Type, TypeVar, Union

import async_timeout
from aioserial import AioSerial  # type: ignore

from .block_check_character import get_block_check_character
from .data_block import DataBlock
from .errors import ParsingError

message_encoding = "iso-8859-1"

MessageT = TypeVar("MessageT", bound="BaseMessage")

logger = getLogger(__package__)


@dataclass
class BaseMessage:
    timestamp: float
    initiator: ClassVar[Optional[bytes]] = None
    terminator: ClassVar[bytes] = b"\r\n"
    extra_bytes_after_terminator: ClassVar[int] = 0

    @classmethod
    @abstractmethod
    def from_bytes(cls: Type[MessageT], timestamp: float, frame: bytes) -> MessageT:
        raise NotImplementedError()

    @classmethod
    async def read_from_serial_port(
        cls: Type[MessageT], serial_port: AioSerial
    ) -> MessageT:
        frame = b""
        if cls.initiator is not None:
            # drain the read buffer
            try:
                with async_timeout.timeout(30):
                    logger.debug(f"Draining the read buffer up to {cls.initiator}")
                    await serial_port.read_until_async(cls.initiator)
                    frame += cls.initiator
            except (asyncio.TimeoutError):
                logger.debug("Gave up on draining the read buffer")
        logger.debug(f"Reading up to {cls.terminator}")
        frame += await serial_port.read_until_async(cls.terminator)
        logger.debug(f"Reading {cls.extra_bytes_after_terminator} extra bytes")
        frame += await serial_port.read_async(cls.extra_bytes_after_terminator)
        timestamp = time()
        logger.debug(f"Finished reading at {timestamp}")

        return cls.from_bytes(timestamp=timestamp, frame=frame)

    @classmethod
    async def read_from_stream(cls: Type[MessageT], reader: StreamReader) -> MessageT:
        frame = b""
        if cls.initiator is not None:
            # drain the read buffer
            try:
                with async_timeout.timeout(30):
                    logger.debug(f"Draining the read buffer up to {cls.initiator}")
                    await reader.readuntil(cls.initiator)
                    frame += cls.initiator
            except BaseException:
                logger.debug("Gave up on draining the read buffer")
        logger.debug(f"Reading up to {cls.terminator}")
        frame += await reader.readuntil(cls.terminator)
        logger.debug(f"Reading {cls.extra_bytes_after_terminator} extra bytes")
        frame += await reader.readexactly(cls.extra_bytes_after_terminator)
        timestamp = time()
        logger.debug(f"Finished reading at {timestamp}")

        return cls.from_bytes(timestamp=timestamp, frame=frame)

    @classmethod
    def match_frame_or_raise(
        cls: Type[MessageT], expression: re.Pattern[bytes], frame: bytes
    ) -> re.Match[bytes]:
        matches = expression.match(frame)

        if matches is None:
            raise ParsingError(frame_type=cls, frame=frame)

        return matches


@dataclass
class RequestMessage(BaseMessage):
    device_address: str = ""
    initiator: ClassVar[bytes] = b"/"

    frame_expression: ClassVar[Pattern[bytes]] = re.compile(
        b"\\A/\\?(?P<device_address>[^!]*)!\r\n\\Z", re.DOTALL
    )

    def __bytes__(self) -> bytes:
        return b"/?%s!%s" % (
            self.device_address.encode(message_encoding),
            self.terminator,
        )

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> "RequestMessage":
        matches = cls.match_frame_or_raise(
            cls.frame_expression,
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
    initiator: ClassVar[bytes] = b"/"

    frame_expression: ClassVar[Pattern[bytes]] = re.compile(
        (
            b"\\A"
            b"/(?P<manufacturer_id>\\w{3})"
            b"(?P<baud_rate_id>[0-9A-Z])"
            b"(?P<mode_ids>(?:\\\\[^\\\\/!])*)"
            b"(?P<identification>[^\\/!\r\n]+)"
            b"\r\n\\Z"
        ),
        re.DOTALL,
    )

    def __bytes__(self) -> bytes:
        return b"%s%s%s%s%s%s" % (
            self.initiator,
            self.manufacturer_id.encode(message_encoding)[:3],
            self.baud_rate_id.encode(message_encoding)[:1],
            self.mode_ids.encode(message_encoding),
            self.identification.encode(message_encoding),
            self.terminator,
        )

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> "IdentificationMessage":
        matches = cls.match_frame_or_raise(
            cls.frame_expression,
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
    initiator: ClassVar[bytes] = b"\x06"

    frame_expression: ClassVar[Pattern[bytes]] = re.compile(
        (
            b"\\A"
            b"\x06(?P<protocol_control>\\d)"
            b"(?P<baud_rate_id>[0-9A-Z])"
            b"(?P<mode_control>[0-9A-Z])"
            b"\r\n\\Z"
        ),
        re.DOTALL,
    )

    def __bytes__(self) -> bytes:
        return b"%s%s%s%s%s" % (
            self.initiator,
            self.protocol_control.encode(message_encoding)[:1],
            self.baud_rate_id.encode(message_encoding)[:1],
            self.mode_control.encode(message_encoding)[:1],
            self.terminator,
        )

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> "AcknowledgementMessage":
        matches = cls.match_frame_or_raise(
            cls.frame_expression,
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
    initiator: ClassVar[bytes] = b"\x02"

    frame_expression: ClassVar[Pattern[bytes]] = re.compile(
        b"\\A\x02(?P<data>[^!]*)!\r\n\x03(?P<block_check>.)\\Z", re.DOTALL
    )

    def __bytes__(self) -> bytes:
        encoded_data = b"%s%s" % (bytes(self.data), self.terminator)
        block_check_character = get_block_check_character(encoded_data)
        return b"\x02%s%s" % (encoded_data, block_check_character)

    @classmethod
    def from_bytes(cls, timestamp: float, frame: bytes) -> "DataMessage":
        matches = cls.match_frame_or_raise(
            cls.frame_expression,
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
