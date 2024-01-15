# PyKolada
A Python wrapper for the statistical API Kolada.

## Overview

This Python package provides a lightweight wrapper for the Kolada API, which allows users to access and interact with key performance indicators (KPIs) for Swedish municipalities and organizational units. The Kolada database, maintained by RKA (Rådet för kommunal analys), offers a rich set of data, and this wrapper simplifies the process of querying and retrieving this information.

## Features

- Access to various endpoints like KPI, KPI groups, municipalities, municipality groups, and organizational units.
- Support for querying data based on different parameters such as ID, title, description, operating area, year, etc.
- Handling of pagination to fetch all relevant data.
- Customizable queries with support for filtering and specifying primary keys.

## Installation

This package requires Python 3.8 or higher.
You can install it using pip:

```bash
pip install pykolada
```

## Usage

### Importing the Module

```python
import pykolada
```

### Making Queries

You can make queries to different endpoints. For example, to query KPI data:

```python
kpi_data = pykolada.get_kpi(id='some_id', title='some_title')
```


## Endpoints
- `kpi`
- `kpi_groups`
- `municipality`
- `municipality_groups`
- `ou`
- `data`
- `oudata`

Each endpoint supports different parameters for querying. Please refer to the documentation for detailed information.


## Documentation and Examples
<!-- ToDo: Add documentation and examples. -->


## Planned Features
- Optional caching of data.
- Support for outputting data in CSV format (currently only original JSON is supported).
- Usage of additional custom filters that can be applied after the data has been retrieved.
- Support for the from_date parameter (limiting results data published after a certain date).


## License
MIT License


---