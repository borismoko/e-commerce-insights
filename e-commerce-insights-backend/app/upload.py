from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from .database import get_db
from .models import FileMetadata, SalesData, User
from .auth import get_current_user
from .schemas import (
    FileListResponse,
    SalesDataSummary,
    UploadResponseWithForecast,
    DashboardMetrics,
    CategoryPerformance,
    MonthlySales,
    DashboardForecasts,
)
from .services.file_service import (
    cleanup_file,
    save_file_metadata,
    save_file_to_disk,
    validate_upload_file,
)
from .services.ingestion_service import parse_csv_to_sales_data
from .services.forecast_service import run_multi_period_forecasts
from .services.dashboard_service import (
    build_biweekly_forecasts,
    build_biweekly_historical_predictions,
    build_biweekly_sales,
    build_category_performance,
    build_dashboard_forecasts,
    build_dashboard_metrics,
    build_monthly_sales,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("/csv/", response_model=UploadResponseWithForecast, status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    forecast_days: int = Query(30, ge=1, le=365, description="Number of days to forecast"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process a CSV file containing sales data.
    
    The CSV file will be:
    1. Saved to disk in the uploads directory
    2. Metadata stored in PostgreSQL
    3. Data parsed and inserted into sales_data table
    4. Forecasting notebook executed automatically
    5. Forecast predictions returned in response
    
    Args:
        file: CSV file to upload
        forecast_days: Number of days to forecast (default: 30)
    """
    validate_upload_file(file)
    
    try:
        # Save file to disk
        file_path, file_size = save_file_to_disk(file)
        
        # Save file metadata to database
        file_metadata = save_file_metadata(
            db=db,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            user_id=current_user.id
        )
        
        # Parse CSV and insert data
        records_inserted = parse_csv_to_sales_data(db, file_path, file_metadata.id)
        
        # Update file metadata as processed
        file_metadata.processed = True
        db.commit()
        
        logger.info(f"File uploaded successfully. file_id={file_metadata.id}, records={records_inserted}")
        
        # Execute forecasting notebook for all periods (14, 42, 84 days)
        forecast_result = None
        if records_inserted > 0:
            try:
                logger.info(f"Executing multi-period forecasting for file_id={file_metadata.id}...")
                forecast_result = run_multi_period_forecasts(file_metadata.id)
                
                if forecast_result.get('success'):
                    logger.info(f"Forecasts generated successfully for file_id={file_metadata.id}")
                else:
                    logger.warning(f"Forecast generation failed for file_id={file_metadata.id}")
            except Exception as e:
                logger.error(f"Error executing notebook: {str(e)}", exc_info=True)
                # Don't fail the upload if forecasting fails, just log it
        
        # Build response
        response_data = {
            "message": "File uploaded and processed successfully",
            "file_id": file_metadata.id,
            "filename": file.filename,
            "file_size": file_size,
            "records_inserted": records_inserted,
            "upload_time": file_metadata.upload_time,
            "forecast": None
        }
        
        # Add forecast data to response if available
        # Note: For multi-period forecasts, we don't map directly to ForecastResponse
        # Instead, forecasts are stored and can be retrieved via the forecasts endpoint
        if forecast_result and forecast_result.get('success'):
            logger.info(f"Multi-period forecasts stored for file_id={file_metadata.id}")
        
        return response_data
        
    except Exception as e:
        if 'file_path' in locals():
            cleanup_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/files/", response_model=List[FileListResponse])
async def get_uploaded_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of uploaded files for the current user"""
    
    files = db.query(FileMetadata).filter(FileMetadata.user_id == current_user.id).all()
    
    return [
        FileListResponse(
            id=file.id,
            filename=file.filename,
            file_size=file.file_size,
            upload_time=file.upload_time,
            processed=file.processed
        )
        for file in files
    ]


@router.get("/files/{file_id}/data/", response_model=List[SalesDataSummary])
async def get_file_data(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sales data for a specific uploaded file"""
    
    # Verify file belongs to user
    file_metadata = db.query(FileMetadata).filter(
        FileMetadata.id == file_id,
        FileMetadata.user_id == current_user.id
    ).first()
    
    if not file_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Get sales data
    sales_data = db.query(SalesData).filter(SalesData.file_id == file_id).limit(1000).all()
    
    return [
        SalesDataSummary(
            id=record.id,
            transaction_id=record.transaction_id,
            user_name=record.user_name,
            age=record.age,
            country=record.country,
            product_category=record.product_category,
            purchase_amount=float(record.purchase_amount) if record.purchase_amount else None,
            payment_method=record.payment_method,
            transaction_date=record.transaction_date
        )
        for record in sales_data
    ]


@router.get("/dashboard/metrics/", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard metrics for the most recently uploaded file."""
    return build_dashboard_metrics(db, current_user.id)


@router.get("/dashboard/categories/", response_model=List[CategoryPerformance])
async def get_category_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get category performance ranked by revenue with growth calculations."""
    return build_category_performance(db, current_user.id)


@router.get("/dashboard/monthly-sales/", response_model=List[MonthlySales])
async def get_monthly_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly sales data for the last 6 months."""
    return build_monthly_sales(db, current_user.id)


@router.get("/dashboard/biweekly-sales/")
async def get_biweekly_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get biweekly (14-day) sales sums covering approximately the last 6 months."""
    return build_biweekly_sales(db, current_user.id)


@router.get("/dashboard/biweekly-historical-predictions/")
async def get_biweekly_historical_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Historical predictions aggregated biweekly for the last 4 weeks."""
    return build_biweekly_historical_predictions(db, current_user.id)


@router.get("/dashboard/biweekly-forecasts/")
async def get_biweekly_forecasts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Biweekly forecast buckets for the next 12 weeks."""
    return build_biweekly_forecasts(db, current_user.id)


@router.get("/dashboard/forecasts/", response_model=DashboardForecasts)
async def get_dashboard_forecasts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get forecasts for 2, 6, and 12 weeks."""
    return build_dashboard_forecasts(db, current_user.id)
