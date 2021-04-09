# pyright: reportUnnecessaryIsInstance=false
from dataclasses import dataclass
from typing import Tuple, Type, Union

from .data_block import DataBlock
from .iec_62056_21_messages import (
    AcknowledgementMessage,
    DataMessage,
    IdentificationMessage,
    Iec6205621Message,
    RequestMessage,
)


@dataclass
class InitialState:
    pass


@dataclass
class IdentifiedState:
    manufacturer_id: str
    baud_rate_id: str
    identification: str


@dataclass
class DataReadoutSuccessState:
    data: DataBlock


@dataclass
class ProtocolErrorState:
    message: str


ModeCState = Union[
    InitialState, IdentifiedState, DataReadoutSuccessState, ProtocolErrorState
]


@dataclass
class ResetEvent:
    pass


@dataclass
class ReceiveMessageEvent:
    message: Iec6205621Message


ModeCEvent = Union[ResetEvent, ReceiveMessageEvent]


@dataclass
class SendMessageEffect:
    message: Iec6205621Message


@dataclass
class AwaitMessageEffect:
    message_type: Type[Iec6205621Message]


@dataclass
class ResetEffect:
    pass


@dataclass
class ResetSpeedEffect:
    pass


@dataclass
class ChangeSpeedEffect:
    baud_rate_id: str


ModeCEffect = Union[
    SendMessageEffect,
    AwaitMessageEffect,
    ResetEffect,
    ResetSpeedEffect,
    ChangeSpeedEffect,
]


def get_next_state(
    state: ModeCState, event: ModeCEvent
) -> Tuple[ModeCState, list[ModeCEffect]]:
    if isinstance(event, ResetEvent):
        return (
            InitialState(),
            [
                SendMessageEffect(message=RequestMessage(0)),
                AwaitMessageEffect(message_type=IdentificationMessage),
            ],
        )
    elif isinstance(state, InitialState):
        if isinstance(event.message, IdentificationMessage):
            return (
                IdentifiedState(
                    manufacturer_id=event.message.manufacturer_id,
                    baud_rate_id=event.message.baud_rate_id,
                    identification=event.message.identification,
                ),
                [
                    SendMessageEffect(
                        message=AcknowledgementMessage(
                            timestamp=0,
                            protocol_control="0",
                            baud_rate_id=event.message.baud_rate_id,
                            mode_control="0",
                        )
                    ),
                    ChangeSpeedEffect(baud_rate_id=event.message.baud_rate_id),
                    AwaitMessageEffect(message_type=DataMessage),
                ],
            )
        else:
            return (
                ProtocolErrorState(
                    message=f"Expected identification message, but received {event.message}"
                ),
                [ResetEffect()],
            )
    elif isinstance(state, IdentifiedState):
        if isinstance(event.message, DataMessage):
            return (
                DataReadoutSuccessState(
                    data=event.message.data.with_manufacturer_identification(
                        state.identification
                    )
                ),
                [ResetEffect()],
            )
        else:
            return (
                ProtocolErrorState(
                    message=f"Expected data message, but received {event.message}"
                ),
                [ResetEffect()],
            )
    else:
        return (
            ProtocolErrorState(message=f"Invalid state and event: {state}, {event}"),
            [ResetEffect()],
        )
