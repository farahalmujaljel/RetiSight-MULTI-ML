from pathlib import Path

from retisight_multi_ml.modeling import write_modeling_omission
from retisight_multi_ml.olives_native_outcomes import visit_elapsed_days


def test_modeling_omission_is_explicit(tmp_path: Path):
    write_modeling_omission(tmp_path, "Synthetic test reason.")
    text = (tmp_path / "modeling_not_performed.md").read_text()
    assert "CONDITIONAL_NOT_APPLICABLE" in text


def test_olives_native_visit_timing_does_not_infer_sequence_labels():
    assert visit_elapsed_days("W24") == 168
    assert visit_elapsed_days("V22") is None
    assert visit_elapsed_days("V1") is None
