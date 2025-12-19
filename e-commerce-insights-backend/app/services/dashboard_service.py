import logging
from calendar import month_name
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy import and_, distinct, func
from sqlalchemy.orm import Session

from ..models import FileMetadata, SalesData
from ..schemas import (
    CategoryPerformance,
    DashboardForecasts,
    DashboardMetrics,
    ForecastPeriod,
    MetricValue,
    MonthlySales,
)
from .forecast_service import ensure_forecast_file, load_forecast_file, run_multi_period_forecasts

logger = logging.getLogger(__name__)


def get_latest_file_id(db: Session, user_id: int) -> Optional[int]:
    """Get the most recent processed file for a user."""
    file_metadata = (
        db.query(FileMetadata)
        .filter(and_(FileMetadata.user_id == user_id, FileMetadata.processed.is_(True)))
        .order_by(FileMetadata.upload_time.desc())
        .first()
    )
    return file_metadata.id if file_metadata else None


def _require_latest_file_id(db: Session, user_id: int) -> int:
    file_id = get_latest_file_id(db, user_id)
    if not file_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No processed files found"
        )
    return file_id


def _latest_date_for_file(db: Session, file_id: int) -> Optional[datetime]:
    return (
        db.query(func.max(SalesData.transaction_date))
        .filter(SalesData.file_id == file_id)
        .scalar()
    )


def build_dashboard_metrics(db: Session, user_id: int) -> DashboardMetrics:
    file_id = _require_latest_file_id(db, user_id)
    latest_date = _latest_date_for_file(db, file_id)
    if not latest_date:
        return DashboardMetrics(
            total_revenue=MetricValue(value=0.0, growth=0.0),
            total_orders=MetricValue(value=0.0, growth=0.0),
            active_users=MetricValue(value=0.0, growth=0.0),
            avg_order_value=MetricValue(value=0.0, growth=0.0),
        )

    current_month_start = datetime(latest_date.year, latest_date.month, 1)
    next_month_start = (
        datetime(latest_date.year + 1, 1, 1)
        if latest_date.month == 12
        else datetime(latest_date.year, latest_date.month + 1, 1)
    )

    if current_month_start.month == 1:
        previous_month_start = datetime(current_month_start.year - 1, 12, 1)
        previous_month_end = datetime(current_month_start.year, 1, 1)
    else:
        previous_month_start = datetime(
            current_month_start.year, current_month_start.month - 1, 1
        )
        previous_month_end = current_month_start

    current_revenue = (
        db.query(func.sum(SalesData.purchase_amount))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= current_month_start,
            SalesData.transaction_date < next_month_start,
            SalesData.purchase_amount.isnot(None),
        )
        .scalar()
        or 0.0
    )

    current_orders = (
        db.query(func.count(SalesData.id))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= current_month_start,
            SalesData.transaction_date < next_month_start,
        )
        .scalar()
        or 0
    )

    current_users = (
        db.query(func.count(distinct(SalesData.user_name)))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= current_month_start,
            SalesData.transaction_date < next_month_start,
            SalesData.user_name.isnot(None),
        )
        .scalar()
        or 0
    )

    current_avg_order = float(current_revenue) / current_orders if current_orders else 0.0

    previous_revenue = (
        db.query(func.sum(SalesData.purchase_amount))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= previous_month_start,
            SalesData.transaction_date < previous_month_end,
            SalesData.purchase_amount.isnot(None),
        )
        .scalar()
        or 0.0
    )

    previous_orders = (
        db.query(func.count(SalesData.id))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= previous_month_start,
            SalesData.transaction_date < previous_month_end,
        )
        .scalar()
        or 0
    )

    previous_users = (
        db.query(func.count(distinct(SalesData.user_name)))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= previous_month_start,
            SalesData.transaction_date < previous_month_end,
            SalesData.user_name.isnot(None),
        )
        .scalar()
        or 0
    )

    previous_avg_order = (
        float(previous_revenue) / previous_orders if previous_orders else 0.0
    )

    def growth(current: float, previous: float) -> float:
        return ((current - previous) / previous * 100) if previous > 0 else 0.0

    return DashboardMetrics(
        total_revenue=MetricValue(
            value=float(current_revenue), growth=growth(float(current_revenue), float(previous_revenue))
        ),
        total_orders=MetricValue(value=float(current_orders), growth=growth(current_orders, previous_orders)),
        active_users=MetricValue(value=float(current_users), growth=growth(current_users, previous_users)),
        avg_order_value=MetricValue(
            value=current_avg_order, growth=growth(current_avg_order, previous_avg_order)
        ),
    )


def build_category_performance(db: Session, user_id: int) -> List[CategoryPerformance]:
    file_id = _require_latest_file_id(db, user_id)
    latest_date = _latest_date_for_file(db, file_id)
    if not latest_date:
        return []

    current_month_start = datetime(latest_date.year, latest_date.month, 1)
    next_month_start = (
        datetime(latest_date.year + 1, 1, 1)
        if latest_date.month == 12
        else datetime(latest_date.year, latest_date.month + 1, 1)
    )

    if current_month_start.month == 1:
        previous_month_start = datetime(current_month_start.year - 1, 12, 1)
        previous_month_end = datetime(current_month_start.year, 1, 1)
    else:
        previous_month_start = datetime(
            current_month_start.year, current_month_start.month - 1, 1
        )
        previous_month_end = current_month_start

    current_category_revenue = (
        db.query(SalesData.product_category, func.sum(SalesData.purchase_amount).label("revenue"))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= current_month_start,
            SalesData.transaction_date < next_month_start,
            SalesData.purchase_amount.isnot(None),
            SalesData.product_category.isnot(None),
        )
        .group_by(SalesData.product_category)
        .all()
    )

    previous_category_revenue = (
        db.query(SalesData.product_category, func.sum(SalesData.purchase_amount).label("revenue"))
        .filter(
            SalesData.file_id == file_id,
            SalesData.transaction_date >= previous_month_start,
            SalesData.transaction_date < previous_month_end,
            SalesData.purchase_amount.isnot(None),
            SalesData.product_category.isnot(None),
        )
        .group_by(SalesData.product_category)
        .all()
    )

    previous_dict = {cat: float(rev) for cat, rev in previous_category_revenue}

    categories = []
    for category, revenue in current_category_revenue:
        prev_revenue = previous_dict.get(category, 0.0)
        growth = ((float(revenue) - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0.0
        categories.append(
            CategoryPerformance(
                name=category,
                revenue=float(revenue),
                growth=growth,
                rank=0,  # temporary, updated below
            )
        )

    categories.sort(key=lambda item: item.revenue, reverse=True)
    for idx, category in enumerate(categories, start=1):
        category.rank = idx
    return categories


def build_monthly_sales(db: Session, user_id: int) -> List[MonthlySales]:
    file_id = _require_latest_file_id(db, user_id)
    latest_date = _latest_date_for_file(db, file_id)
    if not latest_date:
        return []

    anchor_year = latest_date.year
    anchor_month = latest_date.month
    months_data: List[MonthlySales] = []

    for i in range(5, -1, -1):
        month_total = anchor_month - i
        if month_total > 0:
            year = anchor_year
            month = month_total
        else:
            year = anchor_year - 1
            month = month_total + 12

        month_start = datetime(year, month, 1)
        month_end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        revenue = (
            db.query(func.sum(SalesData.purchase_amount))
            .filter(
                SalesData.file_id == file_id,
                SalesData.transaction_date >= month_start,
                SalesData.transaction_date < month_end,
                SalesData.purchase_amount.isnot(None),
            )
            .scalar()
            or 0.0
        )

        months_data.append(
            MonthlySales(
                month=month_name[month],
                month_number=month,
                year=year,
                revenue=float(revenue),
            )
        )

    return months_data


def build_biweekly_sales(db: Session, user_id: int) -> List[Dict[str, Any]]:
    file_id = _require_latest_file_id(db, user_id)
    latest_date = _latest_date_for_file(db, file_id)
    if not latest_date:
        return []

    window_start = latest_date - timedelta(days=180)

    buckets = []
    cur_start = window_start
    while cur_start <= latest_date:
        cur_end = cur_start + timedelta(days=14)
        buckets.append((cur_start, cur_end))
        cur_start = cur_end

    results = []
    for start, end in buckets:
        revenue = (
            db.query(func.sum(SalesData.purchase_amount))
            .filter(
                SalesData.file_id == file_id,
                SalesData.transaction_date >= start,
                SalesData.transaction_date < end,
                SalesData.purchase_amount.isnot(None),
            )
            .scalar()
            or 0.0
        )

        results.append(
            {
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "label": f"{start.month:02}/{start.day:02}",
                "revenue": float(revenue),
            }
        )

    return results


def build_biweekly_historical_predictions(db: Session, user_id: int) -> List[Dict[str, Any]]:
    file_id = _require_latest_file_id(db, user_id)
    latest_date = _latest_date_for_file(db, file_id)
    if not latest_date:
        return []

    forecast_data = load_forecast_file(file_id, 84)
    if not forecast_data:
        logger.warning("Forecast file not found for historical predictions: file_id=%s", file_id)
        return []

    historical_predictions = forecast_data.get("historical_predictions", [])
    if not historical_predictions:
        return []

    pred_df = pd.DataFrame(historical_predictions)
    pred_df["transaction_date"] = pd.to_datetime(pred_df["transaction_date"])

    window_start = latest_date - timedelta(days=28)
    pred_df = pred_df[
        (pred_df["transaction_date"] >= window_start) & (pred_df["transaction_date"] <= latest_date)
    ]
    if pred_df.empty:
        return []

    buckets = []
    cur_start = window_start
    while cur_start <= latest_date:
        cur_end = cur_start + timedelta(days=14)
        buckets.append((cur_start, cur_end))
        cur_start = cur_end

    results = []
    for start, end in buckets:
        bucket_data = pred_df[
            (pred_df["transaction_date"] >= start) & (pred_df["transaction_date"] < end)
        ]
        revenue = (
            float(bucket_data["purchase_amount"].sum()) if not bucket_data.empty else 0.0
        )
        results.append(
            {
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "label": f"{start.month:02}/{start.day:02}",
                "revenue": revenue,
            }
        )
    return results


def build_biweekly_forecasts(db: Session, user_id: int) -> List[Dict[str, Any]]:
    file_id = _require_latest_file_id(db, user_id)
    latest_date = _latest_date_for_file(db, file_id)
    if not latest_date:
        return []

    forecast_data = ensure_forecast_file(file_id, 84)
    if not forecast_data:
        return []

    daily_forecasts = forecast_data.get("forecasts", [])
    if not daily_forecasts:
        return []

    forecast_df = pd.DataFrame(daily_forecasts)
    forecast_df["transaction_date"] = pd.to_datetime(forecast_df["transaction_date"])
    forecast_df.set_index("transaction_date", inplace=True)

    forecast_start = latest_date + timedelta(days=1)
    forecast_end = forecast_start + timedelta(days=84)

    buckets = []
    cur_start = forecast_start
    while cur_start < forecast_end:
        cur_end = cur_start + timedelta(days=14)
        buckets.append((cur_start, cur_end))
        cur_start = cur_end

    results = []
    for start, end in buckets:
        bucket_forecasts = forecast_df[(forecast_df.index >= start) & (forecast_df.index < end)]
        predicted_revenue = (
            float(bucket_forecasts["purchase_amount"].sum()) if not bucket_forecasts.empty else 0.0
        )
        results.append(
            {
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "label": f"{start.month:02}/{start.day:02}",
                "revenue": predicted_revenue,
            }
        )
    return results


def _build_forecast_payload(
    forecast_data: Dict[str, Any], days: int, period_name: str
) -> Dict[str, Any]:
    """Construct forecast summary payload from stored forecast file."""
    summary = forecast_data.get("summary", {}) or {}
    metrics = forecast_data.get("model_metrics", {}) or {}
    total_forecast = summary.get("total_forecasted_sales", 0.0)

    rmse = 0.0
    train_rmse = 0.0
    test_rmse = None
    overfit_ratio = 1.0

    if isinstance(metrics, dict) and metrics:
        first_key = list(metrics.keys())[0]
        first_metric = metrics[first_key]
        if isinstance(first_metric, dict) and "train_rmse" in first_metric:
            best_model = summary.get("best_model")
            if best_model and best_model in metrics:
                best_metrics = metrics[best_model]
                train_rmse = best_metrics.get("train_rmse", 0.0)
                test_rmse = best_metrics.get("test_rmse")
                rmse = test_rmse if test_rmse is not None else train_rmse
                if test_rmse is not None and test_rmse > 0:
                    overfit_ratio = train_rmse / test_rmse
            else:
                train_vals = [
                    m.get("train_rmse", 0.0)
                    for m in metrics.values()
                    if isinstance(m, dict)
                ]
                test_vals = [
                    m.get("test_rmse")
                    for m in metrics.values()
                    if isinstance(m, dict) and m.get("test_rmse") is not None
                ]
                train_rmse = float(sum(train_vals) / len(train_vals)) if train_vals else 0.0
                test_rmse = float(sum(test_vals) / len(test_vals)) if test_vals else None
                rmse = test_rmse if test_rmse is not None else train_rmse
                if test_rmse is not None and test_rmse > 0:
                    overfit_values = [
                        m.get("train_rmse", 0.0) / m.get("test_rmse")
                        for m in metrics.values()
                        if isinstance(m, dict) and m.get("test_rmse")
                    ]
                    if overfit_values:
                        overfit_ratio = float(sum(overfit_values) / len(overfit_values))
        else:
            train_rmse = metrics.get("train_rmse", 0.0)
            test_rmse = metrics.get("test_rmse")
            rmse = test_rmse if test_rmse is not None else train_rmse
            if test_rmse is not None and test_rmse > 0:
                overfit_ratio = train_rmse / test_rmse
    else:
        logger.warning("No model metrics found for %s forecast", period_name)

    avg_daily = summary.get("average_daily_sales", 0.0)
    base_confidence = 100 - (rmse / avg_daily * 100) if avg_daily > 0 else 85

    if overfit_ratio < 0.7:
        confidence_penalty = (0.7 - overfit_ratio) * 20
        base_confidence -= confidence_penalty
    elif overfit_ratio < 0.9:
        confidence_penalty = (0.9 - overfit_ratio) * 10
        base_confidence -= confidence_penalty

    decay_rate = 0.995
    time_decay = decay_rate ** days
    base_confidence *= time_decay

    confidence = max(50, min(99, base_confidence))
    change_pct = 5.0

    return {
        "period": period_name,
        "value": total_forecast,
        "change": change_pct,
        "confidence": confidence,
        "forecast_days": days,
    }


def build_dashboard_forecasts(db: Session, user_id: int) -> DashboardForecasts:
    file_id = _require_latest_file_id(db, user_id)
    forecast_periods = [(14, "2 Weeks"), (42, "6 Weeks"), (84, "12 Weeks")]
    periods: List[ForecastPeriod] = []

    forecasts_dict: Dict[str, Dict[str, Any]] = {}
    all_exist = True

    for days, period_name in forecast_periods:
        forecast_data = load_forecast_file(file_id, days)
        if forecast_data:
            try:
                forecasts_dict[period_name] = _build_forecast_payload(
                    forecast_data, days, period_name
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning(
                    "Error parsing stored forecast for %s: %s", period_name, exc
                )
                all_exist = False
        else:
            all_exist = False

    forecast_result: Dict[str, Any] = {"success": False}
    if all_exist and len(forecasts_dict) == len(forecast_periods):
        forecast_result = {"success": True, "forecasts": forecasts_dict}
    else:
        forecast_result = run_multi_period_forecasts(file_id) or {}
        if forecast_result.get("success"):
            forecasts_dict = forecast_result.get("forecasts", {})

    for days, period_name in forecast_periods:
        period_data = forecasts_dict.get(period_name) or {}
        periods.append(
            ForecastPeriod(
                period=period_name,
                value=period_data.get("value", 0.0),
                change=period_data.get("change", 0.0),
                confidence=period_data.get("confidence", 0.0),
                forecast_days=days,
            )
        )

    return DashboardForecasts(periods=periods)


