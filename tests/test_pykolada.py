import pytest
import pykolada

query = pykolada.query

# If needed, setup and teardown can be managed using pytest fixtures


def test_kpi_endpoint_valid():
    result = query("kpi", id="N00011")
    assert isinstance(result, list)
    assert len(result) > 0


def test_kpi_endpoint_invalid():
    with pytest.raises(ValueError):
        query("kpi", invalid_param="123")


def test_kpi_groups_endpoint_valid():
    result = query("kpi_groups", id="G2KPI113774")
    assert isinstance(result, list)
    assert len(result) > 0


def test_kpi_groups_endpoint_invalid():
    with pytest.raises(ValueError):
        query("kpi_groups", invalid_param="abc")


def test_municipality_endpoint_valid():
    result = query("municipality", id="0180")
    assert isinstance(result, list)
    assert len(result) > 0


def test_municipality_endpoint_invalid():
    with pytest.raises(ValueError):
        query("municipality", invalid_param="xyz")


def test_municipality_groups_endpoint_valid():
    result = query("municipality_groups", id="G128518")
    assert isinstance(result, list)
    assert len(result) > 0


def test_municipality_groups_endpoint_invalid():
    with pytest.raises(ValueError):
        query("municipality_groups", invalid_param="def")


def test_ou_endpoint_valid():
    result = query("ou", id="V17E74148070")
    assert isinstance(result, list)
    assert len(result) > 0


def test_ou_endpoint_invalid():
    with pytest.raises(ValueError):
        query("ou", invalid_param="ghi")


def test_data_endpoint_valid():
    result = query("data", kpi="N00011", municipality="0114", year="2020")
    assert isinstance(result, list)
    assert len(result) > 0


def test_data_endpoint_invalid():
    with pytest.raises(ValueError):
        query("data", invalid_param="jkl")


def test_oudata_endpoint_valid():
    result = query("oudata", kpi="U21468", ou="V21E0010", year="2020")
    assert isinstance(result, list)
    assert len(result) > 0


def test_oudata_endpoint_invalid():
    with pytest.raises(ValueError):
        query("oudata", invalid_param="mno")


def run_all():
    test_kpi_endpoint_valid()
    test_kpi_endpoint_invalid()
    test_kpi_groups_endpoint_valid()
    test_kpi_groups_endpoint_invalid()
    test_municipality_endpoint_valid()
    test_municipality_endpoint_invalid()
    test_municipality_groups_endpoint_valid()
    test_municipality_groups_endpoint_invalid()
    test_ou_endpoint_valid()
    test_ou_endpoint_invalid()
    test_data_endpoint_valid()
    test_data_endpoint_invalid()
    test_oudata_endpoint_valid()
    test_oudata_endpoint_invalid()
