from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[int] = None
    role: Optional[str] = None


# Upload-related schemas
class FileMetadataBase(BaseModel):
    filename: str
    file_size: int


class FileMetadataCreate(FileMetadataBase):
    file_path: str
    user_id: Optional[int] = None


class FileMetadataRead(FileMetadataBase):
    id: int
    file_path: str
    upload_time: datetime
    processed: bool
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    message: str
    file_id: int
    filename: str
    file_size: int
    records_inserted: int
    upload_time: datetime


class SalesDataBase(BaseModel):
    transaction_id: Optional[str] = None
    user_name: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None
    product_category: Optional[str] = None
    purchase_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    transaction_date: Optional[datetime] = None


class SalesDataCreate(SalesDataBase):
    file_id: int


class SalesDataRead(SalesDataBase):
    id: int
    file_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    upload_time: datetime
    processed: bool


class SalesDataSummary(BaseModel):
    id: int
    transaction_id: Optional[str] = None
    user_name: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None
    product_category: Optional[str] = None
    purchase_amount: Optional[float] = None
    payment_method: Optional[str] = None
    transaction_date: Optional[datetime] = None


# Forecast-related schemas
class ForecastEntry(BaseModel):
    transaction_date: str
    purchase_amount: float


class ModelMetrics(BaseModel):
    train_mae: Optional[float] = None
    train_rmse: Optional[float] = None
    train_r2: Optional[float] = None
    test_mae: Optional[float] = None
    test_rmse: Optional[float] = None
    test_r2: Optional[float] = None


class ForecastSummary(BaseModel):
    total_forecasted_sales: float
    average_daily_sales: float
    min_daily_sales: float
    max_daily_sales: float
    forecast_period_start: str
    forecast_period_end: str
    forecast_days: int


class ForecastResponse(BaseModel):
    file_id: int
    forecast_days: int
    forecasts: List[ForecastEntry]
    model_metrics: ModelMetrics
    summary: ForecastSummary
    generated_at: str


class UploadResponseWithForecast(UploadResponse):
    forecast: Optional[ForecastResponse] = None


# Dashboard-related schemas
class MetricValue(BaseModel):
    value: float
    growth: Optional[float] = None  # Percentage growth month-over-month


class DashboardMetrics(BaseModel):
    total_revenue: MetricValue
    total_orders: MetricValue
    active_users: MetricValue
    avg_order_value: MetricValue


class CategoryPerformance(BaseModel):
    name: str
    revenue: float
    growth: float  # Percentage growth month-over-month
    rank: int


class MonthlySales(BaseModel):
    month: str  # Month name (e.g., "January 2024")
    month_number: int
    year: int
    revenue: float


class ForecastPeriod(BaseModel):
    period: str  # "1 Week", "1 Month", "3 Months"
    value: float
    change: float  # Percentage change
    confidence: float  # Confidence percentage
    forecast_days: int


class DashboardForecasts(BaseModel):
    periods: List[ForecastPeriod]
