# Vietnam metadata mapping supplement

Release: 2026-10-16. Scope: metadata associations in the April-labelled Vietnam datasets. These are the dictionaries extracted from the retained analysis source, not an independently verified ownership or physical-location registry.

## Files
- asn_to_operator.csv: ASN-to-operator labels.
- operator_name_aliases.csv: fallback organization-name aliases.
- province_mapping.csv: archived region-name mappings, also used as a final city fallback.
- city_mapping.csv: city-name fallback mappings.
- mapping_rules.py: exact normalization and lookup functions extracted from the analysis source; runs offline and makes no API calls.
- metadata_provenance.json: source hashes, fields, round labels and query-date availability.

## Application order
Keys undergo NFKD normalization, removal of combining marks, conversion of Đ/đ to D/d, replacement of non-ASCII-alphanumeric characters with spaces, lowercasing and whitespace collapse.

Operator mapping first checks the stripped ASN string, then the normalized organization name. Unmatched organization names retain their original stripped value; empty names become (empty).

Province mapping first checks normalized region_name in province_mapping, then normalized city_name in city_mapping, then city_name in province_mapping. If none matches, the result is (unmapped). All entries are preserved exactly, including aliases that are redundant after normalization. This is a 34-province analytical grouping, not independent location validation. CSV row counts are mapping entries, not numbers of distinct provinces.

## Query dates and metadata editions
The retained IP2Location CSVs contain no query timestamp or database-edition field. Exact query start/end dates and database editions are therefore recorded as null (not recorded). Round labels, file modification dates and this release date must not be interpreted as API query dates. API access is a paid subscription as confirmed by the authors.

Publishing mappings improves reproducibility of label grouping. It does not validate the original metadata against routing/geolocation evidence, establish service ownership, resolve anycast, or provide per-ASN routed-space or active-server baselines.

## Author-reported timing workflow
The authors state that IP2Location queries follow scanning. The manifest records the latest connection close timestamp as a preceding reference and its UTC date as an explicitly workflow-derived estimate. Same-day query execution is not independently verified; actual query start/end timestamps remain null.
