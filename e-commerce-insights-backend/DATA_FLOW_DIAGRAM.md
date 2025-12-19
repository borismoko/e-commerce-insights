# Data Flow and User Tracking Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER UPLOADS CSV FILE                        │
│                    (via FastAPI /api/upload/csv/)                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FILE SAVED TO DISK                           │
│              uploads/20d05d09-4a5b-46e5-b63b-63f69528450b.csv        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   METADATA STORED IN DATABASE                        │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  file_metadata TABLE                                          │  │
│  │  ──────────────────────────────────────────────────────────  │  │
│  │  id: 1                                                        │  │
│  │  filename: "sales_data_2024.csv"                             │  │
│  │  file_path: "uploads/20d05d09-4a5b-46e5-b63b-63f69528450b.csv"│ │
│  │  file_size: 245760                                            │  │
│  │  upload_time: 2024-01-15 10:30:00                            │  │
│  │  processed: true                                              │  │
│  │  user_id: 5  ◄──────────────────────────────────────────────┐│  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CSV DATA PARSED AND STORED                        │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  sales_data TABLE                                             │  │
│  │  ──────────────────────────────────────────────────────────  │  │
│  │  id: 1                                                        │  │
│  │  transaction_id: "TXN-001"                                   │  │
│  │  user_name: "John Doe"                                       │  │
│  │  age: 35                                                      │  │
│  │  country: "USA"                                              │  │
│  │  product_category: "Electronics"                             │  │
│  │  purchase_amount: 299.99                                     │  │
│  │  payment_method: "Credit Card"                               │  │
│  │  transaction_date: 2024-01-15 10:30:00                       │  │
│  │  file_id: 1  ◄──────────────────────────────────────────────┐│  │
│  │  created_at: 2024-01-15 10:30:05                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   NOTEBOOK LOADS DATA FOR ANALYSIS                   │
│                                                                      │
│  load_file_with_metadata(file_id=1)                                 │
│  ───────────────────────────────────────────────────────            │
│  Returns:                                                            │
│    • File metadata (including user info)                            │
│    • All sales records from that file                               │
│                                                                      │
│  You can now:                                                        │
│  ✓ Identify who uploaded the data                                   │
│  ✓ Perform forecasting and analysis                                 │
│  ✓ Generate insights and reports                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Relationships

```
┌──────────────────────┐
│       users          │
│  ─────────────────   │
│  id (PK)             │
│  name                │
│  email               │
│  password_hash       │
│  role                │
│  created_at          │
└──────────┬───────────┘
           │
           │ 1:N relationship
           │ (one user can upload many files)
           │
           ▼
┌──────────────────────────────────────────┐
│         file_metadata                    │
│  ─────────────────────────────────────   │
│  id (PK)                                 │
│  filename                                │
│  file_path                               │
│  file_size                               │
│  upload_time                             │
│  processed                               │
│  user_id (FK) ──────────────────────┐   │
└──────────┬───────────────────────────┼───┘
           │                           │
           │ 1:N relationship          │ References
           │ (one file has many        │ users.id
           │  sales records)           │
           │                           │
           ▼                           │
┌──────────────────────────────────────┼───┐
│         sales_data                   │   │
│  ────────────────────────────────────┼─  │
│  id (PK)                             │   │
│  transaction_id                      │   │
│  user_name                           │   │
│  age                                 │   │
│  country                             │   │
│  product_category                    │   │
│  purchase_amount                     │   │
│  payment_method                      │   │
│  transaction_date                    │   │
│  file_id (FK) ───────────────────────┘   │
│  created_at                                │
└────────────────────────────────────────────┘
```

## User Tracking Flow

```
┌─────────────────────────────────────────────────────────────┐
│  QUESTION: Who uploaded this sales data?                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  ANSWER: Follow the foreign key relationships!               │
│                                                              │
│  Step 1: Get sales record                                   │
│  ──────────────────────────────────────────────────────     │
│  sales_record = get_sales_record(id=12345)                  │
│  sales_record.file_id = 1                                   │
│                                                              │
│  Step 2: Get file metadata                                  │
│  ──────────────────────────────────────────────────────     │
│  file_meta = get_file_metadata(id=1)                        │
│  file_meta.user_id = 5                                      │
│  file_meta.filename = "sales_data_2024.csv"                 │
│                                                              │
│  Step 3: Get user information                               │
│  ──────────────────────────────────────────────────────     │
│  user = get_user(id=5)                                      │
│  user.name = "John Smith"                                   │
│  user.email = "john.smith@company.com"                      │
│  user.role = "analyst"                                      │
│                                                              │
│  RESULT: This data was uploaded by John Smith               │
│          (john.smith@company.com) on 2024-01-15             │
└─────────────────────────────────────────────────────────────┘
```

## Example: Loading Data in Notebook

```python
# 1. Load file metadata with user information
meta, sales = load_file_with_metadata(file_id=1)

# 2. Extract user information
uploader_name = meta['user_name'].iloc[0]
uploader_email = meta['user_email'].iloc[0]
upload_time = meta['upload_time'].iloc[0]

# 3. Display
print(f"Dataset: {meta['filename'].iloc[0]}")
print(f"Uploaded by: {uploader_name} ({uploader_email})")
print(f"Uploaded on: {upload_time}")
print(f"Records: {len(sales)}")
print(f"Total sales: ${sales['purchase_amount'].sum():,.2f}")

# Output:
# Dataset: sales_data_2024.csv
# Uploaded by: John Smith (john.smith@company.com)
# Uploaded on: 2024-01-15 10:30:00
# Records: 1000
# Total sales: $125,450.00
```

## Key Points

1. **Every uploaded file is tracked** with its original filename and upload timestamp
2. **Every file links to a user** via the `user_id` foreign key
3. **Every sales record links to its source file** via the `file_id` foreign key
4. **You can always trace data back** to who uploaded it and when
5. **The notebook has direct database access** to all this information

## Security Note

The current implementation allows the notebook to access all uploaded data regardless of user. For production use, you might want to:

- Add user authentication to the notebook
- Filter data based on the current user's permissions
- Implement role-based access control (e.g., analysts can only see their own data, admins can see all)


