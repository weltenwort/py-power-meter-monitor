# pyright: reportUnnecessaryIsInstance=false
import asyncio
from asyncio.streams import StreamReader, StreamWriter
from logging import getLogger

from async_timeout import timeout
from serial import Serial  # type: ignore

from ..iec_62056_protocol.data_block import DataBlock
from ..iec_62056_protocol.errors import Iec62056ProtocolError
from ..iec_62056_protocol.mode_c_state_machine import (
    AwaitMessageEffect,
    ChangeSpeedEffect,
    DataReadoutSuccessState,
    InitialState,
    ProtocolErrorState,
    ReceiveMessageEvent,
    ResetEffect,
    ResetEvent,
    SendMessageEffect,
    get_next_state,
)
from ..iec_62056_protocol.transmission_speeds import mode_c_transmission_speeds
from ..utils.publish_subscribe_topic import PublishSubscribeTopic

logger = getLogger(__package__)


async def read_iec_62056_data_from_serial(
    topic: PublishSubscribeTopic[DataBlock],
    serial_stream_reader: StreamReader,
    serial_stream_writer: StreamWriter,
    polling_delay: float,
    response_delay: float,
    read_timeout: float,
    write_timeout: float,
):
    current_state = InitialState()
    next_event = ResetEvent()

    while True:
        (current_state, next_effects) = get_next_state(
            state=current_state, event=next_event
        )

        try:
            # react to state change
            logger.debug(f"IEC 62056 state machine in state {current_state}")

            if isinstance(current_state, DataReadoutSuccessState):
                topic.publish(current_state.data)
            elif isinstance(current_state, ProtocolErrorState):
                raise Iec62056ProtocolError(current_state.message)

            # execute effects
            for next_effect in next_effects:
                logger.debug(f"IEC 62056 state machine evaluating effect {next_effect}")

                if isinstance(next_effect, SendMessageEffect):
                    async with timeout(write_timeout):
                        serial_stream_writer.write(bytes(next_effect.message))
                        await serial_stream_writer.drain()
                elif isinstance(next_effect, AwaitMessageEffect):
                    async with timeout(read_timeout):
                        message = await next_effect.message_type.read_from_stream(
                            serial_stream_reader
                        )
                        next_event = ReceiveMessageEvent(message=message)
                elif isinstance(next_effect, ResetEffect):
                    next_event = ResetEvent()
                    await asyncio.sleep(polling_delay)
                elif isinstance(next_effect, ChangeSpeedEffect):
                    serial = serial_stream_writer.get_extra_info("serial")
                    new_speed = mode_c_transmission_speeds.get(next_effect.baud_rate_id)
                    if isinstance(serial, Serial) and new_speed is not None:
                        logger.debug(f"Switching serial baud rate to {new_speed}")
                        serial.baudrate = new_speed

            await asyncio.sleep(response_delay)
        except Iec62056ProtocolError:
            logger.exception(f"Protocol error in state {current_state}")
            next_event = ResetEvent()
            await asyncio.sleep(polling_delay)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            logger.exception(f"Error in state {current_state}")
            next_event = ResetEvent()
            await asyncio.sleep(polling_delay)
