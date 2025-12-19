from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

from .database import get_db
from . import schemas, crud, models
from .security import verify_password, create_access_token, decode_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise unauthorized
    except Exception:
        raise unauthorized
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise unauthorized
    return user


@router.post("/register", response_model=schemas.UserRead, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Register attempt: email={payload.email}")
    try:
        if crud.get_user_by_email(db, email=payload.email):
            logger.warning(f"Email already registered: {payload.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        user = crud.create_user(db, name=payload.name, email=payload.email, password=payload.password)
        logger.info(f"User created successfully: {user.email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in register: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt: username={form.username}")
    try:
        user = crud.get_user_by_email(db, form.username)
        if not user or not verify_password(form.password, user.password_hash):
            logger.warning(f"Invalid credentials for: {form.username}")
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        token = create_access_token({"sub": user.email, "role": user.role})
        logger.info(f"Login successful: {user.email}")
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=schemas.UserRead)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
