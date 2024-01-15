import requests
import urllib.parse
from typing import Any, Dict, List, Union
import json
import os

BASE_URL = "http://api.kolada.se/v2/"

# Roles
# primary_key:
# The parameter is used to identify a single object.
# Is added directly to the URL after the endpoint.
# BASE_URL + endpoint + / + primary_key
# Other parameters are ignored.

# path:
# The parameter is used to add path filters to the URL.
# BASE_URL + endpoint + / + path_name + / + path_value
# Query parameters are added after the path parameters.

# query:
# Added to the end of the URL as a query string.
# BASE_URL + endpoint + path_arguments + ? + query_name + = + query_value
# Multiple query parameters are separated by &.

# filter:
# Filter parameters are used to filter the response from the API.
# Not added to the URL.
# Filter parameters are applied after the response is received.


# type:
# The type of the parameter.
#

ENDPOINTS = {
    "kpi": {
        "id": {
            "type": "str",
            "role": "primary_key",
        },
        "title": {
            "type": "str",
            "role": "query",
        },
        "description": {
            "type": "str",
            "role": "query",
        },
        "operating_area": {
            "type": "str",
            "role": "query",
        },
    },
    "kpi_groups": {
        "id": {
            "type": "str",
            "role": "primary_key",
        },
        "title": {
            "type": "str",
            "role": "query",
        },
    },
    "municipality": {
        "id": {
            "type": "str",
            "role": "primary_key",
        },
        "title": {
            "type": "str",
            "role": "query",
        },
    },
    "municipality_groups": {
        "id": {
            "type": "str",
            "role": "primary_key",
        },
        "title": {
            "type": "str",
            "role": "query",
        },
    },
    "ou": {
        "id": {
            "type": "str",
            "role": "primary_key",
        },
        "title": {
            "type": "str",
            "role": "query",
        },
        # "municipality": {
        #     "type": "str",
        #     "role": "filter",
        # },
    },
    "data": {
        "kpi": {
            "type": "str",
            "role": "path",
        },
        "municipality": {
            "type": "str",
            "role": "path",
        },
        "year": {
            "type": "str",
            "role": "path",
        },
    },
    "oudata": {
        "kpi": {
            "type": "str",
            "role": "path",
        },
        "ou": {
            "type": "str",
            "role": "path",
        },
        "year": {
            "type": "str",
            # Also accepts int
            "role": "path",
        },
    },
}


def _build_url(endpoint: str, path_params: dict, query_params: dict) -> str:
    """Builds a URL for a given endpoint and parameters.
    Assumes that the provided parameters are valid.

    Parameters
    ----------
    endpoint : str
        The endpoint to build a URL for.
    path_params : dict
        A dictionary of path parameters.
    query_params : dict
        A dictionary of query parameters.

    Returns
    -------
    A URL string.
    """

    # Build path
    path = ""
    for param in ENDPOINTS[endpoint]:
        if param in path_params:
            if isinstance(path_params[param], list):
                path += f"/{','.join(path_params[param])}"
            else:
                path += f"/{path_params[param]}"

    # Build query
    query = ""
    for param in ENDPOINTS[endpoint]:
        if param in query_params:
            if isinstance(query_params[param], list):
                query += f"{param}={','.join(query_params[param])}&"
            else:
                query += f"{param}={query_params[param]}&"

    # Remove trailing &
    if query:
        query = "?" + query[:-1]

    return BASE_URL + endpoint + path + query


def _make_request(url: str) -> list:
    """Fetches all data from a given endpoint, handling pagination."""
    all_data = []
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: HTTP {response.status_code}")
        data = response.json()
        all_data.extend(data.get("values", []))
        url = data.get("next_page")
    return all_data


def _filter_results(
    endpoint: str, data: List[Dict], filters: Dict[str, Any]
) -> List[Dict]:
    """
    Filters the API response data based on given criteria.
    For strings: substring matching.
    For lists of strings: substring matching for any item in the list.
    For other types: exact match.
    For lists of other types: exact match for any item in the list.
    """
    # TODO: Add support for filtering results returned by the api
    return data


def _format_data_response(endpoint: str, data: List[Dict]) -> List[Dict]:
    """Formats responses from the data and oudata endpoints."""
    entry_structure = {
        "kpi": "",
        "year": "",
        "gender": "",
        "value": "",
    }

    endpoint_specific_key = ""
    if endpoint == "data":
        endpoint_specific_key = "municipality"
    elif endpoint == "oudata":
        endpoint_specific_key = "ou"
    else:
        raise ValueError(f"Invalid endpoint: {endpoint}")

    entry_structure[endpoint_specific_key] = ""

    formatted_data = []
    for input_entry in data:
        try:
            new_entry_base = entry_structure.copy()
            new_entry_base["kpi"] = input_entry["kpi"]
            new_entry_base["year"] = input_entry["period"]
            new_entry_base[endpoint_specific_key] = input_entry[endpoint_specific_key]
            for value in input_entry["values"]:
                new_entry = new_entry_base.copy()
                new_entry["gender"] = value["gender"]
                new_entry["value"] = value["value"]
                formatted_data.append(new_entry)
        except KeyError:
            raise Exception(
                f"Error formatting data: {input_entry}",
                f"Endpoint: {endpoint}",
                f"Input data: {data}",
            )

    return formatted_data


def query(endpoint: str, **kwargs) -> List[Dict]:
    """Main function to handle API queries.

    Parameters
    ----------
    endpoint : str
        The name of the endpoint.
    kwargs : dict
        Additional arguments to pass to the endpoint function.

    Returns
    -------
    A list of dictionaries containing the response from the API.
    """
    # Validate endpoint
    assert (
        endpoint in ENDPOINTS
    ), f"Invalid endpoint: {endpoint}. Valid endpoints are: {list(ENDPOINTS.keys())}"

    # Remove None values from kwargs
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    # Validate parameters
    assert set(kwargs.keys()).issubset(
        ENDPOINTS[endpoint].keys()
    ), f"Invalid parameters: {set(kwargs.keys()) - set(ENDPOINTS[endpoint].keys())}. Valid parameters are: {ENDPOINTS[endpoint].keys()}"

    # Add a special case for the year parameter which if an int or list of ints is converted to a string or list of strings.
    if "year" in kwargs:
        if isinstance(kwargs["year"], int):
            kwargs["year"] = str(kwargs["year"])
        elif isinstance(kwargs["year"], list):
            kwargs["year"] = [str(item) for item in kwargs["year"]]

    parameters = {
        "path": {},
        "query": {},
        "filter": {},
    }

    # If a primary key is provided, ignore all other parameters.
    param_types = [ENDPOINTS[endpoint][param]["role"] for param in kwargs]
    if "primary_key" in param_types:
        if len(param_types) > 1:
            print(
                f"""Warning: primary_key parameter (id) provided for endpoint {endpoint}. Ignoring all other parameters."""
            )

        # Validate parameter is a string
        assert isinstance(
            kwargs["id"], str
        ), f"Invalid type for parameter id. id must be a str."

        url = BASE_URL + endpoint + "/" + kwargs["id"]
        return _make_request(url)

    # Validate parameter types.
    # Note: all parameters with the role "path" OR "filter" can also be lists of the specified type.
    for param, value in kwargs.items():
        if isinstance(value, list):
            # Check that the role is "path"
            assert (
                ENDPOINTS[endpoint][param]["role"] == "path"
                or ENDPOINTS[endpoint][param]["role"] == "filter"
            ), f"Invalid type for parameter: {param}. {param} must be a {ENDPOINTS[endpoint][param]['type']} and not a list."

            # Check that the type is valid
            assert all(
                isinstance(item, ENDPOINTS[endpoint][param]["type"]) for item in value
            ), f"Invalid type for parameter {param}. {param} must be a {ENDPOINTS[endpoint][param]['type']} or a list of {ENDPOINTS[endpoint][param]['type']}."

        else:
            assert isinstance(
                value, ENDPOINTS[endpoint][param]["type"]
            ), f"Invalid type for parameter {param}. {param} must be a {ENDPOINTS[endpoint][param]['type']}."

        # Add parameter to parameters dict
        parameters[ENDPOINTS[endpoint][param]["role"]][param] = value

    # Build URL
    url = _build_url(
        endpoint=endpoint,
        path_params=parameters["path"],
        query_params=parameters["query"],
    )

    # Try to fetch data
    try:
        data = _make_request(url)
    except Exception as e:
        raise Exception(
            f"Error fetching data: {e}",
            f"URL: {url}",
            f"Input parameters: {kwargs}",
        )

    # Format data and oudata responses
    if endpoint in ["data", "oudata"]:
        data = _format_data_response(endpoint=endpoint, data=data)

    # Filter results if applicable
    # if parameters["filter"]:
    #     data = _filter_results(
    #         endpoint=endpoint, data=data, filters=parameters["filter"]
    #     )

    return data


def get_kpi(
    id: str = None,
    title: str = None,
    description: str = None,
    operating_area: str = None,
) -> List[Dict]:
    """A function for retrieving and filtering KPIs.

    Parameters
    ----------
    id : str
        The id of the KPI.
    title : str
        A KPI title to search for. Filtered by substring matching.
    description : str
        A KPI description to search for. Filtered by substring matching.
    operating_area : str
        A KPI operating area to search for. Filtered by substring matching.
    Returns
    -------
    A list of dictionaries for the KPIs matching the search criteria.
    """
    return query(
        endpoint="kpi",
        id=id,
        title=title,
        description=description,
        operating_area=operating_area,
    )


def get_kpi_groups(id: str = None, title: str = None) -> List[Dict]:
    """A function for retrieving and filtering KPI groups.

    Parameters
    ----------
    id : str
        The id of the KPI group.
    title : str
        A KPI group title to search for. Filtered by substring matching.

    Returns
    -------
    A list of dictionaries for the KPI groups matching the search criteria.
    """

    return query(
        endpoint="kpi_groups",
        id=id,
        title=title,
    )


def get_municipality(
    id: str = None,
    title: str = None,
) -> List[Dict]:
    """A function for retrieving and filtering municipalities.

    Parameters
    ----------
    id : str
        The id of the municipality.
    title : str
        A municipality title to search for. Filtered by substring matching.

    Returns
    -------
    A list of dictionaries for the municipalities matching the search criteria.
    """

    return query(
        endpoint="municipality",
        id=id,
        title=title,
    )


def get_municipality_groups(id: str = None, title: str = None) -> List[Dict]:
    """A function for retrieving and filtering municipality groups.

    Parameters
    ----------
    id : str
        The id of the municipality group.
    title : str
        A municipality group title to search for. Filtered by substring matching.

    Returns
    -------
    A list of dictionaries for the municipality groups matching the search criteria.
    """

    return query(
        endpoint="municipality_groups",
        id=id,
        title=title,
    )


def get_ou(
    id: str = None,
    title: str = None,
) -> List[Dict]:
    """A function for retrieving and filtering organization units.

    Parameters
    ----------
    id : str
        The id of the organization unit.
    title : str
        An organization unit title to search for. Filtered by substring matching.

    Returns
    -------
    A list of dictionaries for the organization units matching the search criteria.
    """

    return query(
        endpoint="ou",
        id=id,
        title=title,
    )


def get_data(
    kpi: [str, List[str]] = None,
    municipality: [str, List[str]] = None,
    year: [str, List[str], int, List[int]] = [str(i) for i in range(1970, 2025)],
) -> List[Dict]:
    """A function for retrieving and filtering data.
    At least two of the parameters kpi, municipality or year must be specified.

    Parameters
    ----------
    kpi : str or list of str
        The id(s) of the KPI(s) to retrieve data for.
    municipality : str or list of str
        The id(s) of the municipality(s) to retrieve data for.
    year : str, int, list of str or list of int
        The year(s) to retrieve data for. YYYY

    Returns
    -------
    A list of dictionaries for the data matching the search criteria.
    """

    return query(
        endpoint="data",
        kpi=kpi,
        municipality=municipality,
        year=year,
    )


def get_oudata(
    kpi: [str, List[str]],
    ou: [str, List[str]],
    year: [str, List[str], int, List[int]] = [str(i) for i in range(1970, 2025)],
) -> List[Dict]:
    """A function for retrieving and filtering data.

    Parameters
    ----------
    kpi : str or list of str
        The id(s) of the KPI(s) to retrieve data for.
    ou : str or list of str
        The id(s) of the organization unit(s) to retrieve data for.
    year : str, int, list of str or list of int
        The year(s) to retrieve data for. YYYY

    Returns
    -------
    A list of dictionaries for the data matching the search criteria.
    """

    return query(
        endpoint="oudata",
        kpi=kpi,
        ou=ou,
        year=year,
    )


def _get_all_data(endpoint: str):
    """Get all data for an endpoint.

    Parameters
    ----------
    endpoint : str
        The endpoint to get data for.

    Returns
    -------
    A list of dictionaries for the data for the specified endpoint.
    """
    if endpoint not in ENDPOINTS:
        raise ValueError(f"Invalid endpoint: {endpoint}")

    if endpoint in ["data", "oudata"]:
        raise ValueError(f"Invalid endpoint: {endpoint}")

    if endpoint == "kpi":
        return get_kpi()
    elif endpoint == "kpi_groups":
        return get_kpi_groups()
    elif endpoint == "municipality":
        return get_municipality()
    elif endpoint == "municipality_groups":
        return get_municipality_groups()
    elif endpoint == "ou":
        return get_ou()


def _save_non_data(folder_path=None):
    """Save data for all endpoints except data and oudata.

    Parameters
    ----------
    folder_path : str
        The path to the folder where the data should be saved. Defaults to current working directory.
    """
    if folder_path is None:
        folder_path = os.getcwd()

    for endpoint in ENDPOINTS:
        if endpoint not in ["data", "oudata"]:
            json_data = _get_all_data(endpoint)
            with open(
                os.path.join(folder_path, f"{endpoint}.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)


def main():
    _save_non_data(folder_path="data")


if __name__ == "__main__":
    main()
