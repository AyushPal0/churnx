# Customer input dictionary

The API uses the following 19 fields. Dataset columns are mapped in `backend/schema.py`; `customerID` and `Churn` never enter the model.

| API field | Dataset column | Valid values / units |
|---|---|---|
| gender | gender | Female, Male |
| senior_citizen | SeniorCitizen | Integer 0 or 1 |
| partner | Partner | Yes, No |
| dependents | Dependents | Yes, No |
| tenure | tenure | Nonnegative integer, months |
| phone_service | PhoneService | Yes, No |
| multiple_lines | MultipleLines | Yes, No, No phone service |
| internet_service | InternetService | DSL, Fiber optic, No |
| online_security | OnlineSecurity | Yes, No, No internet service |
| online_backup | OnlineBackup | Yes, No, No internet service |
| device_protection | DeviceProtection | Yes, No, No internet service |
| tech_support | TechSupport | Yes, No, No internet service |
| streaming_tv | StreamingTV | Yes, No, No internet service |
| streaming_movies | StreamingMovies | Yes, No, No internet service |
| contract | Contract | Month-to-month, One year, Two year |
| paperless_billing | PaperlessBilling | Yes, No |
| payment_method | PaymentMethod | Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic) |
| monthly_charges | MonthlyCharges | Nonnegative finite USD amount |
| total_charges | TotalCharges | Nonnegative finite USD amount |

Phone service `No` requires `No phone service` for multiple lines. Internet service `No` requires `No internet service` for every internet-dependent field; those sentinel categories are invalid when the relevant base service is present. The UI keeps these fields synchronized, and the API validates them independently.

API resource bounds are 1,200 months, $1,000,000 monthly charges and $1,000,000,000 total charges. These are input limits, not the model's observed training range. Inputs outside the historical dataset distribution may be unreliable.

The source target is `Churn` (`Yes` → 1, `No` → 0). Blank `TotalCharges` values for zero-tenure customers become 0. Remaining numerical missing values are median-imputed within the pipeline's training folds. Categorical missing values use the most frequent training category, while unexpected raw source categories cause validation to fail.
