# E-Commerce Insights Platform

A full-stack application for analyzing e-commerce sales data, generating insights, and forecasting future sales trends.

## Project Structure

e-commerce-insights/
├── e-commerce-insights-backend/ # FastAPI backend service
└── e-commerce-insights-frontend/ # React frontend application


## Features

- **Data Upload**: Upload CSV files containing sales data
- **Data Analysis**: Comprehensive dashboard with sales insights
- **Sales Forecasting**: ML-powered forecasting using Prophet, XGBoost, and statistical models
- **Product Performance**: Analyze product sales and performance metrics
- **User Authentication**: Secure user authentication and authorization
- **Real-time Dashboard**: Interactive charts and visualizations

## Quick Start Guide

### Prerequisites

- **Backend**:
  - Python 3.8+
  - PostgreSQL 12+
  - pip

- **Frontend**:
  - Node.js 18+ (or Bun)
  - npm/yarn/bun

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd e-commerce-insights-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
5. **Set up PostgreSQL database**:
   - Create a new database:
   ```

     ```sql
     CREATE DATABASE ecommerce;
     ```
   - Update database connection in `app/database.py` if needed:
     ```python
     DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/ecommerce"
     ```

6. **Create environment file** (optional):
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

7. **Start the backend server**:
   ```bash
   python start_server.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd e-commerce-insights-frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   # or
   bun install
   ```

3. **Configure API endpoint** (if needed):
   Update the API base URL in `src/lib/api.ts` to match your backend URL.

4. **Start the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   bun dev
   ```

   The frontend will be available at `http://localhost:5173` (or the port shown in terminal)

## 📖 Usage

### 1. Register/Login

- Create an account or login through the authentication page
- You'll receive an authentication token for API access

### 2. Upload Data

- Navigate to the upload section
- Upload a CSV file containing your sales data
- The system will automatically parse and store the data

### 3. View Dashboard

- Access the dashboard to see:
  - Sales overview and trends
  - Product performance metrics
  - Sales predictions and forecasts
  - Recommendations

### 4. Generate Forecasts

- Use the forecasting feature to predict future sales
- Select forecast parameters (horizon, periods)
- View generated forecasts and visualizations

## CSV File Format

The system supports flexible CSV formats. Common column names are automatically mapped:

- **Transaction ID**: `transaction_id`, `order_id`, `id`
- **Product**: `product_name`, `product`, `item_name`
- **Category**: `category`, `product_category`
- **Price**: `price`, `unit_price`, `cost`
- **Quantity**: `quantity`, `qty`, `amount`
- **Customer**: `customer_name`, `customer`, `client_name`
- **Date**: `order_date`, `date`, `purchase_date`

See `README_CSV_UPLOAD.md` in the backend directory for complete column mapping details.

## Configuration

### Backend Configuration

- Database connection: `app/database.py`
- CORS origins: `app/main.py` (update `allow_origins` list)
- Authentication settings: `app/security.py`

### Frontend Configuration

- API endpoint: `src/lib/api.ts`
- Supabase config: `supabase/config.toml` (if using Supabase)

## Testing

### Backend API Testing

Use the interactive API documentation at `http://localhost:8000/docs` or use the provided `test_main.http` file.

### Example API Request

```bash
# Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

## API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **Pandas** - Data manipulation
- **Prophet** - Time series forecasting
- **XGBoost** - Machine learning
- **scikit-learn** - ML utilities

### Frontend
- **React** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components

## Additional Documentation

- [CSV Upload Guide](e-commerce-insights-backend/README_CSV_UPLOAD.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
