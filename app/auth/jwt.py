from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models
from app.schemas import TokenData
from dotenv import load_dotenv
from pathlib import Path
import os   

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) :
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "could not validate credentials",
        headers = {"WWW-Authenticate":"Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email:str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email = email)
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(models.User).where(models.User.email==token_data.email))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


    