"""
Test script to check for overfitting in forecasting models.
This script will run a forecast and analyze the train vs validation RMSE.
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.notebook_runner import execute_notebook
import json

def test_overfitting(file_id: int, forecast_days: int = 30):
    """Test for overfitting by comparing train vs validation RMSE"""
    print(f"\n{'='*60}")
    print(f"Testing Overfitting for File ID: {file_id}")
    print(f"Forecast Period: {forecast_days} days")
    print(f"{'='*60}\n")
    
    result = execute_notebook(file_id, forecast_days=forecast_days)
    
    if not result.get('success'):
        print(f"❌ Forecast generation failed: {result.get('error', 'Unknown error')}")
        return
    
    metrics = result.get('model_metrics', {})
    summary = result.get('summary', {})
    best_model = summary.get('best_model')
    
    if not best_model:
        print("❌ No best model found")
        return
    
    if best_model not in metrics:
        print(f"❌ Best model '{best_model}' not found in metrics")
        return
    
    model_metrics = metrics[best_model]
    train_rmse = model_metrics.get('train_rmse', 0)
    val_rmse = model_metrics.get('val_rmse', 0)
    overfit_ratio = model_metrics.get('overfit_ratio', 1.0)
    
    print(f"\n{'='*60}")
    print(f"Overfitting Analysis for {best_model}")
    print(f"{'='*60}")
    print(f"Training RMSE:   {train_rmse:.2f}")
    print(f"Validation RMSE: {val_rmse:.2f}")
    print(f"Overfit Ratio:   {overfit_ratio:.3f} (train_rmse / val_rmse)")
    print(f"{'='*60}\n")
    
    # Analyze overfitting
    if overfit_ratio < 0.7:
        print("⚠️  WARNING: Significant overfitting detected!")
        print("   Model performs much better on training than validation.")
        print("   This suggests the model may not generalize well to new data.")
        print(f"   Confidence will be penalized by up to 4%")
    elif overfit_ratio < 0.9:
        print("⚠️  CAUTION: Some overfitting detected.")
        print("   Model performs slightly better on training than validation.")
        print(f"   Confidence will be penalized by up to 1%")
    elif overfit_ratio < 1.1:
        print("✓ Model generalizes well (low overfitting risk)")
        print("   Training and validation performance are similar.")
    else:
        print("ℹ️  Validation RMSE is lower than training RMSE")
        print("   This is unusual but not necessarily bad.")
    
    # Show all models for comparison
    print(f"\n{'='*60}")
    print("All Models Comparison:")
    print(f"{'='*60}")
    for model_name, model_metrics in metrics.items():
        if isinstance(model_metrics, dict):
            train_rmse = model_metrics.get('train_rmse', 0)
            val_rmse = model_metrics.get('val_rmse', model_metrics.get('train_rmse', 0))
            overfit_ratio = model_metrics.get('overfit_ratio', 1.0)
            marker = "★" if model_name == best_model else " "
            print(f"{marker} {model_name:15} | Train RMSE: {train_rmse:8.2f} | Val RMSE: {val_rmse:8.2f} | Ratio: {overfit_ratio:.3f}")
    
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    avg_daily = summary.get('average_daily_sales', 0.0)
    base_confidence = 100 - (val_rmse / avg_daily * 100) if avg_daily > 0 else 85
    
    # Calculate penalty
    confidence_penalty = 0.0
    if overfit_ratio < 0.7:
        confidence_penalty = (0.7 - overfit_ratio) * 20
    elif overfit_ratio < 0.9:
        confidence_penalty = (0.9 - overfit_ratio) * 10
    
    final_confidence = max(50, min(99, base_confidence - confidence_penalty))
    
    print(f"Average Daily Sales: ${avg_daily:,.2f}")
    print(f"Base Confidence:      {base_confidence:.2f}%")
    if confidence_penalty > 0:
        print(f"Overfitting Penalty: -{confidence_penalty:.2f}%")
    print(f"Final Confidence:     {final_confidence:.2f}%")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # Test with file_id 7 (or change to your file_id)
    test_overfitting(file_id=7, forecast_days=30)

