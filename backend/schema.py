from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

YesNo = Literal["Yes", "No"]
InternetOption = Literal["Yes", "No", "No internet service"]

RAW_COLUMNS = {
    "gender": "gender", "senior_citizen": "SeniorCitizen", "partner": "Partner",
    "dependents": "Dependents", "tenure": "tenure", "phone_service": "PhoneService",
    "multiple_lines": "MultipleLines", "internet_service": "InternetService",
    "online_security": "OnlineSecurity", "online_backup": "OnlineBackup",
    "device_protection": "DeviceProtection", "tech_support": "TechSupport",
    "streaming_tv": "StreamingTV", "streaming_movies": "StreamingMovies",
    "contract": "Contract", "paperless_billing": "PaperlessBilling",
    "payment_method": "PaymentMethod", "monthly_charges": "MonthlyCharges",
    "total_charges": "TotalCharges",
}
NUMERIC = ["tenure", "MonthlyCharges", "TotalCharges"]
INTERNET_FIELDS = ["online_security", "online_backup", "device_protection", "tech_support", "streaming_tv", "streaming_movies"]


class CustomerInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    gender: Literal["Female", "Male"]
    senior_citizen: Literal[0, 1]
    partner: YesNo
    dependents: YesNo
    tenure: int = Field(ge=0, le=1200)
    phone_service: YesNo
    multiple_lines: Literal["Yes", "No", "No phone service"]
    internet_service: Literal["DSL", "Fiber optic", "No"]
    online_security: InternetOption
    online_backup: InternetOption
    device_protection: InternetOption
    tech_support: InternetOption
    streaming_tv: InternetOption
    streaming_movies: InternetOption
    contract: Literal["Month-to-month", "One year", "Two year"]
    paperless_billing: YesNo
    payment_method: Literal["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
    monthly_charges: float = Field(ge=0, le=1000000)
    total_charges: float = Field(ge=0, le=1000000000)

    @model_validator(mode="after")
    def validate_services(self):
        no_phone = self.phone_service == "No"
        if no_phone != (self.multiple_lines == "No phone service"):
            raise ValueError("Multiple lines must match phone service availability")
        for field in INTERNET_FIELDS:
            if (self.internet_service == "No") != (getattr(self, field) == "No internet service"):
                raise ValueError(f"{field} must match internet service availability")
        return self

    def raw_row(self):
        return {RAW_COLUMNS[key]: value for key, value in self.model_dump().items()}


class PredictionOutput(BaseModel):
    prediction: Literal[0, 1]
    churn_probability: float = Field(ge=0, le=1)
    churn_percentage: float
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    model_version: str
    top_factors: list[str]
    explanation_method: str
    prediction_id: str | None = None


def risk_level(probability, low=0.3, high=0.6):
    return "LOW" if probability < low else "MEDIUM" if probability < high else "HIGH"
