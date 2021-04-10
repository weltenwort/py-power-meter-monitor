from pytest import raises

from ..data_block import DataBlock
from ..errors import ParsingError
from ..iec_62056_21_messages import (
    AcknowledgementMessage,
    DataMessage,
    IdentificationMessage,
    RequestMessage,
)


def test_request_message_from_bytes():
    frame = b"/?!\r\n"
    message = RequestMessage(timestamp=0)

    assert bytes(message) == frame
    assert bytes(message).startswith(RequestMessage.initiator)
    assert RequestMessage.from_bytes(timestamp=0, frame=frame) == message


def test_request_message_from_bytes_raises():
    with raises(ParsingError):
        RequestMessage.from_bytes(timestamp=0, frame=b"invalid")


def test_request_message_with_device_address():
    frame = b"/?SOME_ADDRESS!\r\n"
    message = RequestMessage(timestamp=0, device_address="SOME_ADDRESS")

    assert bytes(message) == frame
    assert bytes(message).startswith(RequestMessage.initiator)
    assert RequestMessage.from_bytes(timestamp=0, frame=frame) == message


def test_identification_message():
    frame = b"/LOG5LK123\r\n"
    message = IdentificationMessage(
        timestamp=0,
        manufacturer_id="LOG",
        baud_rate_id="5",
        mode_ids="",
        identification="LK123",
    )

    assert bytes(message) == frame
    assert bytes(message).startswith(IdentificationMessage.initiator)
    assert IdentificationMessage.from_bytes(timestamp=0, frame=frame) == message


def test_identification_message_with_sequence_delimiter():
    frame = b"/LGZ5\\2ZMD3104107.B40\r\n"
    message = IdentificationMessage(
        timestamp=0,
        manufacturer_id="LGZ",
        baud_rate_id="5",
        mode_ids="\\2",
        identification="ZMD3104107.B40",
    )

    assert bytes(message) == frame
    assert IdentificationMessage.from_bytes(timestamp=0, frame=frame) == message


def test_acknowledgement_message():
    frame = b"\x06050\r\n"
    message = AcknowledgementMessage(
        timestamp=0, protocol_control="0", baud_rate_id="5", mode_control="0"
    )

    assert bytes(message) == frame
    assert bytes(message).startswith(AcknowledgementMessage.initiator)
    assert AcknowledgementMessage.from_bytes(timestamp=0, frame=frame) == message


def test_logarex_data_message():
    frame = b"\x02%s!\r\n\x03\x67" % sample_logarex_data_block
    message = DataMessage(
        timestamp=0,
        data=DataBlock.from_bytes(timestamp=0, data=sample_logarex_data_block),
    )

    assert bytes(message) == frame
    assert bytes(message).startswith(DataMessage.initiator)
    assert DataMessage.from_bytes(timestamp=0, frame=frame) == message


def test_landis_gyr_data_message():
    DataMessage.from_bytes(timestamp=0, frame=sample_landis_gyr_data_message_frame)


sample_logarex_data_block = (
    b"1-0:96.1.0*255(001LOG0065282495)\r\n"
    b"1-0:1.8.0*255(015882.6927*kWh)\r\n"
    b"1-0:2.8.0*255(000219.4882*kWh)\r\n"
    b"1-0:16.7.0*255(000028*W)\r\n"
    b"1-0:32.7.0*255(235.2*V)\r\n"
    b"1-0:52.7.0*255(235.8*V)\r\n"
    b"1-0:72.7.0*255(237.1*V)\r\n"
    b"1-0:31.7.0*255(000.90*A)\r\n"
    b"1-0:51.7.0*255(002.28*A)\r\n"
    b"1-0:71.7.0*255(001.85*A)\r\n"
    b"1-0:81.7.1*255(117*deg)\r\n"
    b"1-0:81.7.2*255(242*deg)\r\n"
    b"1-0:81.7.4*255(032*deg)\r\n"
    b"1-0:81.7.15*255(051*deg)\r\n"
    b"1-0:81.7.26*255(073*deg)\r\n"
    b"1-0:14.7.0*255(49.9*Hz)\r\n"
    b"1-0:1.8.0*96(00019.3*kWh)\r\n"
    b"1-0:1.8.0*97(00158.7*kWh)\r\n"
    b"1-0:1.8.0*98(01074.7*kWh)\r\n"
    b"1-0:1.8.0*99(09027.4*kWh)\r\n"
    b"1-0:1.8.0*100(15882.6*kWh)\r\n"
    b"1-0:0.2.0*255(ver.03,432F,20170504)\r\n"
    b"1-0:96.90.2*255(0F66)\r\n"
    b"1-0:97.97.0*255(00000000)\r\n"
)

sample_landis_gyr_data_message_frame = (
    b"\x021-1:F.F(00000000)\r\n"
    b"1-1:0.0.0(001LGZ0056859504)\r\n"
    b"1-1:0.9.1(185532)\r\n"
    b"1-1:0.9.2(210410)\r\n"
    b"1-1:0.1.0(01)\r\n"
    b"1-1:0.1.2*01(2104010000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:0.1.2*00(0000000000)\r\n"
    b"1-1:1.5.0(00.030*kW)\r\n"
    b"1-1:1.6.0(10.102*kW)(2104070015)\r\n"
    b"1-1:1.6.0*01(06.130)(2101281415)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:1.8.0(0000094.5*kWh)\r\n"
    b"1-1:1.8.0*01(0000010.2)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:1.8.0*00(0000000.0)\r\n"
    b"1-1:2.5.0(00.000*kW)\r\n"
    b"1-1:2.6.0(09.293*kW)(2104021300)\r\n"
    b"1-1:2.6.0*01(09.301)(2103301415)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.6.0*00(00.000)(0000000000)\r\n"
    b"1-1:2.8.0(0000293.9*kWh)\r\n"
    b"1-1:2.8.0*01(0000106.8)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:2.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0(0000001.1*kvarh)\r\n"
    b"1-1:5.8.0*01(0000001.1)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:5.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0(0000000.3*kvarh)\r\n"
    b"1-1:6.8.0*01(0000000.3)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:6.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0(0000036.8*kvarh)\r\n"
    b"1-1:7.8.0*01(0000008.8)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:7.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0(0000158.8*kvarh)\r\n"
    b"1-1:8.8.0*01(0000029.5)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:8.8.0*00(0000000.0)\r\n"
    b"1-1:C.5(0000E0F0)\r\n"
    b"1-1:C.7.0(00000008)\r\n"
    b"1-1:C.7.1(00000009)\r\n"
    b"1-1:C.7.2(00000010)\r\n"
    b"1-1:C.7.3(00000010)\r\n"
    b"1-1:0.2.0(B40)\r\n"
    b"1-1:0.2.1(017)\r\n"
    b"1-1:0.2.8(7F42)\r\n"
    b"1-1:32.7.0(235.2*V)\r\n"
    b"1-1:52.7.0(235.0*V)\r\n"
    b"1-1:72.7.0(237.6*V)\r\n"
    b"1-1:31.7.0(003.54*A)\r\n"
    b"1-1:51.7.0(007.63*A)\r\n"
    b"1-1:71.7.0(003.81*A)\r\n"
    b"1-1:36.7.0(-000.82*kW)\r\n"
    b"1-1:56.7.0( 001.67*kW)\r\n"
    b"1-1:76.7.0(-000.81*kW)\r\n"
    b"1-1:16.7.0( 000.03*kW)\r\n"
    b"1-1:151.7.0(-000.05*kvar)\r\n"
    b"1-1:171.7.0(-000.51*kvar)\r\n"
    b"1-1:191.7.0(-000.37*kvar)\r\n"
    b"1-1:131.7.0(-000.95*kvar)\r\n"
    b"1-1:0.5.1.2(80.000*kW)\r\n"
    b"!\r\n"
    b"\x03\n"
)  # the block check byte happens to be the newline char
