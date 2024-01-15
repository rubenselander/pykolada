import requests
import urllib.parse
from typing import Any, Dict, List, Union
import json
import os

# Configuration
BASE_URL = "http://api.kolada.se/v2/"
ENDPOINTS = {
    "kpi": {
        "api_parameters": ["id", "title", "description", "operating_area"],
    }
}


# Helper Functions
def build_url(endpoint: str, params: Dict[str, Any]) -> str:
    """
    Constructs a URL for the API request.
    """
    url = BASE_URL + endpoint
    if "id" in params and params["id"]:
        url += f"/{params['id']}"
        del params["id"]

    query_string = "&".join(
        f"{key}={urllib.parse.quote(str(value))}"
        for key, value in params.items()
        if value is not None
    )
    return f"{url}?{query_string}" if query_string else url


def filter_results(data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """
    Filters the API response data based on given criteria.
    """
    for key, value in filters.items():
        if value is not None:
            data = [item for item in data if item.get(key) == value]
    return data


def make_request(url: str) -> List[Dict]:
    """
    Makes an API request and handles pagination.
    """
    all_data = []
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: HTTP {response.status_code}")
        data = response.json()
        all_data.extend(data.get("values", []))
        url = data.get("next_page")
    return all_data


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


# Main API Function
def api_query(endpoint: str, **kwargs) -> List[Dict]:
    """
    Main function to handle API queries.
    """
    if endpoint not in ENDPOINTS:
        raise ValueError(
            f"Invalid endpoint: {endpoint}. Valid endpoints are: {list(ENDPOINTS.keys())}"
        )

    valid_params = {
        param: kwargs.get(param) for param in ENDPOINTS[endpoint] if param in kwargs
    }
    url = build_url(endpoint, valid_params)
    data = make_request(url)

    # Filter results if applicable
    filter_keys = set(ENDPOINTS[endpoint]) - set(valid_params)
    filter_criteria = {key: kwargs.get(key) for key in filter_keys}
    return filter_results(data, filter_criteria)


# Example Usage
try:
    kpi_data = api_query("kpi", title="Health", has_ou_data=True)
    print(kpi_data)
except Exception as e:
    print(f"Error: {e}")
