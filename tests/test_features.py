from retisight_multi_ml.oct_aggregation import aggregate_baseline_oct


def test_oct_aggregation_uses_baseline_only(synthetic_biomarkers):
    out = aggregate_baseline_oct(synthetic_biomarkers)
    assert len(out) == 1
    row = out.iloc[0]
    assert row["irf_present"] == 1
    assert row["irf_positive_scan_count"] == 1
    assert row["number_of_annotated_scans"] == 2

