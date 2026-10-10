# MULTI-03/05/06 Recovery Decision

## Linkage

Decision: `TRAJECTORY_SUPPORTED_CANDIDATES_REQUIRE_EXTERNAL_CONFIRMATION`

The investigation found 56 trajectory-supported candidate links with no BCVA/CST mismatches across overlapping visits. These links remain candidate links, not externally verified links.

## Outcome Timing

Decision: `NOT_FEASIBLE_WITHOUT_AUTHORITATIVE_CROSSWALK`

The Vision sheets contain 165 ETDRS cells in the 150-210 day window, but no patient/eye identifiers and no authoritative crosswalk to OLIVES eyes.

## Alternative Endpoints

Decision: `DESCRIPTIVE_ONLY_REQUIRES_CLINICAL_APPROVAL`

OLIVES-native visit-index endpoints can be described, but must not be labelled six-month outcomes and must not enable modeling without clinical approval.

## Unresolved Data-Owner Questions

1. Provide an authoritative row-level crosswalk from OLIVES Patient_ID/Eye_ID/path visit to OCT-DME StudyID and study eye.
2. Confirm whether the OLIVES folder token is guaranteed to equal OCT-DME StudyID for every TREX-DME eye.
3. Provide patient/eye identifiers for TREX Vision and GILA Vision rows, or confirm an official row-order mapping.
4. Provide actual visit dates or elapsed study days for OLIVES TREX-DME V1-V27 visits.
5. Provide eye-level injection dates/counts before the intended prediction endpoint.
6. Confirm the clinically approved response endpoint and time zero.
7. Confirm whether visit-index endpoints such as V13 or V22 are clinically meaningful descriptive endpoints.