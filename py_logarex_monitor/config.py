from pathlib import Path
from typing import Optional

from pydantic import BaseModel
import tomlkit


def load_default_configuration():
    return PyLogarexMonitorConfig()


def load_configuration_from_file_path(config_file_path: Path):
    if not config_file_path.is_file():
        return load_default_configuration()

    return load_configuration_from_text(config_file_path.read_text())


def load_configuration_from_text(config_file_text: str) -> "PyLogarexMonitorConfig":
    return PyLogarexMonitorConfig.parse_obj(dict(tomlkit.parse(config_file_text)))


# class DefaultRegisterConfiguration(BaseModel):
#     polling_enabled: bool = True
#     polling_interval: float = 60.0


# class RegisterConfiguration(BaseModel):
#     elster_index: int
#     polling_enabled: Optional[bool]
#     polling_interval: Optional[float]


class SerialPortConfig(BaseModel):
    port_url: str = "/dev/ttyUSB0"
    polling_interval: float = 30.0

    class Config:
        allow_mutation = False


class MqttBrokerConfig(BaseModel):
    hostname: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None


class MqttDeviceConfig(BaseModel):
    id: str = "logarex-power-meter-0"
    name: str = "Logarex Power Meter 0"
    manufacturer: str = "Logarex"
    model: str = "Unknown Model"


class MqttConfig(BaseModel):
    enabled: bool = True
    configuration_topic_template: str = "homeassistant/sensor/{device_id}/config"
    state_topic_template: str = "homeassistant/sensor/{device_id}/state"

    broker: MqttBrokerConfig = MqttBrokerConfig()
    device: MqttDeviceConfig = MqttDeviceConfig()


class PyLogarexMonitorConfig(BaseModel):
    serial_port: SerialPortConfig = SerialPortConfig()
    mqtt: MqttConfig = MqttConfig()

    class Config:
        allow_mutation = False
