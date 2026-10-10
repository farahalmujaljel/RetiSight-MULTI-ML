from retisight_multi_ml.config import read_yaml


def test_pipeline_config_loads():
    cfg = read_yaml("configs/pipeline.yaml")
    assert cfg["random_seed"] == 20261010


def test_cli_exposes_recovery_investigation_command():
    from retisight_multi_ml.cli import main  # noqa: PLC0415

    assert callable(main)
