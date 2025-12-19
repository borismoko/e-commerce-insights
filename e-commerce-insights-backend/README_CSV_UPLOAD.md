# CSV Upload and Processing Workflow

This document describes the CSV upload and processing workflow implemented for the E-Commerce Insights backend.

## Overview

The system provides a complete workflow for handling CSV file uploads:

1. **File Upload**: Users can upload CSV files through a REST API endpoint
2. **File Storage**: Files are saved to disk in the `uploads/` directory
3. **Metadata Storage**: File metadata is stored in PostgreSQL
4. **Data Processing**: CSV data is parsed and inserted into the `sales_data` table

## Features

- ✅ Secure file upload with authentication
- ✅ File validation (type, size)
- ✅ Automatic CSV parsing with flexible column mapping
- ✅ PostgreSQL integration for metadata and data storage
- ✅ Error handling and cleanup
- ✅ RESTful API with proper response schemas
- ✅ User-specific file access control

## Database Schema

### File Metadata Table (`file_metadata`)
```sql
- id: Primary key
- filename: Original filename
- file_path: Path to saved file
- file_size: File size in bytes
- upload_time: Timestamp of upload
- processed: Boolean indicating if file was processed
- user_id: Foreign key to users table
```

### Sales Data Table (`sales_data`)
```sql
- id: Primary key
- transaction_id: Transaction identifier
- product_id: Product identifier
- product_name: Name of the product
- category: Product category
- subcategory: Product subcategory
- brand: Product brand
- price: Unit price
- quantity: Quantity ordered
- total_amount: Total amount for the line item
- discount_amount: Discount applied
- customer_id: Customer identifier
- customer_name: Customer name
- customer_email: Customer email
- customer_phone: Customer phone
- customer_address: Customer address
- customer_city: Customer city
- customer_state: Customer state
- customer_country: Customer country
- order_date: Date of order
- shipping_date: Date shipped
- delivery_date: Date delivered
- payment_method: Payment method used
- payment_status: Payment status
- shipping_address: Shipping address
- shipping_city: Shipping city
- shipping_state: Shipping state
- shipping_country: Shipping country
- shipping_cost: Cost of shipping
- tax_amount: Tax amount
- notes: Additional notes
- file_id: Foreign key to file_metadata table
- created_at: Timestamp when record was created
```

## API Endpoints

### 1. Upload CSV File
```
POST /api/upload/csv/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body: file (CSV file)
```

**Response:**
```json
{
  "message": "File uploaded and processed successfully",
  "file_id": 1,
  "filename": "sample_data.csv",
  "file_size": 2048,
  "records_inserted": 5,
  "upload_time": "2024-01-20T10:30:00Z"
}
```

### 2. Get Uploaded Files
```
GET /api/upload/files/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "sample_data.csv",
    "file_size": 2048,
    "upload_time": "2024-01-20T10:30:00Z",
    "processed": true
  }
]
```

### 3. Get File Data
```
GET /api/upload/files/{file_id}/data/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "transaction_id": "TXN001",
    "product_name": "Laptop Gaming",
    "category": "Electronics",
    "price": 1299.99,
    "quantity": 1,
    "total_amount": 1299.99,
    "customer_name": "John Doe",
    "order_date": "2024-01-15T00:00:00Z",
    "payment_method": "Credit Card",
    "payment_status": "Paid"
  }
]
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Ensure PostgreSQL is running and create the database:
```sql
CREATE DATABASE ecommerce;
```

Update the database connection in `app/database.py` if needed.

### 3. Start the Server
```bash
uvicorn app.main:app --reload
```

### 4. Test the API
1. Go to `http://localhost:8000/docs` for the interactive API documentation
2. Register a user and get an authentication token
3. Use the upload endpoint with your token

## CSV File Format

The system supports flexible CSV formats. It automatically maps common column names to database fields:

### Supported Column Names (case-insensitive)
- **Transaction ID**: `transaction_id`, `transactionid`, `id`, `order_id`, `orderid`
- **Product**: `product_name`, `productname`, `product`, `item_name`, `itemname`
- **Category**: `category`, `product_category`, `productcategory`
- **Price**: `price`, `unit_price`, `unitprice`, `cost`
- **Quantity**: `quantity`, `qty`, `amount`
- **Customer**: `customer_name`, `customername`, `customer`, `client_name`, `clientname`
- **Email**: `customer_email`, `customeremail`, `email`
- **Date**: `order_date`, `orderdate`, `date`, `purchase_date`, `purchasedate`

And many more! See the `parse_csv_to_sales_data` function in `app/upload.py` for the complete list.

## Sample Data

A sample CSV file (`sample_data.csv`) is included for testing. It contains 5 sample e-commerce transactions with all common fields.

## Error Handling

The system includes comprehensive error handling:
- File type validation (CSV only)
- File size limits (10MB default)
- Database transaction rollback on errors
- Automatic file cleanup on processing failures
- Detailed error messages

## Security Features

- Authentication required for all endpoints
- User-specific file access control
- File type validation
- Size limits to prevent abuse
- SQL injection protection through SQLAlchemy ORM

## File Storage

Files are stored in the `uploads/` directory with unique filenames to prevent conflicts. The original filename is preserved in the database metadata.

## Performance Considerations

- Files are processed row by row to handle large datasets
- Database transactions are used for data integrity
- File size limits prevent memory issues
- Pagination is implemented for data retrieval (1000 records per request)

## Future Enhancements

Potential improvements:
- Cloud storage integration (AWS S3, Google Cloud Storage)
- Asynchronous processing for large files
- Data validation and cleaning
- Duplicate detection
- Export functionality
- File compression
- Batch processing API
