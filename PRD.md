# ChurnX
## AI-Powered Customer Churn Intelligence Platform

**Document Type:** Product Requirements Document  
**Version:** 1.0  
**Status:** Development Specification  
**Project Type:** Artificial Intelligence / Machine Learning  
**Primary ML Task:** Binary Classification  
**Target Deployment:** Web Application  

### Team

- **Amogh Sharma — S24CSEU1212**
- **Ayush Pal — S24CSEU0352**
- **Aditya Veer Singh — S24CSEU1195**

---

# 1. Executive Summary

ChurnX is an AI-powered customer churn intelligence platform designed to identify customers who are at risk of discontinuing a service.

Customer churn is a major problem for subscription-based businesses such as telecommunications companies, SaaS products, streaming platforms, financial services, online marketplaces, internet providers and membership platforms. Companies frequently react only after a customer leaves, at which point retention becomes significantly more difficult.

ChurnX aims to shift this process from reactive to predictive.

The platform will use historical customer information to train supervised machine-learning models capable of estimating the probability that an existing customer will churn.

Instead of returning only a binary result such as:

`Churn = Yes`

the product will expose a more useful result:

`Churn Probability = 78.4%`

and convert this into an understandable business risk classification:

`HIGH RISK`

The platform will additionally surface important factors associated with the prediction, enabling a user to understand why a customer may be at risk.

The complete system will include:

1. Customer churn dataset
2. Data cleaning pipeline
3. Exploratory data analysis
4. Feature preprocessing
5. Multiple ML model experiments
6. Model evaluation
7. Best-model selection
8. Model serialization
9. FastAPI prediction backend
10. React-based product dashboard
11. Prediction history
12. Customer risk visualization
13. Explainability layer
14. Dockerized backend
15. Cloud deployment
16. Basic model monitoring

The final result should behave like a small production ML product rather than simply a Jupyter Notebook.

---

# 2. Product Vision

### Vision Statement

> ChurnX should allow a business user to identify customers who are likely to leave, understand the major factors contributing to their risk, and prioritize retention efforts before churn occurs.

The product should answer three questions:

### 1. Who is likely to churn?

ChurnX produces a churn probability for each customer.

### 2. How serious is the risk?

Customers are grouped into risk categories.

Example:

- Low Risk
- Medium Risk
- High Risk

### 3. Why is the customer considered risky?

ChurnX surfaces important contributing variables such as:

- short tenure
- month-to-month contract
- high monthly charges
- lack of technical support
- payment method
- service configuration

---

# 3. Problem Statement

Modern subscription-based businesses operate in environments where customers can easily change providers when they encounter poor experiences, pricing concerns, insufficient support, or better alternatives.

Customer churn directly affects recurring revenue, customer lifetime value and long-term business growth.

Traditional churn management frequently relies on retrospective analysis. Organizations identify churn patterns only after customers have already discontinued their service. Such an approach provides limited opportunities for proactive intervention.

ChurnX addresses this challenge through an AI/ML-based customer churn prediction system.

The system analyzes historical customer information including tenure, subscribed services, contract characteristics, billing information, payment method and service-related attributes. A supervised machine-learning model learns patterns associated with previously churned customers and applies these patterns to existing customers.

The platform estimates each customer's probability of churn and categorizes the customer into an appropriate risk level.

Beyond prediction, ChurnX aims to improve interpretability by identifying the factors most strongly associated with each prediction.

The objective is therefore not merely to classify customers as churned or retained, but to create a complete customer-risk intelligence platform capable of supporting proactive retention decisions.

---

# 4. Problem Classification

ChurnX is primarily a:

## Supervised Binary Classification Problem

Target:

```text
Churn = 0 → Customer remains

Churn = 1 → Customer leaves
```

The model learns the mapping:

```text
Customer Features
        ↓
Machine Learning Model
        ↓
Probability of Churn
        ↓
Churn / No Churn
```

Example:

```text
Customer #CX1047

Model Output Probability
0.8237

Converted Probability
82.37%

Classification
Likely to Churn

Risk
HIGH
```

Although the product displays percentages, the underlying problem is not traditional regression.

The probability is produced by a classification model.

---

# 5. Core Product Objectives

ChurnX must:

1. Build a reproducible customer churn dataset pipeline.
2. Identify variables associated with customer churn.
3. Train multiple supervised classification algorithms.
4. Compare models using appropriate evaluation metrics.
5. Select a final production model based on validation performance.
6. Generate churn probabilities instead of only yes/no outputs.
7. Convert probabilities into human-readable risk categories.
8. Provide meaningful explanations for model predictions.
9. Expose the model through a REST API.
10. Create a product-style dashboard for interacting with predictions.
11. Support individual customer predictions.
12. Support future batch customer scoring.
13. Store or display prediction history.
14. Deploy the frontend and backend independently.
15. maintain identical preprocessing during training and inference.

---

# 6. Non-Goals for Version 1

The first release will intentionally avoid unnecessary complexity.

V1 will NOT attempt to:

- predict the exact date a customer will churn
- automatically contact customers
- execute retention offers
- integrate with live telecom infrastructure
- continuously retrain itself
- use deep neural networks
- ingest streaming event data
- claim causal relationships
- provide financial guarantees
- replace CRM systems

These can become later extensions.

---

# 7. Target Users

## Primary User — Retention Analyst

Needs to identify customers with high churn probability.

Uses:

- customer overview
- risk scores
- high-risk customer list
- prediction explanations

---

## Secondary User — Business Manager

Needs to understand:

- percentage of customers at risk
- potential retention opportunities
- common churn drivers
- overall churn patterns

---

## Technical User — Data Scientist

Needs:

- model version
- features
- performance metrics
- prediction confidence
- training metadata

---

# 8. Dataset Strategy

## 8.1 Primary Dataset

The MVP will use the:

### IBM Telco Customer Churn Dataset

IBM provides a public Telco churn sample and an associated end-to-end churn example. The commonly used CSV contains approximately **7,043 customer records and 21 raw columns**.

The dataset represents customers of a fictional telecommunications service.

Each row represents one customer.

The target column is:

```text
Churn
```

Values:

```text
Yes
No
```

Converted internally to:

```text
Yes → 1
No  → 0
```

The dataset is a **customer snapshot rather than a longitudinal monthly history**, which is important: ChurnX V1 should be described as predicting churn risk from snapshot characteristics, not as forecasting the exact month in which a customer will leave.

---

# 9. Raw Dataset Schema

## Identifier

### customerID

Unique customer identifier.

This field must NOT be used as a predictive feature.

Reason:

The identifier itself contains no meaningful behavioral information and could cause meaningless associations.

---

# 10. Demographic Features

### gender

Possible values:

```text
Male
Female
```

### SeniorCitizen

```text
0
1
```

### Partner

```text
Yes
No
```

### Dependents

```text
Yes
No
```

---

# 11. Account Features

### tenure

Number of months the customer has remained with the company.

Example:

```text
1
12
37
68
```

This is expected to be an important churn-related feature.

---

# 12. Service Features

### PhoneService

```text
Yes
No
```

### MultipleLines

```text
Yes
No
No phone service
```

### InternetService

```text
DSL
Fiber optic
No
```

### OnlineSecurity

### OnlineBackup

### DeviceProtection

### TechSupport

### StreamingTV

### StreamingMovies

These commonly contain:

```text
Yes
No
No internet service
```

---

# 13. Contract and Billing Features

### Contract

```text
Month-to-month
One year
Two year
```

### PaperlessBilling

```text
Yes
No
```

### PaymentMethod

Possible categories include:

```text
Electronic check
Mailed check
Bank transfer (automatic)
Credit card (automatic)
```

### MonthlyCharges

Continuous numerical value.

### TotalCharges

Total historical charges accumulated by the customer.

The original data stores `TotalCharges` in a way that requires numeric conversion and contains a small number of blank values associated with new customers, so this field must be explicitly cleaned before training.

---

# 14. Target Variable

### Churn

```text
Yes → Customer churned
No  → Customer remained
```

Training representation:

```text
Yes = 1
No  = 0
```

---

# 15. Important Dataset / Frontend Alignment Decision

The original ChurnX frontend prototype contained fields such as:

```text
Usage Frequency
Support Tickets
Late Payments
```

These fields are useful conceptually, but they do **not exist in the base IBM Telco dataset**.

Therefore they must NOT be used by the real V1 model unless an additional dataset is introduced.

### V1 production form should instead use real dataset fields such as:

```text
Tenure
Monthly Charges
Total Charges
Contract Type
Internet Service
Tech Support
Online Security
Payment Method
Paperless Billing
Phone Service
Streaming Services
```

The richer behavioral variables can later be introduced into ChurnX V2.

This prevents a common ML project mistake:

> Training a model on one schema while pretending the frontend collects another.

---

# 16. Phase 2 Dataset Extension

ChurnX may later introduce an enriched synthetic or independently sourced dataset containing:

- login frequency
- service usage
- support tickets
- complaint count
- payment delays
- failed payments
- customer satisfaction
- NPS score
- session frequency
- usage trend
- days since last activity

These features may make the product more realistic.

However:

**Synthetic fields should never be presented as real IBM dataset variables.**

---

# 17. Data Directory Strategy

Recommended structure:

```text
data/
│
├── raw/
│   └── Telco-Customer-Churn.csv
│
├── processed/
│   └── churn_processed.csv
│
└── README.md
```

The raw dataset should remain unchanged.

All transformations should produce separate processed data.

---

# 18. Data Validation

Before model training, the pipeline must verify:

- dataset exists
- expected columns exist
- target column exists
- customer IDs are unique
- no unexpected target categories exist
- numerical fields contain valid ranges
- categorical fields contain known values
- missing values are accounted for

Example validation:

```text
Rows > 0

Churn ∈ {Yes, No}

tenure >= 0

MonthlyCharges >= 0
```

---

# 19. Data Cleaning Pipeline

## Step 1 — Load CSV

Using:

```text
pandas
```

---

## Step 2 — Remove unnecessary identifiers

Drop:

```text
customerID
```

from model inputs.

Retain it separately if customer-level predictions need identifiers.

---

## Step 3 — Convert target

```text
Yes → 1
No → 0
```

---

## Step 4 — Convert TotalCharges

Convert from text/object representation to numeric.

Invalid values become:

```text
NaN
```

Then handle these values explicitly.

For customers with:

```text
tenure = 0
```

a reasonable transformation is:

```text
TotalCharges = 0
```

because the customer has not accumulated historical charges.

The final choice must be documented.

---

## Step 5 — Handle Missing Values

Numerical variables:

```text
Median imputation
```

if missing data exists.

Categorical variables:

```text
Most frequent category
```

or:

```text
Unknown
```

depending on the feature.

---

# 20. Exploratory Data Analysis

EDA must be completed before model training.

The project should examine:

### Target Distribution

```text
Churn
├── No
└── Yes
```

---

### Numerical Feature Analysis

Analyze:

```text
tenure
MonthlyCharges
TotalCharges
```

against churn.

Visualizations:

- histograms
- box plots
- distributions
- churn-group comparisons

---

### Categorical Analysis

Analyze churn rate across:

- Contract
- InternetService
- PaymentMethod
- TechSupport
- OnlineSecurity
- PaperlessBilling

---

### Correlation Analysis

For numerical features:

```text
Correlation matrix
```

---

### Class Balance

The public dataset is moderately imbalanced, with roughly one-quarter of customers labelled as churn. Therefore raw accuracy alone is not a sufficient evaluation metric.

---

# 21. Data Leakage Prevention

This is critical.

ChurnX must ensure that information unavailable at prediction time is not included during model training.

Examples of leakage:

```text
Future cancellation date
Post-cancellation information
A manually calculated "Churn Score"
Outcome-derived columns
```

Any feature directly generated from the churn outcome must be removed.

The model must only receive variables that would realistically exist before churn is known.

---

# 22. Train / Validation / Test Strategy

Recommended initial split:

```text
70% Training
15% Validation
15% Testing
```

Alternative:

```text
80% Training
20% Testing
```

plus stratified cross-validation within training.

Preferred approach:

```text
Train/Test Split
+
5-Fold Stratified Cross Validation
```

Use:

```python
stratify=y
```

when splitting.

This preserves approximately the same churn proportion across datasets.

---

# 23. Preprocessing Architecture

Preprocessing must be contained within the trained ML pipeline.

Do NOT separately preprocess the entire dataset before splitting.

That could cause leakage.

Recommended architecture:

```text
Raw Features
     ↓
ColumnTransformer
     ↓
Numerical Pipeline
     +
Categorical Pipeline
     ↓
Classifier
```

---

# 24. Numerical Preprocessing

For:

```text
tenure
MonthlyCharges
TotalCharges
```

Recommended:

```text
SimpleImputer
StandardScaler
```

Scaling is particularly relevant for models such as Logistic Regression.

Tree-based models do not require scaling, but keeping preprocessing consistent simplifies the system.

---

# 25. Categorical Preprocessing

Use:

```text
OneHotEncoder
```

with unseen-category handling.

One-hot encoding converts categorical values into numeric indicator columns suitable for many standard ML estimators.

Recommended configuration:

```python
OneHotEncoder(handle_unknown="ignore")
```

This avoids inference failures if an unseen category is received.

---

# 26. Feature Engineering

V1 should remain interpretable.

Useful engineered variables may include:

### Number of subscribed services

```text
service_count
```

Count active services such as:

- online security
- online backup
- device protection
- technical support
- streaming TV
- streaming movies

---

### Average historical monthly spend

Possible:

```text
TotalCharges / max(tenure, 1)
```

---

### Tenure Bucket

Example:

```text
0–12 months
13–24 months
25–48 months
49+ months
```

---

### Has Support

Derived from:

```text
TechSupport
```

---

### Long-Term Contract

```text
Contract != Month-to-month
```

---

# 27. Model Candidates

ChurnX should compare multiple algorithms rather than selecting one beforehand.

---

# 28. Model 0 — Dummy Classifier

Purpose:

Establish a naive baseline.

Example:

```text
Always predict majority class
```

Any production model must outperform this baseline.

---

# 29. Model 1 — Logistic Regression

Purpose:

Interpretable baseline classification model.

Advantages:

- simple
- fast
- explainable
- probability output
- good baseline for tabular classification

This should be the first legitimate ML model trained.

---

# 30. Model 2 — Decision Tree

Advantages:

- intuitive
- easy to visualize
- handles nonlinear relationships

Risks:

- overfitting
- unstable without pruning

Useful primarily for comparison and explanation.

---

# 31. Model 3 — Random Forest

Strong MVP candidate.

Advantages:

- handles nonlinear relationships
- robust
- handles mixed relationships well
- provides feature importance
- less likely to overfit than one decision tree

IBM's archived Telco churn example itself includes a Random Forest-based training flow, making it a reasonable project choice.

---

# 32. Model 4 — Gradient Boosting

Possible choices:

```text
HistGradientBoostingClassifier
XGBoost
LightGBM
```

For a simpler dependency stack, use Scikit-learn Gradient Boosting or HistGradientBoosting.

For a stronger advanced experiment, add:

```text
XGBoost
```

as an optional model.

---

# 33. Recommended Model Experiment Set

Minimum:

```text
DummyClassifier
LogisticRegression
DecisionTreeClassifier
RandomForestClassifier
```

Better:

```text
DummyClassifier
LogisticRegression
RandomForestClassifier
GradientBoostingClassifier
XGBoost
```

---

# 34. Model Evaluation Metrics

ChurnX must NOT evaluate models based only on accuracy.

Use:

### Accuracy

Overall percentage correctly classified.

Useful but insufficient.

---

### Precision

Of customers predicted as churners:

> How many actually churned?

---

### Recall

Of all actual churners:

> How many did the model successfully identify?

This is particularly important for ChurnX.

Missing an at-risk customer could mean losing the opportunity to intervene.

---

### F1 Score

Balances:

```text
Precision
+
Recall
```

---

### ROC-AUC

Measures the ability of the classifier to rank positive cases above negative cases across thresholds.

---

### PR-AUC

Useful when positive cases are less common than negative cases.

---

### Confusion Matrix

```text
                 Predicted
              Stay     Churn

Actual Stay     TN       FP

Actual Churn    FN       TP
```

---

# 35. Model Selection Priority

Recommended selection order:

1. ROC-AUC / PR-AUC
2. Recall
3. F1
4. Precision
5. Probability quality
6. Explainability
7. Inference speed

Accuracy should be reported but should not dominate selection.

---

# 36. Target Performance Gates

These are **development targets**, not fabricated results.

Actual scores must be obtained through training.

Suggested target:

```text
ROC-AUC ≥ 0.80

Recall ≥ 0.70

F1 ≥ 0.55
```

If the model performs below these thresholds, investigate:

- preprocessing
- feature engineering
- class weighting
- hyperparameters
- threshold selection

---

# 37. Handling Class Imbalance

Possible methods:

### Class Weights

Preferred initial approach.

Example:

```python
class_weight="balanced"
```

---

### SMOTE

Optional experiment.

Important:

SMOTE must only be applied to training folds.

Never oversample before train/test splitting.

---

# 38. Hyperparameter Tuning

Use:

```text
GridSearchCV
```

or:

```text
RandomizedSearchCV
```

Example Random Forest parameters:

```text
n_estimators
max_depth
min_samples_split
min_samples_leaf
max_features
class_weight
```

Example Logistic Regression parameters:

```text
C
penalty
class_weight
```

Use stratified cross-validation.

---

# 39. Prediction Probability

The final classifier must expose:

```python
predict_proba()
```

Example:

```text
Probability Stay  = 0.214

Probability Churn = 0.786
```

Frontend receives:

```text
78.6%
```

---

# 40. Classification Threshold

Default:

```text
0.50
```

However the threshold should be tuned using the validation dataset.

Example:

At threshold 0.50:

```text
Precision = 0.62
Recall    = 0.71
```

At threshold 0.40:

```text
Precision = 0.55
Recall    = 0.81
```

If retention teams prefer identifying more at-risk customers, the lower threshold may be preferable.

Threshold selection should therefore be treated as a business decision, not merely a mathematical default.

---

# 41. Risk Categories

Product-level risk bands can initially be:

```text
0%  – 30% → LOW
30% – 60% → MEDIUM
60% – 100% → HIGH
```

These should remain configurable.

Important:

Risk category thresholds are a UX feature.

The actual binary classifier decision threshold may be separately tuned.

---

# 42. Probability Calibration

Random Forest probabilities may not always behave like perfectly calibrated real-world probabilities.

Optional advanced step:

```text
CalibratedClassifierCV
```

Evaluate calibration using:

```text
Calibration Curve
Brier Score
```

This would substantially strengthen the ML quality of the project.

---

# 43. Explainable AI

The product must attempt to answer:

> Why is this customer's churn risk high?

V1 options:

### Logistic Regression Coefficients

Simple global interpretability.

### Random Forest Feature Importance

Shows globally important features.

### Permutation Importance

Better model-independent global explanation.

### SHAP

Advanced optional implementation.

SHAP can provide customer-specific explanations such as:

```text
Churn Probability: 82%

Primary contributors:

+ Month-to-month contract
+ Short tenure
+ High monthly charges
+ No technical support
- Automatic payment
```

---

# 44. Model Artifact

Once selected, the entire pipeline should be serialized.

Recommended:

```text
joblib
```

File:

```text
models/
└── churnx_pipeline.joblib
```

The saved object should contain:

```text
Preprocessing
+
Feature transformations
+
Final classifier
```

This is extremely important.

Do not save only the classifier while recreating preprocessing manually in the backend.

---

# 45. Model Metadata

Save:

```text
models/
├── churnx_pipeline.joblib
└── metadata.json
```

Example:

```json
{
  "model_name": "RandomForestClassifier",
  "version": "1.0.0",
  "dataset": "IBM Telco Customer Churn",
  "training_date": "YYYY-MM-DD",
  "roc_auc": 0.0,
  "recall": 0.0,
  "precision": 0.0,
  "f1": 0.0,
  "threshold": 0.5
}
```

Actual values are inserted after training.

---

# 46. Backend Architecture

Recommended:

```text
FastAPI
```

Architecture:

```text
React Frontend
       ↓
 HTTP Request
       ↓
FastAPI Backend
       ↓
Pydantic Validation
       ↓
Model Pipeline
       ↓
predict_proba()
       ↓
Risk Calculation
       ↓
JSON Response
       ↓
React Dashboard
```

---

# 47. API Endpoints

## Health

```text
GET /health
```

Response:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

# 48. Model Information

```text
GET /model-info
```

Response:

```json
{
  "model": "RandomForestClassifier",
  "version": "1.0.0",
  "task": "binary_classification"
}
```

---

# 49. Individual Prediction

```text
POST /predict
```

Example request:

```json
{
  "gender": "Female",
  "senior_citizen": 0,
  "partner": "Yes",
  "dependents": "No",
  "tenure": 12,
  "phone_service": "Yes",
  "multiple_lines": "No",
  "internet_service": "Fiber optic",
  "online_security": "No",
  "online_backup": "Yes",
  "device_protection": "No",
  "tech_support": "No",
  "streaming_tv": "Yes",
  "streaming_movies": "Yes",
  "contract": "Month-to-month",
  "paperless_billing": "Yes",
  "payment_method": "Electronic check",
  "monthly_charges": 89.50,
  "total_charges": 1074.00
}
```

---

# 50. Prediction Response

```json
{
  "prediction": 1,
  "churn_probability": 0.8124,
  "churn_percentage": 81.24,
  "risk_level": "HIGH",
  "model_version": "1.0.0"
}
```

Optional:

```json
{
  "top_factors": [
    "Month-to-month contract",
    "Short tenure",
    "No tech support"
  ]
}
```

---

# 51. Batch Prediction

Phase 1.5:

```text
POST /predict/batch
```

Input:

```text
CSV
```

Output:

```text
Scored CSV
```

Additional columns:

```text
churn_probability
risk_level
prediction
```

This would make ChurnX substantially more useful.

---

# 52. Backend Validation

Pydantic schemas should reject:

```text
negative tenure
negative charges
invalid contract names
invalid payment types
missing required fields
```

Example:

```text
tenure >= 0
monthly_charges >= 0
total_charges >= 0
```

---

# 53. Frontend Technology

Recommended:

```text
React
Vite
CSS
Fetch API
```

Optional later:

```text
React Router
Recharts
Lucide Icons
```

---

# 54. Product Dashboard

Main navigation:

```text
Overview
Customers
Predictions
Insights
Model
```

---

# 55. Overview Page

Purpose:

Immediately explain the product.

Hero:

> Know who is leaving before they do.

Supporting statement:

> ChurnX uses machine learning to identify high-risk customers and explain the factors associated with their churn probability.

---

# 56. Overview Metrics

Cards:

### Customers Analyzed

```text
7,043
```

### Customers Predicted High Risk

Calculated from scored dataset.

### Average Churn Probability

Calculated from predictions.

### Dataset Churn Rate

Actual percentage from dataset.

Important:

Do not show invented financial metrics such as:

```text
₹8.4L revenue protected
```

unless a legitimate calculation supports them.

---

# 57. Prediction Page

Form fields must correspond exactly to the model schema.

Sections:

### Customer

- gender
- senior citizen
- partner
- dependents

### Account

- tenure
- contract

### Services

- internet service
- phone service
- security
- backup
- support
- streaming

### Billing

- monthly charges
- total charges
- payment method
- paperless billing

Button:

```text
Analyze Churn Risk
```

---

# 58. Prediction Result

Display:

```text
CHURN RISK

81.24%

HIGH RISK
```

Then:

```text
Model Classification:
Likely to Churn
```

---

# 59. Explainability Panel

Example:

```text
WHY THIS CUSTOMER IS AT RISK

1. Month-to-month contract
2. Short customer tenure
3. No technical support
4. High monthly charges
```

---

# 60. Customers Page

Display scored customer dataset.

Columns:

```text
Customer ID
Tenure
Contract
Monthly Charges
Churn Probability
Risk
```

Controls:

```text
Search
Filter
Sort
```

Filters:

```text
All
High Risk
Medium Risk
Low Risk
```

---

# 61. Insights Page

Analytics:

- churn rate by contract
- churn rate by tenure
- churn by internet service
- churn by payment method
- churn by technical support
- feature importance

Charts may include:

```text
Bar Charts
Donut Charts
Histograms
Feature Importance Chart
```

---

# 62. Model Page

Display:

```text
Model Name
Version
Training Date
Dataset
ROC-AUC
Recall
Precision
F1
```

This helps communicate that the product is an actual ML system.

---

# 63. Persistence Layer

For the simplest MVP:

```text
No database required
```

Prediction history may exist temporarily in frontend state.

Better product version:

```text
SQLite — local development
PostgreSQL — deployed application
```

Tables:

### predictions

```text
id
customer_id
probability
risk_level
model_version
created_at
```

---

# 64. Repository Architecture

Recommended:

```text
churnx/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── App.css
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── model_service.py
│   │   └── config.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── ml/
│   ├── notebooks/
│   │   ├── 01_eda.ipynb
│   │   ├── 02_preprocessing.ipynb
│   │   └── 03_model_experiments.ipynb
│   │
│   ├── src/
│   │   ├── data.py
│   │   ├── features.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── predict.py
│   │
│   └── models/
│       ├── churnx_pipeline.joblib
│       └── metadata.json
│
├── data/
│   ├── raw/
│   └── processed/
│
├── tests/
│
├── docs/
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

# 65. Training Command

Goal:

Eventually training should not depend on manually running notebook cells.

Example:

```bash
python -m ml.src.train
```

Pipeline:

```text
Load Dataset
    ↓
Validate
    ↓
Clean
    ↓
Split
    ↓
Train Models
    ↓
Cross Validate
    ↓
Compare Metrics
    ↓
Tune Best Candidates
    ↓
Evaluate Test Set
    ↓
Serialize Winner
```

---

# 66. Testing Requirements

## Data Tests

Test:

- expected columns
- valid target
- numeric conversion
- missing data handling

---

## Model Tests

Test:

```text
model file loads
prediction succeeds
probability ∈ [0,1]
expected feature count
```

---

## API Tests

Using:

```text
pytest
FastAPI TestClient
```

Test:

```text
GET /health → 200

POST /predict valid → 200

POST /predict invalid → 422
```

---

## Frontend Tests

Minimum manual tests:

- form accepts valid inputs
- required fields validated
- request sent correctly
- loading state visible
- errors displayed
- prediction rendered correctly

---

# 67. Error Handling

Frontend must handle:

```text
Backend unavailable
Invalid input
Prediction failure
Timeout
```

Example UI:

```text
Unable to analyze customer.

Please verify the customer information and try again.
```

Do not expose Python tracebacks to users.

---

# 68. Loading State

When inference is running:

```text
Analyzing customer...
```

Disable prediction button until the request completes.

---

# 69. Deployment Architecture

Recommended:

```text
                    INTERNET
                       │
             ┌─────────┴─────────┐
             │                   │
       React Frontend      FastAPI Backend
          Vercel             Container
             │                   │
             │                   ↓
             │             ML Pipeline
             │                   │
             └────── API ────────┘
```

---

# 70. Frontend Deployment

Recommended:

### Vercel

Vercel supports deployment of Vite projects and Git-based deployments, including preview and production environments.

Environment:

```text
VITE_API_URL=https://api-domain.example
```

Frontend requests:

```javascript
fetch(`${import.meta.env.VITE_API_URL}/predict`)
```

---

# 71. Backend Deployment

The FastAPI application should be containerized with Docker.

FastAPI's current deployment documentation recommends building a container from an official Python base image rather than relying on the old deprecated FastAPI base image.

Backend container contains:

```text
FastAPI code
Dependencies
Model artifact
Model metadata
```

---

# 72. Dockerfile Concept

```text
Python Base Image
       ↓
Install Dependencies
       ↓
Copy Backend
       ↓
Copy ML Model
       ↓
Start FastAPI
```

Backend should expose:

```text
PORT
```

provided by the deployment environment.

---

# 73. CORS

Backend must allow requests from the frontend deployment domain.

Development:

```text
http://localhost:5173
```

Production:

```text
https://churnx.vercel.app
```

Avoid:

```text
allow_origins=["*"]
```

for a production-style deployment where the frontend domain is known.

---

# 74. Environment Variables

Frontend:

```text
VITE_API_URL
```

Backend:

```text
APP_ENV
MODEL_PATH
ALLOWED_ORIGINS
DATABASE_URL
```

Do not commit `.env` files.

---

# 75. CI/CD

Recommended Git workflow:

```text
feature branch
      ↓
Pull Request
      ↓
Tests
      ↓
Merge
      ↓
Automatic Deployment
```

Frontend deployment can be connected to Git.

Vercel can automatically create deployments from connected Git repositories and generate preview deployments for changes before production.

---

# 76. Monitoring

Even a student ML product should include monitoring concepts.

## Application Monitoring

Track:

```text
request count
API error rate
prediction latency
backend health
```

---

# 77. Model Monitoring

Track:

```text
average churn probability
risk-level distribution
feature distributions
prediction distribution
```

Future:

```text
data drift
model drift
actual churn outcomes
```

---

# 78. Drift Detection

Example:

Training:

```text
Average tenure = X
```

Production:

```text
Average tenure changes significantly
```

This may indicate that production data no longer resembles training data.

ChurnX V1 only needs to document this concept.

---

# 79. Retraining Strategy

V1:

```text
Manual retraining
```

Steps:

```text
New labelled dataset
      ↓
Run training pipeline
      ↓
Evaluate
      ↓
Compare with existing model
      ↓
Approve
      ↓
Version
      ↓
Deploy
```

Do not automatically replace a production model simply because a new model exists.

---

# 80. Model Versioning

Example:

```text
churnx-v1.0.0
churnx-v1.1.0
churnx-v2.0.0
```

Prediction responses should contain:

```text
model_version
```

This improves reproducibility.

---

# 81. Security and Privacy

Real customer churn data could contain sensitive information.

Production principles:

- avoid unnecessary personal information
- do not expose customer identifiers publicly
- encrypt data in transit
- validate all incoming data
- avoid logging personal data
- restrict database access
- store secrets as environment variables

The academic dataset is fictional/sample data, making it appropriate for demonstration.

---

# 82. Fairness Considerations

Demographic fields can introduce fairness concerns.

Features such as:

```text
gender
SeniorCitizen
```

should be analyzed carefully.

ChurnX should compare model performance across relevant groups and determine whether demographics are actually necessary.

Possible advanced experiment:

Train:

```text
Model A — demographics included

Model B — demographics excluded
```

Compare performance.

This demonstrates responsible AI awareness.

---

# 83. Product Success Metrics

## ML Metrics

```text
ROC-AUC
PR-AUC
Recall
Precision
F1
```

---

## Technical Metrics

Target:

```text
Prediction endpoint < 500 ms under normal demo usage

API success rate > 99% during controlled testing

Frontend errors = 0 during primary demo flow
```

---

## Product Metrics

For demonstration:

```text
User can create a prediction

User can understand the risk category

User can identify major prediction factors

User can filter high-risk customers
```

---

# 84. MVP Definition

ChurnX MVP is complete when:

### Data

- IBM Telco dataset loaded
- cleaned
- validated
- EDA completed

### ML

- at least three meaningful classifiers trained
- models compared
- final model selected
- test metrics recorded
- model serialized

### Backend

- FastAPI server created
- `/health` implemented
- `/predict` implemented
- model loaded once on startup
- request validation implemented

### Frontend

- product dashboard exists
- prediction form matches model schema
- prediction API connected
- churn probability displayed
- risk category displayed

### Deployment

- frontend publicly accessible
- backend publicly accessible
- frontend successfully calls backend

---

# 85. Phase 1 — Data Foundation

Deliverables:

```text
dataset
data dictionary
cleaning script
EDA notebook
visualizations
```

Tasks:

1. Download IBM dataset.
2. Store raw copy.
3. Inspect schema.
4. Identify missing values.
5. Convert TotalCharges.
6. Encode target.
7. Analyze target imbalance.
8. Visualize churn characteristics.
9. Document observations.

---

# 86. Phase 2 — Machine Learning

Tasks:

1. Establish dummy baseline.
2. Create preprocessing pipeline.
3. Train Logistic Regression.
4. Train Decision Tree.
5. Train Random Forest.
6. Train boosting model.
7. Cross-validate.
8. Compare metrics.
9. Tune candidates.
10. Select final model.
11. Evaluate untouched test dataset.
12. Save model.
13. Save metadata.

---

# 87. Phase 3 — Explainability

Tasks:

1. Compute global feature importance.
2. Determine major churn drivers.
3. Create feature importance visualization.
4. Add customer-specific explanation if practical.
5. Document limitations.

---

# 88. Phase 4 — Backend

Tasks:

1. Create FastAPI project.
2. Load serialized pipeline.
3. Create prediction schema.
4. Implement `/health`.
5. Implement `/model-info`.
6. Implement `/predict`.
7. Add CORS.
8. Add error handling.
9. Add API tests.

---

# 89. Phase 5 — Frontend

Tasks:

1. Convert current mock dashboard to reusable components.
2. Replace fake prediction logic.
3. Align form with IBM model schema.
4. Connect FastAPI.
5. Add loading state.
6. Add error state.
7. Display prediction.
8. Display explanation.
9. Add customer list.
10. Add insights page.

---

# 90. Phase 6 — Deployment

Tasks:

1. Dockerize backend.
2. Test container locally.
3. Deploy backend.
4. Configure CORS.
5. Deploy Vite frontend.
6. Add production backend URL.
7. Perform end-to-end test.
8. Record demonstration video/screenshots.

---

# 91. Phase 7 — Documentation

Create:

```text
README.md
PRD.md
MODEL_CARD.md
DATA_DICTIONARY.md
API.md
```

README sections:

```text
Project Overview
Problem
Features
Architecture
Dataset
Model
Results
Installation
Training
Backend
Frontend
Deployment
Team
Limitations
Future Work
```

---

# 92. Suggested Development Responsibility Split

This is a suggested parallel workflow rather than a fixed requirement.

### Amogh Sharma

Possible ownership:

```text
ML architecture
Backend integration
Deployment
Overall system architecture
```

### Ayush Pal

Possible ownership:

```text
Frontend dashboard
Data visualization
UI integration
```

### Aditya Veer Singh

Possible ownership:

```text
Dataset pipeline
Model experimentation
API testing / analytics
```

All members should understand the complete system for evaluation and viva purposes.

---

# 93. Important Viva Concepts

Every member should be prepared to explain:

### Why classification?

Because:

```text
Churn ∈ {Yes, No}
```

---

### Why not regression?

The target is categorical.

The probability shown in the UI is generated by the classifier.

---

### Why Logistic Regression?

Interpretable baseline classifier.

---

### Why Random Forest?

Capable of capturing nonlinear interactions and mixed feature relationships.

---

### Why not accuracy alone?

Because the dataset is imbalanced and a majority-class model may obtain misleadingly high accuracy.

---

### What is precision?

Of predicted churners, how many were actually churners?

---

### What is recall?

Of actual churners, how many did the model detect?

---

### What is F1?

Harmonic mean of precision and recall.

---

### What is ROC-AUC?

Measures ranking ability across classification thresholds.

---

### What is overfitting?

When a model performs well on training data but poorly on unseen data.

---

### Why cross-validation?

To obtain a more stable estimate of model performance.

---

### Why separate test data?

The test set should simulate unseen data and should not influence model development.

---

### Why OneHotEncoder?

Most ML models require numeric representations of categorical values.

---

### What is data leakage?

When information unavailable at prediction time accidentally influences training.

---

# 94. Academic Evaluation Alignment

## Problem Domain Identification and Analysis

Covered through:

- churn business problem
- customer retention motivation
- classification formulation
- user requirements

---

## Review of Existing Systems and Feasibility

Covered through:

- historical churn modelling approach
- public IBM dataset
- open-source ML stack
- low infrastructure requirements
- reproducible deployment architecture

---

## Objectives and Methodology

Covered through:

```text
Data
→ EDA
→ Preprocessing
→ Training
→ Validation
→ Testing
→ Deployment
```

---

## Relevance of Algorithms / Techniques

Algorithms are compared instead of arbitrarily selected.

The project demonstrates:

- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosting
- class balancing
- cross-validation
- probability thresholds
- explainability

---

## Synchronization of Project Design and Implementation

The same preprocessing/model pipeline is used in:

```text
Training
and
Production Inference
```

Frontend input fields align with actual model features.

Backend directly consumes the trained model artifact.

This ensures the design and implementation describe the same system.

---

# 95. Key Risks

## Risk 1 — Fake Dashboard Data

The frontend may look polished but show numbers unrelated to the dataset.

### Mitigation

Calculate dashboard metrics from real dataset/prediction output.

---

## Risk 2 — Model / UI Schema Mismatch

Frontend collects features the model was never trained on.

### Mitigation

Maintain one canonical input schema.

---

## Risk 3 — Data Leakage

Outcome-related features improve metrics artificially.

### Mitigation

Audit features before training.

---

## Risk 4 — Overfitting

Complex model performs well only on training data.

### Mitigation

Cross-validation + untouched test set.

---

## Risk 5 — Misleading Probabilities

Model probability interpreted as certainty.

### Mitigation

Use risk terminology and optional probability calibration.

---

## Risk 6 — Deployment Environment Differences

Local model works but cloud deployment fails.

### Mitigation

Dockerize backend.

---

# 96. Future Roadmap

## ChurnX V1

```text
Static churn dataset
Classification
Dashboard
REST API
Single-customer prediction
```

---

## ChurnX V1.5

```text
Batch CSV scoring
Customer filtering
Prediction history
Explainability
Database
```

---

## ChurnX V2

Introduce behavioral data:

```text
activity frequency
support tickets
complaints
late payments
usage decline
failed transactions
```

---

## ChurnX V3

Temporal modelling:

```text
Customer activity over time
```

Possible approaches:

```text
Time-series features
Survival analysis
```

Prediction:

> Probability that customer churns within the next 30 days.

---

## ChurnX V4

Retention intelligence:

```text
Churn Risk
+
Customer Value
+
Retention Cost
```

Prioritize customers based on:

```text
Expected Value at Risk
```

---

## ChurnX V5

Recommendation engine:

```text
High churn risk
       ↓
Analyze customer profile
       ↓
Recommend retention action
```

Example:

```text
Switch to yearly plan
Offer support consultation
Provide targeted discount
Improve service package
```

Such recommendations must initially be presented as heuristic suggestions unless their effectiveness is validated experimentally.

---

# 97. Final System Architecture

```text
                    CHURNX

              CUSTOMER DATA
                    │
                    ▼
           ┌──────────────────┐
           │ Input Validation │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ ML Preprocessing │
           │                  │
           │ Missing Values   │
           │ One-Hot Encoding │
           │ Scaling          │
           │ Features         │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Classification   │
           │ Model            │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ predict_proba()  │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Risk Engine      │
           │                  │
           │ LOW              │
           │ MEDIUM           │
           │ HIGH             │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Explainability   │
           └────────┬─────────┘
                    │
                    ▼
             FASTAPI REST API
                    │
                    ▼
             REACT DASHBOARD
                    │
          ┌─────────┼──────────┐
          ▼         ▼          ▼
      Overview   Customers   Insights
                    │
                    ▼
              DEPLOYED PRODUCT
```

---

# 98. Final Definition of ChurnX

ChurnX should ultimately be described as:

> **An end-to-end machine-learning customer retention intelligence platform that processes customer account and service information, predicts individual churn probability using supervised classification, categorizes customers by risk, explains important prediction factors and exposes these results through a deployed interactive web dashboard.**

The project's main strength should not be that it uses the most complicated algorithm.

Its strength should be that the entire machine-learning lifecycle is correctly implemented:

```text
Problem
   ↓
Dataset
   ↓
Exploration
   ↓
Preprocessing
   ↓
Training
   ↓
Evaluation
   ↓
Explainability
   ↓
Serialization
   ↓
API
   ↓
Frontend
   ↓
Deployment
   ↓
Monitoring
```

That makes ChurnX an actual **AI/ML system**, rather than a model running inside a notebook.