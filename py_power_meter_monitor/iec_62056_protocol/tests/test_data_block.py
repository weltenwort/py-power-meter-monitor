from ..data_block import DataBlock


def test_parse_empty_data_block():
    assert DataBlock.from_bytes(timestamp=0, data=b"") == DataBlock(
        manufacturer_identification="", data_lines=[]
    )
