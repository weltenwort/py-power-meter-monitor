import asyncio

import asyncio_mqtt
import serial_asyncio

from ..config import MqttConfig, SerialPortConfig
from ..iec_62056_protocol.data_block import DataBlock
from ..utils.async_closing import async_closing
from ..utils.publish_subscribe_topic import PublishSubscribeTopic
from ..workers.iec_62056_data_serial_reader import read_iec_62056_data_from_serial


async def run_monitor_serial(
    serial_config: SerialPortConfig,
    mqtt_config: MqttConfig,
    # default_register_configuration: DefaultRegisterConfiguration,
    # register_configurations: List[RegisterConfiguration] = [],
    # register_definitions: List[RegisterDefinition] = [],
):
    data_blocks: PublishSubscribeTopic[DataBlock] = PublishSubscribeTopic()

    # register_configurations_by_index = {
    #     register_configuration.elster_index: register_configuration
    #     for register_configuration in register_configurations
    # }

    # polling_configurations = [
    #     create_register_polling_configuration(
    #         register_definition=register_definition,
    #         register_configuration=register_configurations_by_index.get(
    #             register_definition.elster_index
    #         ),
    #         default_register_configuration=default_register_configuration,
    #     )
    #     for register_definition in register_definitions
    # ]

    # TODO: set other connection params
    serial_reader, serial_writer = await serial_asyncio.open_serial_connection(
        url=serial_config.port_url
    )

    async with async_closing(serial_writer):
        async with asyncio_mqtt.Client(
            hostname=mqtt_config.broker.hostname,
            port=int(mqtt_config.broker.port) if mqtt_config.broker.port else None,
            username=mqtt_config.broker.username,
            password=mqtt_config.broker.password,
        ) as mqtt_client:
            await asyncio.gather(
                read_iec_62056_data_from_serial(
                    topic=data_blocks,
                    serial_stream_reader=serial_reader,
                    serial_stream_writer=serial_writer,
                    polling_interval=serial_config.polling_interval,
                )
                # log_elster_frames(topic=elster_frames) if log_frames else async_noop(),
                # log_elster_registers(
                #     topic=elster_frames, register_definitions=register_definitions
                # )
                # if log_registers
                # else async_noop(),
                # mqtt_log_elster_registers(
                #     elster_frames=elster_frames,
                #     mqtt_client=mqtt_client,
                #     mqtt_config=mqtt_config,
                #     register_definitions=register_definitions,
                # )
                # if mqtt_config.enabled
                # else async_noop(),
                # read_elster_canbus(topic=elster_frames, bus=bus),
                # poll_elster_registers_canbus(
                #     bus=bus,
                #     polling_configurations=polling_configurations,
                #     sender_id=sender_id,
                # ),
            )


async def async_noop():
    pass


# def create_register_polling_configuration(
#     register_definition: RegisterDefinition,
#     register_configuration: Optional[RegisterConfiguration],
#     default_register_configuration: DefaultRegisterConfiguration,
# ) -> RegisterPollingConfiguration:
#     return RegisterPollingConfiguration(
#         register_definition=register_definition,
#         enabled=register_configuration.polling_enabled
#         if register_configuration and register_configuration.polling_enabled != None
#         else default_register_configuration.polling_enabled,
#         interval=register_configuration.polling_interval
#         if register_configuration and register_configuration.polling_interval != None
#         else default_register_configuration.polling_interval,
#     )
