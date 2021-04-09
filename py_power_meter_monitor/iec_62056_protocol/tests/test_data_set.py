import re

from hypothesis import given
from hypothesis import strategies as st

from ..data_block import DataSet, data_set_encoding
from ..obis_data_set import obis_id_expression

address_strategy = st.from_regex(
    regex=re.compile(obis_id_expression.pattern.encode(data_set_encoding), re.X),
    fullmatch=True,
)
value_strategy = st.from_regex(regex=re.compile(b"^[^()*/!\\n]{1,32}$"), fullmatch=True)
unit_strategy = st.from_regex(regex=re.compile(b"^[^()/!]{1,16}$"), fullmatch=True)


@given(
    timestamp=st.integers(),
    address=address_strategy,
    value=value_strategy,
)
def test_parse_data_set_without_unit(timestamp: int, address: bytes, value: bytes):
    assert DataSet.from_bytes(
        timestamp=timestamp,
        line=b"%s(%s)" % (address, value),
    ) == DataSet(
        timestamp=timestamp,
        address=address.decode(data_set_encoding),
        value=value.decode(data_set_encoding),
        unit=None,
    )


@given(
    timestamp=st.integers(),
    address=address_strategy,
    value=value_strategy,
    unit=unit_strategy,
)
def test_parse_data_set_with_unit(
    timestamp: int, address: bytes, value: bytes, unit: bytes
):
    assert DataSet.from_bytes(
        timestamp=timestamp,
        line=b"%s(%s*%s)" % (address, value, unit),
    ) == DataSet(
        timestamp=timestamp,
        address=address.decode(data_set_encoding),
        value=value.decode(data_set_encoding),
        unit=unit.decode(data_set_encoding),
    )


@given(
    timestamp=st.integers(),
    address=address_strategy,
    values_and_units=st.lists(
        elements=st.tuples(  # type: ignore unkown member in upstream signature
            value_strategy, unit_strategy
        ),
        min_size=1,
    ),
)
def test_parse_data_set_with_multiple_values(
    timestamp: int, address: bytes, values_and_units: list[tuple[bytes, bytes]]
):
    values_bytes = b"".join(
        b"(%s*%s)" % (value, unit) for (value, unit) in values_and_units
    )

    assert DataSet.from_bytes(
        timestamp=timestamp,
        line=b"%s%s" % (address, values_bytes),
    ) == DataSet(
        timestamp=timestamp,
        address=address.decode(data_set_encoding),
        value=values_and_units[0][0].decode(data_set_encoding),
        unit=values_and_units[0][1].decode(data_set_encoding),
    )
