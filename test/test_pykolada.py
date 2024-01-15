import pykolada


def test_query():
    # Test valid endpoint and parameters
    result = pykolada.query("data", year=2021, region="SE")
    assert isinstance(result, list)
    assert len(result) > 0

    # Test invalid endpoint
    try:
        pykolada.query("invalid_endpoint", year=2021, region="SE")
        assert False, "Expected ValueError for invalid endpoint"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid endpoint: invalid_endpoint. Valid endpoints are: ['data', 'oudata']"
        )

    # Test invalid parameter
    try:
        pykolada.query("data", year=2021, invalid_param="value")
        assert False, "Expected ValueError for invalid parameter"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter: invalid_param. Valid parameters for endpoint data are: ['year', 'region']"
        )

    # Test invalid parameter value type
    try:
        pykolada.query("data", year=2021, region=123)
        assert False, "Expected ValueError for invalid parameter value type"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter value: 123. Parameter values must be strings or lists of strings."
        )

    # Test invalid parameter value type in list
    try:
        pykolada.query("data", year=2021, region=["SE", 123])
        assert False, "Expected ValueError for invalid parameter value type in list"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter value: 123. Parameter values must be strings or lists of strings."
        )

    # Test empty parameter value
    try:
        pykolada.query("data", year=2021, region="")
        assert False, "Expected ValueError for empty parameter value"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter value: . Parameter values must be strings or lists of strings."
        )

    # Test empty parameter value in list
    try:
        pykolada.query("data", year=2021, region=["SE", ""])
        assert False, "Expected ValueError for empty parameter value in list"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter value: . Parameter values must be strings or lists of strings."
        )

    # Test empty parameter value in list for primary_key
    try:
        pykolada.query("data", year=2021, region=["SE"], primary_key=[""])
        assert (
            False
        ), "Expected ValueError for empty parameter value in list for primary_key"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter value: . Parameter values must be strings or lists of strings."
        )

    # Test empty parameter value for primary_key
    try:
        pykolada.query("data", year=2021, region="SE", primary_key="")
        assert False, "Expected ValueError for empty parameter value for primary_key"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter value: . Parameter values must be strings or lists of strings."
        )

    # Test missing required parameter
    try:
        pykolada.query("data", year=2021)
        assert False, "Expected ValueError for missing required parameter"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter: region. Valid parameters for endpoint data are: ['year', 'region']"
        )

    # Test missing required parameter in list
    try:
        pykolada.query("data", year=2021, region=["SE"])
        assert False, "Expected ValueError for missing required parameter in list"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter: region. Valid parameters for endpoint data are: ['year', 'region']"
        )

    # Test missing required parameter for primary_key
    try:
        pykolada.query("data", year=2021, primary_key="SE")
        assert (
            False
        ), "Expected ValueError for missing required parameter for primary_key"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter: region. Valid parameters for endpoint data are: ['year', 'region']"
        )

    # Test missing required parameter in list for primary_key
    try:
        pykolada.query("data", year=2021, primary_key=["SE"])
        assert (
            False
        ), "Expected ValueError for missing required parameter in list for primary_key"
    except ValueError as e:
        assert (
            str(e)
            == "Invalid parameter: region. Valid parameters for endpoint data are: ['year', 'region']"
        )

    # Test empty kwargs
    result = pykolada.query("data")
    assert isinstance(result, list)
    assert len(result) > 0

    print("All tests passed!")


test_query()
