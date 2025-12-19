"""
Module to execute the forecasting notebook and extract predictions.
"""
import os
import json
import papermill as pm
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from .database import SessionLocal
from .models import SalesData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
NOTEBOOK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
NOTEBOOK_PATH = os.path.join(NOTEBOOK_DIR, "forecasting.ipynb")
OUTPUT_DIR = os.path.join(NOTEBOOK_DIR, "outputs")
FORECAST_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "forecasts.json")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def execute_notebook(file_id: int, forecast_days: int = 30) -> Dict:
    """
    Execute the forecasting notebook with given parameters and extract forecasts.
    
    Args:
        file_id: ID of the uploaded file to forecast
        forecast_days: Number of days to forecast (default: 30)
    
    Returns:
        Dictionary containing forecast results and metadata
    """
    try:
        logger.info(f"Executing notebook for file_id={file_id}, forecast_days={forecast_days}")
        
        # Output notebook path
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        output_notebook = os.path.join(OUTPUT_DIR, f"forecast_{file_id}_{forecast_days}_{timestamp}.ipynb")
        
        # Unique output file for this forecast period
        unique_output_file = f"forecasts_{file_id}_{forecast_days}.json"
        unique_output_path = os.path.join(OUTPUT_DIR, unique_output_file)
        
        # Parameters to pass to notebook
        parameters = {
            'file_id': file_id,
            'forecast_days': forecast_days,
            'output_file': unique_output_file
        }
        
        # Execute notebook with parameters
        pm.execute_notebook(
            NOTEBOOK_PATH,
            output_notebook,
            parameters=parameters,
            kernel_name='python3'
        )
        
        # Read the forecast results from the output file
        if os.path.exists(unique_output_path):
            with open(unique_output_path, 'r') as f:
                forecast_data = json.load(f)
            
            logger.info(f"Successfully generated forecasts for file_id={file_id}")
            # Anchor forecast dates to the day after the dataset's last date
            try:
                db = SessionLocal()
                latest_date = db.query(SalesData.transaction_date).filter(SalesData.file_id == file_id).order_by(SalesData.transaction_date.desc()).limit(1).scalar()
            finally:
                try:
                    db.close()
                except Exception:
                    pass

            if latest_date:
                forecasts_list = forecast_data.get('forecasts', []) or []
                # Rebuild dates sequentially from latest_date + 1 day
                if isinstance(forecasts_list, list) and len(forecasts_list) > 0:
                    from datetime import timedelta
                    rebuilt = []
                    for idx, entry in enumerate(forecasts_list, start=1):
                        new_date = (pd.Timestamp(latest_date) + pd.Timedelta(days=idx)).strftime('%Y-%m-%d')
                        amount = entry.get('purchase_amount', entry.get('y', 0.0))
                        rebuilt.append({
                            'transaction_date': new_date,
                            'purchase_amount': float(amount) if amount is not None else 0.0
                        })
                    forecast_data['forecasts'] = rebuilt
                    # Recompute summary
                    total = float(sum(e['purchase_amount'] for e in rebuilt))
                    avg = float(total / len(rebuilt)) if rebuilt else 0.0
                    summary = forecast_data.get('summary', {}) or {}
                    summary.update({
                        'total_forecasted_sales': total,
                        'average_daily_sales': avg,
                        'forecast_period_start': rebuilt[0]['transaction_date'] if rebuilt else None,
                        'forecast_period_end': rebuilt[-1]['transaction_date'] if rebuilt else None,
                        'forecast_days': int(forecast_days),
                    })
                    forecast_data['summary'] = summary

            backtest_predictions = forecast_data.get('backtest_predictions')
            if not backtest_predictions:
                legacy_backtest = forecast_data.get('historical_predictions', []) or []
                normalized = []
                for entry in legacy_backtest:
                    if isinstance(entry, dict):
                        entry_date = entry.get('transaction_date') or entry.get('date')
                        if not entry_date:
                            continue
                        actual_val = entry.get('actual')
                        predicted_val = entry.get('predicted', entry.get('purchase_amount'))
                        try:
                            actual_val = float(actual_val) if actual_val is not None else None
                        except (TypeError, ValueError):
                            actual_val = None
                        try:
                            predicted_val = float(predicted_val) if predicted_val is not None else None
                        except (TypeError, ValueError):
                            predicted_val = None
                        normalized.append({
                            'date': str(entry_date),
                            'actual': actual_val,
                            'predicted': predicted_val
                        })
                backtest_predictions = normalized
            else:
                normalized = []
                for entry in backtest_predictions:
                    if not isinstance(entry, dict):
                        continue
                    entry_date = entry.get('date') or entry.get('transaction_date')
                    if not entry_date:
                        continue
                    actual_val = entry.get('actual')
                    predicted_val = entry.get('predicted', entry.get('purchase_amount'))
                    try:
                        actual_val = float(actual_val) if actual_val is not None else None
                    except (TypeError, ValueError):
                        actual_val = None
                    try:
                        predicted_val = float(predicted_val) if predicted_val is not None else None
                    except (TypeError, ValueError):
                        predicted_val = None
                    normalized.append({
                        'date': str(entry_date),
                        'actual': actual_val,
                        'predicted': predicted_val
                    })
                backtest_predictions = normalized

            forecast_data['backtest_predictions'] = backtest_predictions

            return {
                'success': True,
                'file_id': file_id,
                'forecast_days': forecast_days,
                'forecasts': forecast_data.get('forecasts', []),
                'backtest_predictions': forecast_data.get('backtest_predictions', []),
                'model_metrics': forecast_data.get('model_metrics', {}),
                'summary': forecast_data.get('summary', {})
            }
        else:
            logger.warning(f"Forecast output file not found: {unique_output_path}")
            return {
                'success': False,
                'error': 'Forecast output file not generated',
                'file_id': file_id
            }
            
    except Exception as e:
        logger.error(f"Error executing notebook: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'file_id': file_id
        }


def get_forecast_summary(forecast_data: Dict) -> Dict:
    """
    Generate summary statistics from forecast data.
    
    Args:
        forecast_data: Dictionary containing forecast results
    
    Returns:
        Summary dictionary with key metrics
    """
    if not forecast_data.get('success') or not forecast_data.get('forecasts'):
        return {}
    
    forecasts = forecast_data['forecasts']
    df = pd.DataFrame(forecasts)
    
    if 'purchase_amount' in df.columns:
        return {
            'total_forecasted_sales': float(df['purchase_amount'].sum()),
            'average_daily_sales': float(df['purchase_amount'].mean()),
            'forecast_period_start': df['transaction_date'].min() if 'transaction_date' in df.columns else None,
            'forecast_period_end': df['transaction_date'].max() if 'transaction_date' in df.columns else None,
            'min_daily_sales': float(df['purchase_amount'].min()),
            'max_daily_sales': float(df['purchase_amount'].max())
        }
    
    return {}


def execute_multi_period_forecasts(file_id: int) -> Dict:
    """
    Execute forecasting notebook for multiple periods (14, 42, 84 days).
    
    Args:
        file_id: ID of the uploaded file to forecast
    
    Returns:
        Dictionary containing forecast results for all periods
    """
    periods = [14, 42, 84]
    period_names = ["2 Weeks", "6 Weeks", "12 Weeks"]
    all_forecasts = {}
    
    for days, period_name in zip(periods, period_names):
        logger.info(f"Generating {period_name} forecast ({days} days) for file_id={file_id}")
        result = execute_notebook(file_id, forecast_days=days)
        if result.get('success'):
            summary = result.get('summary', {})
            forecasts = result.get('forecasts', [])
            total_forecast = summary.get('total_forecasted_sales', 0.0)
            backtest = result.get('backtest_predictions', [])
            
            # Calculate confidence based on model metrics
            metrics = result.get('model_metrics', {})
            
            # Handle nested structure from robust forecasting (multiple models)
            rmse = 0.0
            train_rmse = 0.0
            test_rmse = None
            overfit_ratio = 1.0
            
            if isinstance(metrics, dict) and len(metrics) > 0:
                # Check if it's the nested format (robust forecasting)
                first_key = list(metrics.keys())[0]
                if isinstance(metrics[first_key], dict) and 'train_rmse' in metrics[first_key]:
                    # Robust forecasting format - use best model's metrics
                    summary_data = result.get('summary', {})
                    best_model = summary_data.get('best_model')
                    if best_model and best_model in metrics:
                        best_metrics = metrics[best_model]
                        train_rmse = best_metrics.get('train_rmse', 0.0)
                        test_rmse = best_metrics.get('test_rmse')
                        # Use test_rmse if available (more reliable), otherwise train_rmse
                        rmse = test_rmse if test_rmse is not None else train_rmse
                        
                        # Calculate overfitting ratio (train_rmse / test_rmse)
                        # < 1.0 indicates overfitting (train performs better than test)
                        if test_rmse is not None and test_rmse > 0:
                            overfit_ratio = train_rmse / test_rmse
                    else:
                        # Fallback: use first available model or average RMSE
                        train_rmse_values = [m.get('train_rmse', 0.0) for m in metrics.values() if isinstance(m, dict)]
                        test_rmse_values = [m.get('test_rmse') for m in metrics.values() if isinstance(m, dict) and m.get('test_rmse') is not None]
                        train_rmse = np.mean(train_rmse_values) if train_rmse_values else 0.0
                        test_rmse = np.mean(test_rmse_values) if test_rmse_values else None
                        rmse = test_rmse if test_rmse is not None else train_rmse
                        
                        if test_rmse is not None and test_rmse > 0:
                            overfit_ratio = train_rmse / test_rmse
                else:
                    # Simple format (current/fallback)
                    train_rmse = metrics.get('train_rmse', 0.0)
                    test_rmse = metrics.get('test_rmse')
                    rmse = test_rmse if test_rmse is not None else train_rmse
                    if test_rmse is not None and test_rmse > 0:
                        overfit_ratio = train_rmse / test_rmse
            
            avg_daily = summary.get('average_daily_sales', 0.0)
            # Base confidence using TEST RMSE (more reliable) or train_rmse as fallback
            base_confidence = 100 - (rmse / avg_daily * 100) if avg_daily > 0 else 85
            
            # Apply overfitting penalty if significant overfitting detected
            if overfit_ratio < 0.7:  # Significant overfitting (train RMSE much lower than test)
                confidence_penalty = (0.7 - overfit_ratio) * 20  # Reduce confidence by up to 4%
                base_confidence -= confidence_penalty
                logger.warning(f"Overfitting detected (ratio: {overfit_ratio:.3f}), applying confidence penalty: -{confidence_penalty:.1f}%")
            elif overfit_ratio < 0.9:  # Some overfitting
                confidence_penalty = (0.9 - overfit_ratio) * 10  # Reduce confidence by up to 1%
                base_confidence -= confidence_penalty
            
            # Apply time decay factor: confidence decreases with forecast horizon
            # Exponential decay: 0.5% reduction per day (more realistic for long-term forecasts)
            decay_rate = 0.995  # 0.5% reduction per day
            time_decay = decay_rate ** days
            base_confidence *= time_decay
            logger.info(f"Applied time decay for {days} days: {time_decay:.3f} (confidence: {base_confidence:.2f}%)")
            
            confidence = max(50, min(99, base_confidence))
            logger.info(f"Calculated confidence for {period_name}: RMSE={rmse} (test), train_rmse={train_rmse}, overfit_ratio={overfit_ratio:.3f}, time_decay={time_decay:.3f}, confidence={confidence}")
            
            # Calculate change percentage (compare to historical average)
            change_pct = 5.0  # Default optimistic change, could be calculated from trend
            
            all_forecasts[period_name] = {
                'period': period_name,
                'value': total_forecast,
                'change': change_pct,
                'confidence': confidence,
                'forecast_days': days,
                'forecasts': forecasts,
                'summary': summary,
                'metrics': metrics,
                'backtest': backtest
            }
        else:
            logger.warning(f"Failed to generate {period_name} forecast: {result.get('error')}")
            all_forecasts[period_name] = {
                'period': period_name,
                'value': 0.0,
                'change': 0.0,
                'confidence': 0.0,
                'forecast_days': days,
                'error': result.get('error')
            }
    
    return {
        'success': True,
        'file_id': file_id,
        'forecasts': all_forecasts
    }


