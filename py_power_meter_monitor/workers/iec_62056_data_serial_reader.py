# pyright: reportUnnecessaryIsInstance=false
import asyncio
from logging import getLogger

from aioserial import AioSerial  # type: ignore
from async_timeout import timeout

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
    ResetSpeedEffect,
    SendMessageEffect,
    get_next_state,
)
from ..iec_62056_protocol.transmission_speeds import mode_c_transmission_speeds
from ..utils.publish_subscribe_topic import PublishSubscribeTopic

logger = getLogger(__package__)


async def read_iec_62056_data_from_serial(
    topic: PublishSubscribeTopic[DataBlock],
    serial_port: AioSerial,
    baud_rate: int,
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
                        await serial_port.write_async(bytes(next_effect.message))
                    await asyncio.sleep(response_delay)
                elif isinstance(next_effect, AwaitMessageEffect):
                    async with timeout(read_timeout):
                        message = await next_effect.message_type.read_from_serial_port(
                            serial_port
                        )
                        next_event = ReceiveMessageEvent(message=message)
                elif isinstance(next_effect, ResetEffect):
                    switch_baud_rate(serial_port=serial_port, baud_rate=baud_rate)
                    next_event = ResetEvent()
                    await asyncio.sleep(polling_delay)
                elif isinstance(next_effect, ResetSpeedEffect):
                    switch_baud_rate(serial_port=serial_port, baud_rate=baud_rate)
                elif isinstance(next_effect, ChangeSpeedEffect):
                    new_speed = mode_c_transmission_speeds.get(next_effect.baud_rate_id)
                    if isinstance(new_speed, int):
                        switch_baud_rate(serial_port=serial_port, baud_rate=new_speed)
        except Iec62056ProtocolError:
            logger.exception(f"Protocol error in state {current_state}")
            next_event = ResetEvent()
            await asyncio.sleep(polling_delay)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            logger.exception(f"Error in state {current_state}")
            next_event = ResetEvent()
            await asyncio.sleep(polling_delay)


def switch_baud_rate(serial_port: AioSerial, baud_rate: int):
    logger.debug(f"Switching serial baud rate to {baud_rate}")
    serial_port.flush()
    serial_port.baudrate = baud_rate
