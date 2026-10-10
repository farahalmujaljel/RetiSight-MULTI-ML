from pathlib import Path

import pandas as pd

from retisight_multi_ml.config import SourceConfig
from retisight_multi_ml.inventory import inventory_sources


def test_inventory_records_csv_shape(tmp_path: Path):
    source = tmp_path / "synthetic.csv"
    pd.DataFrame({"Patient_ID": [1, 2], "value": [3, 4]}).to_csv(source, index=False)
    manifest = inventory_sources(
        [SourceConfig("synthetic", "synthetic.csv", source, "local", "unit test")], tmp_path / "out"
    )
    assert manifest[0]["inspection_status"] == "INSPECTED"
    assert manifest[0]["tables"][0]["row_count"] == 2

