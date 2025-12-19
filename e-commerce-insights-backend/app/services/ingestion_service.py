import logging

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import SalesData

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = {
    "transaction_id": ["transaction_id", "transactionid", "id"],
    "user_name": ["user_name", "username", "customer_name", "customername", "name"],
    "age": ["age"],
    "country": ["country"],
    "product_category": ["product_category", "productcategory", "category"],
    "purchase_amount": [
        "purchase_amount",
        "purchaseamount",
        "amount",
        "total_amount",
        "totalamount",
    ],
    "payment_method": ["payment_method", "paymentmethod", "payment"],
    "transaction_date": [
        "transaction_date",
        "transactiondate",
        "date",
        "order_date",
        "orderdate",
    ],
}


def parse_csv_to_sales_data(db: Session, file_path: str, file_id: int) -> int:
    """Parse CSV file and insert data into sales_data table."""
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError("CSV file is empty")

        column_mapping = {}
        csv_columns = [col.lower().strip() for col in df.columns]

        for db_col, possible_names in EXPECTED_COLUMNS.items():
            for name in possible_names:
                if name in csv_columns:
                    original_col = df.columns[csv_columns.index(name)]
                    column_mapping[db_col] = original_col
                    break

        records_inserted = 0
        for _, row in df.iterrows():
            sales_record = SalesData(file_id=file_id)

            for db_col, csv_col in column_mapping.items():
                value = row[csv_col]
                if pd.isna(value):
                    continue

                if db_col == "purchase_amount":
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        continue
                elif db_col == "age":
                    try:
                        value = int(float(value))
                    except (ValueError, TypeError):
                        continue
                elif db_col == "transaction_date":
                    try:
                        value = pd.to_datetime(value)
                    except (ValueError, TypeError):
                        continue
                else:
                    value = str(value)[:255]

                setattr(sales_record, db_col, value)

            db.add(sales_record)
            records_inserted += 1

        db.commit()
        return records_inserted

    except Exception as exc:  # pylint: disable=broad-except
        db.rollback()
        logger.error("Error parsing CSV file %s: %s", file_path, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing CSV file: {exc}",
        ) from exc






