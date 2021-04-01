from enum import Enum, IntEnum
from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union

from pydantic import BaseModel
import tomlkit

from .iec_62056_protocol.obis_data_set import (
    ObisFloatDataSet,
    ObisIntegerDataSet,
    ObisStringDataSet,
)


def load_default_configuration():
    return PyPowerMeterMonitorConfig()


def load_configuration_from_file_path(config_file_path: Path):
    if not config_file_path.is_file():
        return load_default_configuration()

    return load_configuration_from_text(config_file_path.read_text())


def load_configuration_from_text(config_file_text: str) -> "PyPowerMeterMonitorConfig":
    return PyPowerMeterMonitorConfig.parse_obj(dict(tomlkit.parse(config_file_text)))


class LoggingLevel(IntEnum):
    critical = 50
    error = 40
    warning = 30
    info = 20
    debug = 10


class LoggingConfig(BaseModel):
    level: LoggingLevel = LoggingLevel.error


class SerialPortParity(Enum):
    NONE = "N"
    EVEN = "E"
    ODD = "O"
    MARK = "M"
    SPACE = "S"


class SerialPortStopBits(Enum):
    ONE = 1
    ONE_POINT_FIVE = 1.5
    TWO = 2


class SerialPortConfig(BaseModel):
    port_url: str = "/dev/ttyUSB0"
    baud_rate: int = 9600
    byte_size: int = 8
    parity: SerialPortParity = SerialPortParity.NONE
    stop_bits: SerialPortStopBits = SerialPortStopBits.ONE
    polling_delay: float = 30.0
    response_delay: float = 0.5
    read_timeout: float = 10.0
    write_timeout: float = 10.0

    class Config:
        allow_mutation = False


class MqttBrokerConfig(BaseModel):
    hostname: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None


class MqttDeviceConfig(BaseModel):
    id: str = "power-meter-0"
    name: str = "Power Meter 0"
    manufacturer: str = "Unknown Manufacturer"
    model: str = "Unknown Model"


class MqttConfig(BaseModel):
    enabled: bool = True
    configuration_topic_template: str = "homeassistant/sensor/{entity_id}/config"
    state_topic_template: str = "homeassistant/sensor/{entity_id}/state"

    broker: MqttBrokerConfig = MqttBrokerConfig()
    device: MqttDeviceConfig = MqttDeviceConfig()


class ObisBaseDataSetConfig(BaseModel):
    id: Tuple[int, int, int, int, int, int]
    name: str


class ObisIntegerDataSetConfig(ObisBaseDataSetConfig):
    value_type: Literal["integer"]

    @property
    def obis_data_set_type(self):
        return ObisIntegerDataSet


class ObisFloatDataSetConfig(ObisBaseDataSetConfig):
    value_type: Literal["float"]

    @property
    def obis_data_set_type(self):
        return ObisFloatDataSet


class ObisStringDataSetConfig(ObisBaseDataSetConfig):
    value_type: Literal["string"]

    @property
    def obis_data_set_type(self):
        return ObisStringDataSet


ObisDataSetConfig = Union[
    ObisIntegerDataSetConfig, ObisFloatDataSetConfig, ObisStringDataSetConfig
]


class ObisConfig(BaseModel):
    data_sets: List[ObisDataSetConfig] = []


class PyPowerMeterMonitorConfig(BaseModel):
    logging: LoggingConfig = LoggingConfig()
    serial_port: SerialPortConfig = SerialPortConfig()
    mqtt: MqttConfig = MqttConfig()
    obis: ObisConfig = ObisConfig()

    class Config:
        allow_mutation = False
