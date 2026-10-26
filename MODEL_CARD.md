# ChurnX model card

## Intended use

Customer-risk prioritization and academic demonstration on the IBM fictional Telco customer snapshot dataset. Scores support analyst review; they are not causal claims, retention guarantees, or cancellation-date forecasts.

## Selected model

`GradientBoostingClassifier`, version `churnx-v1.0.0`, trained on 2026-10-26 with scikit-learn 1.8.0. The saved joblib object includes numerical imputation/scaling, categorical imputation/one-hot encoding, and classification. The identifier and target are excluded from its 19 input fields.

## Selection and evaluation

Random seed 42; stratified 4,507 training / 1,127 validation / 1,409 test customers. Preprocessing fits inside each training fold. Five-fold ROC-AUC/PR-AUC comparison covers Dummy, Logistic Regression, Decision Tree, Random Forest, and Gradient Boosting. The selected family is tuned with a four-candidate cross-validation grid. Best parameters are 120 estimators, learning rate 0.07, and maximum depth 2.

Validation selects threshold 0.35 to maximize F1 among thresholds with recall at least 0.70. The saved model remains fitted to the training partition, retaining the exact pipeline evaluated on the test partition. It is not refitted on test or validation data after evaluation.

| Held-out test metric | Measured result |
|---|---:|
| ROC-AUC | 0.84398 |
| Average precision (PR-AUC) | 0.66263 |
| Recall | 0.72193 |
| Precision | 0.56485 |
| F1 | 0.63380 |
| Accuracy | 0.77857 |
| Brier score | 0.13615 |

The dummy ROC-AUC is 0.50. Test confusion matrix: TN 827, FP 208, FN 104, TP 270. All PRD gates pass: ROC-AUC ≥0.80, recall ≥0.70, F1 ≥0.55. Calibration and confusion-matrix plots are saved in `reports/evaluation.png`. Probabilities are uncalibrated classifier outputs; Brier score and the calibration plot are reported for inspection.

## Risk bands and classification

LOW: probability <0.30. MEDIUM: 0.30 ≤ probability <0.60. HIGH: probability ≥0.60. These display bands are stored separately from the binary classification threshold in model metadata. A medium-risk customer may be classified as likely to churn at threshold 0.35.

## Explainability

Global importance measures the validation ROC-AUC decrease from shuffling each raw feature, averaged across five repeats. Individual explanations replace one field with its training median/mode and measure the resulting probability decrease. The four largest positive differences are displayed. This is a local sensitivity measure, not SHAP, causal attribution, or an experimentally validated retention action. Independent field replacement can create unrealistic combinations, so it should be interpreted cautiously.

## Fairness and limitations

`models/metadata.json` reports test metrics and sample sizes by gender and senior-citizen status. Both demographic features are present in this academic baseline. Group disparities and whether demographics are necessary require further analysis before real customer use; these checks do not establish fairness.

The dashboard scores all 7,043 records, including training records. Those scores are useful for demonstration and exploration; only the held-out test metrics measure generalization. The fictional historical dataset may not represent other businesses or current customers. No live outcome monitoring, automated retraining, drift detector, authentication, or validated intervention policy is provided.

## Reproduction and lifecycle

Use Python 3.12 and `requirements.lock`, then `python -m ml.train`. The source checksum, split IDs, dependency version, threshold sweep, comparison results, and training reference profile are saved with the artifacts. Review the metrics before promoting a retrained artifact; the service loads artifacts once at startup and must be restarted after an approved model update. Monitoring aggregates reset on process restart; SQLite prediction history persists on the configured volume.
