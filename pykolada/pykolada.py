import requests
import urllib.parse
from typing import Any, Dict, List, Union
import json
import os

BASE_URL = "http://api.kolada.se/v2/"

ENDPOINTS = [
    "kpi",
    "kpi_groups",
    "municipality",
    "municipality_groups",
    "ou",
    "data",
    "oudata",
]

PARAMETERS = {
    "kpi": {
        "id": "primary_key",
        "title": "query",
        "description": "query",
        "operating_area": "query",
    },
    "kpi_groups": {"id": "primary_key", "title": "query"},
    "municipality": {
        "id": "primary_key",
        "title": "query",
    },
    "municipality_groups": {
        "id": "primary_key",
        "title": "query",
    },
    "ou": {"id": "primary_key", "title": "query"},
    "data": {
        "kpi": "path",
        "municipality": "path",
        "year": "path",
    },
    "oudata": {
        "kpi": "path",
        "ou": "path",
        "year": "path",
    },
}

path_construction_order = ["kpi", "municipality", "ou", "year"]


def _make_request(url: str) -> list:
    """Fetches all data from a given endpoint, handling pagination."""
    all_data = []
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                f"Error fetching data: HTTP {response.status_code}. URL: {url}"
            )
        data = response.json()
        all_data.extend(data.get("values", []))
        url = data.get("next_page")
    return all_data


def _build_url(
    endpoint: str,
    primary_keys: dict = None,
    path_params: dict = None,
    query_params: dict = None,
) -> str:
    """Builds a URL for a given endpoint and parameters.
    Assumes that the provided parameters are valid.

    Parameters
    ----------
    endpoint : str
        The endpoint to build a URL for.
    primary_keys: list[str]
        A list of primary keys.
    path_params : dict
        A dictionary of path parameters.
    query_params : dict
        A dictionary of query parameters.

    Returns
    -------
    A URL string.
    """
    # Print for debugging
    # print(f"endpoint: {endpoint}")
    # print(f"primary_keys: {json.dumps(primary_keys, indent=4, ensure_ascii=False)}")
    # print(f"path_params: {json.dumps(path_params, indent=4, ensure_ascii=False)}")
    # print(f"query_params: {json.dumps(query_params, indent=4, ensure_ascii=False)}")
    # print("")

    url = BASE_URL + endpoint
    if primary_keys:
        url += "/" + ",".join(primary_keys)
        return url

    if path_params:
        for key in path_construction_order:
            if key in path_params:
                if isinstance(path_params[key], str):
                    url += "/" + key + "/" + path_params[key]
                elif isinstance(path_params[key], list):
                    url += "/" + key + "/" + ",".join(path_params[key])

    if query_params:
        url += "?"
        for key, value in query_params.items():
            if isinstance(value, str):
                url += key + "=" + urllib.parse.quote(value) + "&"
            elif isinstance(value, list):
                for item in value:
                    url += key + "=" + urllib.parse.quote(item) + "&"

        # Remove the last "&"
        url = url[:-1]

    return url


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


def query(
    endpoint: str,
    **kwargs,
):
    """A function for interacting with the Kolada API.

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
    if endpoint not in ENDPOINTS:
        raise ValueError(
            f"Invalid endpoint: {endpoint}. Valid endpoints are: {ENDPOINTS}"
        )

    input_parameters = {
        "primary_key": [],
        "query": {},
        "path": {},
    }

    # If present convert "year" to string or list of strings
    if "year" in kwargs:
        if isinstance(kwargs["year"], int):
            kwargs["year"] = str(kwargs["year"])
        elif isinstance(kwargs["year"], list):
            kwargs["year"] = [str(year) for year in kwargs["year"]]

    # Remove any parameters with value None or empty list or empty string
    kwargs = {k: v for k, v in kwargs.items() if v}

    # Check that all given parameters are valid
    for key, value in kwargs.items():
        if key not in PARAMETERS[endpoint]:
            raise ValueError(
                f"Invalid parameter: {key}. Valid parameters for endpoint {endpoint} are: {PARAMETERS[endpoint]}"
            )

        # Check that the parameter value is a string (or list of strings for primary_key and path)
        if not isinstance(value, str) and not isinstance(value, list):
            raise ValueError(
                f"Invalid parameter value: {value}. Parameter values must be strings or lists of strings."
            )

        if isinstance(value, list):
            if (
                PARAMETERS[endpoint][key] != "primary_key"
                and PARAMETERS[endpoint][key] != "path"
            ):
                raise ValueError(
                    f"Invalid parameter value: {value}. Parameter values must be strings or lists of strings."
                )
            else:
                for item in value:
                    if not isinstance(item, str):
                        raise ValueError(
                            f"Invalid parameter value: {value}. Parameter values must be strings or lists of strings."
                        )

        elif not isinstance(value, str):
            raise ValueError(
                f"Invalid parameter value: {value}. Parameter values must be strings or lists of strings."
            )

        # If the parameter is a primary_key add the value to the primary_keys list
        if PARAMETERS[endpoint][key] == "primary_key":
            input_parameters["primary_key"].append(value)

        # Else add the parameter to the input_parameters list as a dictionary
        else:
            input_parameters[PARAMETERS[endpoint][key]][key] = value

    # Build the URL
    url = _build_url(
        endpoint,
        primary_keys=input_parameters["primary_key"],
        path_params=input_parameters["path"],
        query_params=input_parameters["query"],
    )

    # Make the request
    json_data = _make_request(url)

    if endpoint in ["data", "oudata"]:
        json_data = _format_data_response(endpoint, json_data)

    return json_data


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


def api_query(endpoint: str, **kwargs) -> List[Dict]:
    """
    Routes a request to the appropriate function based on the endpoint.

    Parameters
    ----------
    endpoint : str
        The name of the endpoint.
    kwargs : dict
        Additional arguments to pass to the endpoint function.

    Returns
    -------
    A list of dictionaries containing the response from the API.

    Raises
    ------
    ValueError
        If an invalid endpoint is provided.
    """
    if endpoint not in ENDPOINTS:
        raise ValueError(
            f"Invalid endpoint: {endpoint}. Valid endpoints are: {ENDPOINTS}"
        )

    if endpoint == "kpi":
        return get_kpi(**kwargs)
    elif endpoint == "kpi_groups":
        return get_kpi_groups(**kwargs)
    elif endpoint == "municipality":
        return get_municipality(**kwargs)
    elif endpoint == "municipality_groups":
        return get_municipality_groups(**kwargs)
    elif endpoint == "ou":
        return get_ou(**kwargs)
    elif endpoint == "data":
        return get_data(**kwargs)
    elif endpoint == "oudata":
        return get_oudata(**kwargs)
    else:
        raise ValueError(
            f"Endpoint '{endpoint}' is not yet implemented in the route_request function."
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
    # Raise an error if the endpoint is data or oudata
    if endpoint in ["data", "oudata"]:
        raise ValueError(
            f"Endpoint '{endpoint}' does not support the _get_all_data function."
        )

    return api_query(endpoint)


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


# def main():
#     _save_non_data(folder_path="data")


# if __name__ == "__main__":
#     main()
