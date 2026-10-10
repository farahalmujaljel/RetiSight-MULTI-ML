# OLIVES-Native Feature Manifest

This manifest lists supported features and temporal predictor eligibility.

- baseline_bcva_etdrs: source=OLIVES Clinical_Data_Images.xlsx; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- baseline_cst_um: source=OLIVES Clinical_Data_Images.xlsx; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- irf_present: source=OLIVES Biomarker_Clinical_Data_Images.csv; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- srf_present: source=OLIVES Biomarker_Clinical_Data_Images.csv; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- dril_present: source=OLIVES Biomarker_Clinical_Data_Images.csv; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- hrf_present: source=OLIVES Biomarker_Clinical_Data_Images.csv; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- ez_disruption_present: source=OLIVES Biomarker_Clinical_Data_Images.csv; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- number_of_annotated_scans: source=OLIVES Biomarker_Clinical_Data_Images.csv; time=V1 baseline visit label; role=baseline_predictor; eligible=True; missingness_recorded_in=row-level ignored export
- endpoint_bcva: source=OLIVES Clinical_Data_Images.xlsx; time=post-baseline visit-index endpoint; role=outcome_candidate; eligible=False; missingness_recorded_in=row-level ignored export
- anti_vegf_injection_count_prior_12mo: source=future hospital integration; time=requires dated treatment history; role=treatment_history; eligible=False; missingness_recorded_in=row-level ignored export