from retisight_multi_ml.normalization import clean_column_name, normalize_eye, path_parts


def test_path_parts_extracts_visit_eye_and_study_folder():
    parsed = path_parts("/TREX DME/GILA/0201GOD/V1/OD/TREXJ_000000.tif")
    assert parsed["arm"] == "GILA"
    assert parsed["study_folder"] == "0201GOD"
    assert parsed["visit"] == "V1"
    assert parsed["eye_laterality"] == "OD"


def test_path_parts_handles_prime_layout():
    parsed = path_parts("/Prime_FULL/02-010/W0/OD/0.tif")
    assert parsed["trial"] == "Prime_FULL"
    assert parsed["study_folder"] == "02-010"
    assert parsed["visit"] == "W0"
    assert parsed["eye_laterality"] == "OD"


def test_column_and_eye_normalization():
    assert clean_column_name("Fluid (IRF)") == "fluid_irf"
    assert normalize_eye("right") == "OD"
