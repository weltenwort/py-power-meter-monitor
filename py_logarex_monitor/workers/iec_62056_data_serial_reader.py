import asyncio
from asyncio.streams import StreamReader, StreamWriter
from logging import getLogger


from async_timeout import timeout


from ..iec_62056_protocol.data_block import DataBlock
from ..iec_62056_protocol.errors import Iec62056ProtocolError
from ..iec_62056_protocol.mode_c_state_machine import (
    AwaitMessageEffect,
    DataReadoutSuccessState,
    InitialState,
    ProtocolErrorState,
    ReceiveMessageEvent,
    ResetEffect,
    SendMessageEffect,
    ResetEvent,
    get_next_state,
)
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

            await asyncio.sleep(response_delay)
        except Iec62056ProtocolError:
            logger.exception(f"Protocol error in state {current_state}")
            next_event = ResetEvent()
            await asyncio.sleep(polling_delay)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            logger.exception(f"Error in state {current_state}")
            next_event = ResetEvent()
            await asyncio.sleep(polling_delay)
