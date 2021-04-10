import pytest

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
        DataSet(timestamp=0, address="1-0:16.7.0*255", value="000028", unit="W")
    )

    assert obis_data_set == ObisIntegerDataSet(
        timestamp=0, id=(1, 0, 16, 7, 0, 255), value=28, unit="W"
    )


def test_parse_obis_float_data_set():
    obis_data_set = ObisFloatDataSet.from_iec_62056_21_data_set(
        DataSet(timestamp=0, address="1-0:1.8.0*255", value="015882.6927", unit="kWh")
    )

    assert obis_data_set == ObisFloatDataSet(
        timestamp=0, id=(1, 0, 1, 8, 0, 255), value=15882.6927, unit="kWh"
    )


def test_parse_obis_string_data_set():
    obis_data_set = ObisStringDataSet.from_iec_62056_21_data_set(
        DataSet(
            timestamp=0,
            address="1-0:0.2.0*255",
            value="ver.03,432F,20170504",
            unit=None,
        )
    )

    assert obis_data_set == ObisStringDataSet(
        timestamp=0, id=(1, 0, 0, 2, 0, 255), value="ver.03,432F,20170504", unit=None
    )


def test_parse_only_mandatory_groups():
    assert parse_obis_id_from_address("1.2") == (0, 0, 1, 2)


def test_parse_shortened_end():
    assert parse_obis_id_from_address("1-1:1.2") == (1, 1, 1, 2)


def test_parse_obis_display_code_f():
    assert parse_obis_id_from_address("1-1:F.F") == (1, 1, 97, 97)


def test_parse_obis_display_code_c():
    assert parse_obis_id_from_address("1-1:C.7.0") == (1, 1, 96, 7, 0)


def test_parse_obis_display_code_l():
    assert parse_obis_id_from_address("1-1:L.0") == (1, 1, 98, 0)


def test_parse_obis_display_code_p():
    assert parse_obis_id_from_address("1-1:P.0") == (1, 1, 99, 0)


def test_parse_group_f_separator_star():
    assert parse_obis_id_from_address("1-2:3.4.5*6") == (1, 2, 3, 4, 5, 6)


def test_parse_group_f_separator_ampersand():
    assert parse_obis_id_from_address("1-2:3.4.5&6") == (1, 2, 3, 4, 5, 6)


def test_parse_group_f_separator_period():
    assert parse_obis_id_from_address("1-2:3.4.5.6") == (1, 2, 3, 4, 5, 6)


def test_parse_raise_value_error():
    with pytest.raises(ValueError):
        parse_obis_id_from_address("1-2:3")
