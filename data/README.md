# Dataset provenance

Source: [IBM Telco Customer Churn sample](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv).

- `raw/Telco-Customer-Churn.csv` is the unchanged downloaded source: 7,043 customer snapshots and 21 columns.
- SHA-256: `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91`.
- `processed/churn_cleaned.csv` contains a separate cleaned copy; it is not globally encoded or scaled.
- `../reports/eda.json`, `eda.png`, and `numeric_correlations.csv` contain the reproducible exploratory analysis.
- `../reports/splits.json` records the exact train, validation and test customer identifiers.

This fictional telecom sample is a snapshot dataset. ChurnX estimates risk associated with snapshot characteristics; it does not forecast a cancellation date or a calibrated 30-day outcome. Source charges are USD; no currency conversion is applied.

Run `python -m ml.train --download` to fetch the source if absent, validate it, regenerate reports, compare classifiers, and serialize the selected pipeline. Existing raw data is never overwritten by that command.
