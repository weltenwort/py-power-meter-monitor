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


def test_data_message():
    frame = b"\x02%s!\r\n\x03\x67" % sample_data_block
    message = DataMessage(
        timestamp=0, data=DataBlock.from_bytes(timestamp=0, data=sample_data_block)
    )

    assert bytes(message) == frame
    assert bytes(message).startswith(DataMessage.initiator)
    assert DataMessage.from_bytes(timestamp=0, frame=frame) == message


sample_data_block = (
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
