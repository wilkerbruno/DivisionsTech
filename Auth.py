"""auth.py — Login JWT para admin (MySQL)"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy import text
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_db
from config import JWT_SECRET, JWT_ALGO, JWT_EXPIRE_HOURS

router = APIRouter()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido")


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM admins WHERE username = :u"), {"u": form.username}
    ).fetchone()

    if not row or not pwd_ctx.verify(form.password, row.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_token({"sub": form.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(username: str = Depends(get_current_admin)):
    return {"username": username}