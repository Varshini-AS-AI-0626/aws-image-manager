from passlib.context import CryptContext
from pymongo import MongoClient

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


client = MongoClient("")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
