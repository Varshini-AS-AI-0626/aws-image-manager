import os
from typing import Any
from functools import wraps
from fastapi import Request
from dataclasses import asdict
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from ..database.connections import MakeConnections

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


connection_obj = MakeConnections()
client = connection_obj.client

db = client["DO_console"]
users_collection = db["users"]
logapi = db["apilogs"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def admin_required(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    user = users_collection.find_one({"username": username})

    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    return user


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def convert_dataclass_to_dict(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: convert_dataclass_to_dict(value) for key, value in obj.items()}
    elif hasattr(obj, "__dict__"):
        return convert_dataclass_to_dict(obj.__dict__)
    elif isinstance(obj, list):
        return [convert_dataclass_to_dict(item) for item in obj]
    elif hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    else:
        return obj


def insert_logs(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        converted_dict = convert_dataclass_to_dict(kwargs)
        token = converted_dict["token"]
        del converted_dict["token"]
        request_data = {
            "method": request.method,
            "path": func.__name__,
            "body": dict(converted_dict),
            "token": jwt.decode(token, algorithms=ALGORITHM, key=SECRET_KEY),
            "dtcollected": datetime.now(),
        }
        response = await func(request, *args, **kwargs)
        logapi.insert_one(request_data)
        return response

    return wrapper
