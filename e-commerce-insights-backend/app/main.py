from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from .auth import router as auth_router
from .upload import router as upload_router
from .database import Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce Insights API", version="0.1.0")

# Add CORS middleware FIRST - it must be before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log detailed validation errors and return 422 with details"""
    logger.error(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code} for {request.method} {request.url.path}")
        return response
    except Exception as e:
        logger.error(f"Error processing {request.method} {request.url.path}: {str(e)}", exc_info=True)
        raise

app.include_router(auth_router)
app.include_router(upload_router)

@app.get("/secure/ping")
def secure_ping(user=auth_router.dependencies[0] if False else None):
    return {"ok": True}