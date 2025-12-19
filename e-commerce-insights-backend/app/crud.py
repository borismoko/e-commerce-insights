from sqlalchemy.orm import Session
from . import models
from .security import hash_password


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, *, name: str, email: str, password: str, role: str = "analyst"):
    user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
