import pykolada
import json


def test_get_data():
    kpi_id = "N00011"
    data = pykolada.get_data(kpi_id=kpi_id)
    print(json.dumps(data, indent=4))
