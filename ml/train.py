"""Run with: python -m ml.train [--download]. All preprocessing is fitted in folds."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                            confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from backend.schema import CustomerInput, NUMERIC, RAW_COLUMNS, risk_level

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
SEED = 42


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def load_data(path):
    data = pd.read_csv(path)
    expected = set(RAW_COLUMNS.values()) | {"customerID", "Churn"}
    if set(data.columns) != expected or data.empty:
        raise ValueError("Dataset must contain exactly the 21 IBM Telco columns")
    if data.customerID.isna().any() or not data.customerID.is_unique:
        raise ValueError("Customer identifiers must be present and unique")
    if data.Churn.isna().any() or not set(data.Churn).issubset({"Yes", "No"}):
        raise ValueError("Unexpected target values")
    data["TotalCharges"] = pd.to_numeric(data.TotalCharges, errors="coerce")
    data.loc[(data.tenure == 0) & data.TotalCharges.isna(), "TotalCharges"] = 0
    # Keep unknown numerical values for fold-local median imputation; audit all categories.
    for row in data.to_dict("records"):
        values = {api: row[raw] for api, raw in RAW_COLUMNS.items()}
        values = {key: (0 if pd.isna(value) else value) for key, value in values.items()}
        CustomerInput.model_validate(values)
    return data


def metrics(y, probabilities, threshold):
    labels = probabilities >= threshold
    return {"accuracy": float(accuracy_score(y, labels)), "precision": float(precision_score(y, labels, zero_division=0)),
            "recall": float(recall_score(y, labels)), "f1": float(f1_score(y, labels)),
            "roc_auc": float(roc_auc_score(y, probabilities)), "pr_auc": float(average_precision_score(y, probabilities)),
            "brier_score": float(brier_score_loss(y, probabilities)), "confusion_matrix": confusion_matrix(y, labels).tolist()}


def eda(data, reports):
    groups = {}
    target = data.Churn.eq("Yes")
    for column in ["Contract", "InternetService", "PaymentMethod", "TechSupport", "OnlineSecurity", "PaperlessBilling"]:
        grouped = data.assign(target=target).groupby(column).target.agg(["mean", "count"])
        groups[column] = [{"label": str(index), "value": round(float(row["mean"]) * 100, 2), "count": int(row["count"])} for index, row in grouped.iterrows()]
    buckets = pd.cut(data.tenure, [-1, 12, 24, 48, float("inf")], labels=["0–12 months", "13–24 months", "25–48 months", "49+ months"])
    grouped = pd.DataFrame({"tenure": buckets, "target": target}).groupby("tenure", observed=True).target.agg(["mean", "count"])
    groups["tenure"] = [{"label": str(index), "value": round(float(row["mean"]) * 100, 2), "count": int(row["count"])} for index, row in grouped.iterrows()]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, column in zip(axes[0], NUMERIC):
        for label, color in [("No", "#65a97f"), ("Yes", "#dd797b")]:
            ax.hist(data.loc[data.Churn == label, column].dropna(), bins=25, alpha=.65, label=label, color=color)
        ax.set_title(column); ax.legend(title="Churn")
    for ax, column in zip(axes[1], ["Contract", "InternetService", "TechSupport"]):
        rows = groups[column]
        ax.bar([r["label"] for r in rows], [r["value"] for r in rows], color="#65a97f")
        ax.set_title(f"Churn % by {column}"); ax.tick_params(axis="x", rotation=15)
    fig.tight_layout(); fig.savefig(reports / "eda.png", dpi=140); plt.close(fig)
    data[NUMERIC].corr().to_csv(reports / "numeric_correlations.csv")
    write_json(reports / "eda.json", {"records": len(data), "churn_rate": float(target.mean()), "missing": data.isna().sum().to_dict(), "groups": groups})
    return groups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    path = ROOT / "data/raw/Telco-Customer-Churn.csv"
    if not path.exists():
        if not args.download:
            parser.error("Dataset missing; run with --download")
        path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(SOURCE, timeout=60) as response:
            path.write_bytes(response.read())
    reports, models = ROOT / "reports", ROOT / "models"
    reports.mkdir(exist_ok=True); models.mkdir(exist_ok=True)
    data = load_data(path)
    groups = eda(data, reports)
    processed = ROOT / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)
    data.to_csv(processed / "churn_cleaned.csv", index=False)
    x, y = data[list(RAW_COLUMNS.values())], data.Churn.eq("Yes").astype(int)
    development, test = train_test_split(data.index, test_size=.2, stratify=y, random_state=SEED)
    train, validation = train_test_split(development, test_size=.2, stratify=y.loc[development], random_state=SEED)
    categorical = [name for name in x if name not in NUMERIC]
    preprocessing = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), categorical),
    ])
    candidates = {
        "DummyClassifier": DummyClassifier(strategy="prior"),
        "LogisticRegression": LogisticRegression(C=1, class_weight="balanced", max_iter=1500, random_state=SEED),
        "DecisionTreeClassifier": DecisionTreeClassifier(max_depth=5, min_samples_leaf=25, class_weight="balanced", random_state=SEED),
        "RandomForestClassifier": RandomForestClassifier(n_estimators=180, max_depth=9, min_samples_leaf=6, class_weight="balanced", n_jobs=1, random_state=SEED),
        "GradientBoostingClassifier": GradientBoostingClassifier(n_estimators=120, max_depth=2, learning_rate=.07, random_state=SEED),
    }
    comparison, fitted = [], {}
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    for name, classifier in candidates.items():
        pipeline = Pipeline([("preprocessing", clone(preprocessing)), ("classifier", classifier)])
        cv = cross_validate(pipeline, x.loc[train], y.loc[train], cv=folds, scoring={"roc_auc": "roc_auc", "pr_auc": "average_precision", "recall": "recall", "f1": "f1"}, n_jobs=1)
        pipeline.fit(x.loc[train], y.loc[train])
        fitted[name] = pipeline
        row = {"model": name, **{key[5:]: float(value.mean()) for key, value in cv.items() if key.startswith("test_")}}
        comparison.append(row)
        print(json.dumps(row), flush=True)
    ranked = sorted([row for row in comparison if row["model"] != "DummyClassifier"], key=lambda row: (row["roc_auc"], row["pr_auc"], row["recall"]), reverse=True)
    winner = ranked[0]["model"]
    pipeline = fitted[winner]
    grids = {
        "LogisticRegression": {"classifier__C": [.3, 1, 3]},
        "DecisionTreeClassifier": {"classifier__max_depth": [4, 5, 7]},
        "RandomForestClassifier": {"classifier__max_depth": [7, 9, 12]},
        "GradientBoostingClassifier": {"classifier__n_estimators": [80, 120], "classifier__learning_rate": [.05, .07]},
    }
    tuning = GridSearchCV(pipeline, grids[winner], scoring="roc_auc", cv=folds, n_jobs=1)
    tuning.fit(x.loc[train], y.loc[train])
    pipeline = tuning.best_estimator_
    validation_prob = pipeline.predict_proba(x.loc[validation])[:, 1]
    thresholds = [{"threshold": round(float(t), 2), **metrics(y.loc[validation], validation_prob, t)} for t in np.arange(.15, .76, .01)]
    acceptable = [row for row in thresholds if row["recall"] >= .70]
    choice = max(acceptable or thresholds, key=lambda row: row["f1"])
    threshold = choice["threshold"]
    # Preserve the exact fitted model/threshold evaluated below; do not refit on test data.
    test_prob = pipeline.predict_proba(x.loc[test])[:, 1]
    test_metrics = metrics(y.loc[test], test_prob, threshold)
    baseline = metrics(y.loc[test], fitted["DummyClassifier"].predict_proba(x.loc[test])[:, 1], .5)
    importance = permutation_importance(pipeline, x.loc[validation], y.loc[validation], scoring="roc_auc", n_repeats=5, random_state=SEED, n_jobs=1)
    features = sorted([{"label": column, "value": round(max(0, float(value)), 5)} for column, value in zip(x.columns, importance.importances_mean)], key=lambda item: item["value"], reverse=True)
    fairness = {}
    for column in ["gender", "SeniorCitizen"]:
        fairness[column] = {str(group): {"records": int(len(indices)), **metrics(y.loc[indices], pipeline.predict_proba(x.loc[indices])[:, 1], threshold)} for group, indices in x.loc[test].groupby(column).groups.items()}
    metadata = {
        "model_name": winner, "version": "churnx-v1.0.0", "task": "binary_classification",
        "training_date": datetime.now(timezone.utc).isoformat(), "dataset": "IBM Telco Customer Churn", "dataset_url": SOURCE,
        "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "records": len(data), "features": list(x.columns),
        "threshold": threshold, "risk_bands": {"low": .3, "high": .6}, "metrics": test_metrics,
        "baseline_metrics": baseline, "validation_metrics": choice, "comparison": comparison, "feature_importance": features,
        "split": {"train": len(train), "validation": len(validation), "test": len(test), "seed": SEED, "cv_folds": 5},
        "fairness": fairness, "sklearn_version": sklearn.__version__,
        "tuning": {"best_params": tuning.best_params_, "cv_roc_auc": float(tuning.best_score_), "candidates": len(tuning.cv_results_["params"])},
        "reference_profile": {column: float(x.loc[train, column].median()) if column in NUMERIC else x.loc[train, column].mode().iloc[0].item() if isinstance(x.loc[train, column].mode().iloc[0], np.generic) else x.loc[train, column].mode().iloc[0] for column in x},
        "performance_gates": {"roc_auc": test_metrics["roc_auc"] >= .8, "recall": test_metrics["recall"] >= .7, "f1": test_metrics["f1"] >= .55},
    }
    joblib.dump(pipeline, models / "churnx_pipeline.joblib", compress=3)
    write_json(models / "metadata.json", metadata)
    probabilities = pipeline.predict_proba(x)[:, 1]
    customers = [{"id": str(data.loc[index, "customerID"]), "tenure": int(row.tenure), "contract": row.Contract,
                  "monthlyCharges": float(row.MonthlyCharges), "internetService": row.InternetService, "techSupport": row.TechSupport,
                  "churnProbability": round(float(probability) * 100, 2), "risk": risk_level(probability).title()}
                 for (index, row), probability in zip(x.iterrows(), probabilities)]
    write_json(models / "dashboard.json", {"customers": customers, "groups": groups, "records": len(data), "churn_rate": round(float(y.mean()) * 100, 2), "feature_importance": features,
                                               "scoring_context": "All dataset rows scored, including training rows; model quality is measured only on the held-out test set."})
    write_json(reports / "splits.json", {"train": data.loc[train, "customerID"].tolist(), "validation": data.loc[validation, "customerID"].tolist(), "test": data.loc[test, "customerID"].tolist()})
    write_json(reports / "thresholds.json", thresholds)
    observed, predicted = calibration_curve(y.loc[test], test_prob, n_bins=10, strategy="quantile")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(predicted, observed, marker="o", label=winner)
    axes[0].plot([0, 1], [0, 1], linestyle="--", color="grey")
    axes[0].set(xlabel="Mean predicted probability", ylabel="Observed churn fraction", title="Held-out calibration")
    axes[1].imshow(test_metrics["confusion_matrix"], cmap="Greens")
    axes[1].set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Stay", "Churn"], yticklabels=["Stay", "Churn"], xlabel="Predicted", ylabel="Actual", title="Test confusion matrix")
    for i in range(2):
        for j in range(2):
            axes[1].text(j, i, str(test_metrics["confusion_matrix"][i][j]), ha="center", va="center")
    fig.tight_layout(); fig.savefig(reports / "evaluation.png", dpi=140); plt.close(fig)
    print(json.dumps({"selected": winner, "threshold": threshold, "test": test_metrics, "gates": metadata["performance_gates"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
