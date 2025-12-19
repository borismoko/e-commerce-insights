import json
import logging
import os
from typing import Any

from ..notebook_runner import OUTPUT_DIR, execute_multi_period_forecasts

logger = logging.getLogger(__name__)


def _forecast_file_path(file_id: int, days: int) -> str:
    return os.path.join(OUTPUT_DIR, f"forecasts_{file_id}_{days}.json")


def load_forecast_file(file_id: int, days: int) -> dict[str, Any] | None:
    """Load a stored forecast file if it exists."""
    path = _forecast_file_path(file_id, days)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Failed to load forecast file %s: %s", path, exc)
        return None


def ensure_forecast_file(file_id: int, days: int) -> dict[str, Any] | None:
    """
    Ensure a forecast file exists for the given period.
    Generates forecasts if missing, then reloads the file.
    """
    data = load_forecast_file(file_id, days)
    if data is not None:
        return data

    logger.info("Forecast %s days missing for file %s, regenerating...", days, file_id)
    result = execute_multi_period_forecasts(file_id)
    if not result.get("success"):
        logger.warning("Forecast generation failed for file %s", file_id)
        return None

    return load_forecast_file(file_id, days)


def run_multi_period_forecasts(file_id: int) -> dict[str, Any] | None:
    """Execute forecasts for all configured periods."""
    logger.info("Executing multi-period forecasting for file_id=%s", file_id)
    try:
        result = execute_multi_period_forecasts(file_id)
        if result.get("success"):
            logger.info("Forecasts generated successfully for file_id=%s", file_id)
        else:
            logger.warning("Forecast generation returned unsuccessful for file_id=%s", file_id)
        return result
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error executing multi-period forecast: %s", exc, exc_info=True)
        return None






