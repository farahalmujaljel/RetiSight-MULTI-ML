from pathlib import Path

from retisight_multi_ml.modeling import write_modeling_omission


def test_modeling_omission_is_explicit(tmp_path: Path):
    write_modeling_omission(tmp_path, "Synthetic test reason.")
    text = (tmp_path / "modeling_not_performed.md").read_text()
    assert "CONDITIONAL_NOT_APPLICABLE" in text
