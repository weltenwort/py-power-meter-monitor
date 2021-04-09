from typing import Any, Type


class Iec62056ProtocolError(Exception):
    pass


class ParsingError(Iec62056ProtocolError):
    def __init__(self, frame_type: Type[Any], frame: bytes):
        super().__init__(frame_type, frame)

        self.frame_type = frame_type
        self.frame = frame
