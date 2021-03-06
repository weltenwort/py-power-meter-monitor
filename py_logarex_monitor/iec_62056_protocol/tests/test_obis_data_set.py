from ..data_block import DataSet
from ..obis_data_set import (
    ObisFloatDataSet,
    ObisIntegerDataSet,
    ObisStringDataSet,
    parse_obis_id_from_address,
)


def test_parse_obis_id_from_address():
    assert parse_obis_id_from_address("1-0:96.1.0*255") == (1, 0, 96, 1, 0, 255)


def test_parse_obis_integer_data_set():
    obis_data_set = ObisIntegerDataSet.from_iec_62056_21_data_set(
        DataSet(address="1-0:16.7.0*255", value="000028", unit="W")
    )

    assert obis_data_set == ObisIntegerDataSet(
        id=(1, 0, 16, 7, 0, 255), value=28, unit="W"
    )


def test_parse_obis_float_data_set():
    obis_data_set = ObisFloatDataSet.from_iec_62056_21_data_set(
        DataSet(address="1-0:1.8.0*255", value="015882.6927", unit="kWh")
    )

    assert obis_data_set == ObisFloatDataSet(
        id=(1, 0, 1, 8, 0, 255), value=15882.6927, unit="kWh"
    )


def test_parse_obis_string_data_set():
    obis_data_set = ObisStringDataSet.from_iec_62056_21_data_set(
        DataSet(address="1-0:0.2.0*255", value="ver.03,432F,20170504", unit=None)
    )

    assert obis_data_set == ObisStringDataSet(
        id=(1, 0, 0, 2, 0, 255), value="ver.03,432F,20170504"
    )
