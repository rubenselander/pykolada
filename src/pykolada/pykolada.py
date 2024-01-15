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


def get_kpi(
    id: str = None,
    title: str = None,
    description: str = None,
    operating_area: str = None,
    has_ou_data: bool = None,
    is_divided_by_gender: bool = None,
    municipality_type: str = None,
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
    has_ou_data : bool
        Boolean indicating whether the KPI must have organization unit data.
    is_divided_by_gender : bool
         Boolean indicating whether the KPI must have gender specific data.
    municipality_type : str
        A municipality type to filter by. Valid values are: "L", "K", "A".

    Returns
    -------
    A list of dictionaries for the KPIs matching the search criteria.
    """

    url = BASE_URL + "kpi"
    url_suffixes = []

    if id:
        return _make_request(url + f"/{id}")

    if title:
        url_suffixes.append(f"title={urllib.parse.quote(title)}")

    if description:
        url_suffixes.append(f"description={urllib.parse.quote(description)}")

    if operating_area:
        url_suffixes.append(f"operating_area={urllib.parse.quote(operating_area)}")

    if url_suffixes:
        url += "?" + "&".join(url_suffixes)

    json_data = _make_request(url)

    if has_ou_data is not None:
        json_data = [item for item in json_data if item["has_ou_data"] == has_ou_data]

    if is_divided_by_gender is not None:
        json_data = [
            item for item in json_data if item["is_divided_by_gender"] == has_ou_data
        ]

    if municipality_type:
        json_data = [
            item for item in json_data if item["municipality_type"] == municipality_type
        ]

    return json_data


def get_kpi_groups(
    id: str = None,
    title: str = None,
    member_id: str = None,
    member_title: str = None,
) -> List[Dict]:
    """A function for retrieving and filtering KPI groups.

    Parameters
    ----------
    id : str
        The id of the KPI group.
    title : str
        A KPI group title to search for. Filtered by substring matching.
    member_id : str
        The id of a KPI group member.
    member_title : str
        A KPI group member title to search for. Filtered by substring matching.

    Returns
    -------
    A list of dictionaries for the KPI groups matching the search criteria.
    """

    if id:
        return _make_request(BASE_URL + f"kpi_groups/{id}")

    url = BASE_URL + "kpi_groups"
    url_suffixes = []

    if title:
        url_suffixes.append(f"title={urllib.parse.quote(title)}")

    json_data = _make_request(url)

    if member_id:
        new_json_data = []
        for item in json_data:
            for member in item["members"]:
                if member["member_id"] == member_id:
                    new_json_data.append(item)
                    break
        json_data = new_json_data

    if member_title:
        new_json_data = []
        for item in json_data:
            for member in item["members"]:
                if member["member_title"] == member_title:
                    new_json_data.append(item)
                    break
        json_data = new_json_data

    return json_data


def get_municipality(
    id: str = None,
    title: str = None,
    type: str = None,
) -> List[Dict]:
    """A function for retrieving and filtering municipalities.

    Parameters
    ----------
    id : str
        The id of the municipality.
    title : str
        A municipality title to search for. Filtered by substring matching.
    type : str
        A municipality type to filter by. Valid values are: "L", "K".

    Returns
    -------
    A list of dictionaries for the municipalities matching the search criteria.
    """

    if id:
        return _make_request(BASE_URL + f"municipality/{id}")

    url = BASE_URL + "municipality"
    url_suffixes = []

    if title:
        url_suffixes.append(f"title={urllib.parse.quote(title)}")

    json_data = _make_request(url)

    if type:
        json_data = [item for item in json_data if item["type"] == type]

    return json_data


def get_municipality_groups(
    id: str = None,
    title: str = None,
    member_id: str = None,
    member_title: str = None,
) -> List[Dict]:
    """A function for retrieving and filtering municipality groups.

    Parameters
    ----------
    id : str
        The id of the municipality group.
    title : str
        A municipality group title to search for. Filtered by substring matching.
    member_id : str
        The id of a municipality group member.
    member_title : str
        A municipality group member title to search for. Filtered by substring matching.

    Returns
    -------
    A list of dictionaries for the municipality groups matching the search criteria.
    """

    if id:
        return _make_request(BASE_URL + f"municipality_groups/{id}")

    url = BASE_URL + "municipality_groups"
    url_suffixes = []

    if title:
        url_suffixes.append(f"title={urllib.parse.quote(title)}")

    json_data = _make_request(url)

    if member_id:
        new_json_data = []
        for item in json_data:
            for member in item["members"]:
                if member["member_id"] == member_id:
                    new_json_data.append(item)
                    break
        json_data = new_json_data

    if member_title:
        new_json_data = []
        for item in json_data:
            for member in item["members"]:
                if member["member_title"] == member_title:
                    new_json_data.append(item)
                    break
        json_data = new_json_data

    return json_data


def get_ou(
    id: str = None,
    title: str = None,
    municipality: str = None,
) -> List[Dict]:
    """A function for retrieving and filtering organization units.

    Parameters
    ----------
    id : str
        The id of the organization unit.
    title : str
        An organization unit title to search for. Filtered by substring matching.
    municipality : str
        The id of a municipality to filter by.

    Returns
    -------
    A list of dictionaries for the organization units matching the search criteria.
    """

    if id:
        return _make_request(BASE_URL + f"ou/{id}")

    url = BASE_URL + "ou"
    url_suffixes = []

    if title:
        url_suffixes.append(f"title={urllib.parse.quote(title)}")

    if municipality:
        url_suffixes.append(f"municipality={urllib.parse.quote(municipality)}")

    json_data = _make_request(url)

    return json_data


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

    if not any([kpi, municipality]):
        raise ValueError(
            "At least two of the parameters kpi, municipality or year must be specified."
        )

    url = BASE_URL + "data"

    if kpi:
        if isinstance(kpi, list):
            url += f"/kpi/{','.join(kpi)}"
        else:
            url += f"/kpi/{kpi}"

    if municipality:
        if isinstance(municipality, list):
            url += f"/municipality/{','.join(municipality)}"
        else:
            url += f"/municipality/{municipality}"

    if isinstance(year, list):
        url += f"/year/{','.join(year)}"
    else:
        url += f"/year/{year}"

    return _make_request(url)


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

    if not any([kpi, ou]):
        raise ValueError(
            "At least two of the parameters kpi, ou or year must be specified."
        )

    url = BASE_URL + "oudata"

    if kpi:
        if isinstance(kpi, list):
            url += f"/kpi/{','.join(kpi)}"
        else:
            url += f"/kpi/{kpi}"

    if ou:
        if isinstance(ou, list):
            url += f"/ou/{','.join(ou)}"
        else:
            url += f"/ou/{ou}"

    if isinstance(year, list):
        url += f"/year/{','.join(year)}"
    else:
        url += f"/year/{year}"

    return _make_request(url)


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


# def main():
#     _save_non_data(folder_path="data")


# if __name__ == "__main__":
#     main()
