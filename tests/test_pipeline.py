from retisight_multi_ml.config import read_yaml


def test_pipeline_config_loads():
    cfg = read_yaml("configs/pipeline.yaml")
    assert cfg["random_seed"] == 20261010

