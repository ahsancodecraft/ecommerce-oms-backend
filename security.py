from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Secret key token sign karne ke liye (production mein yeh environment variable hoti hai)
SECRET_KEY = "my_super_secret_key_oms_project"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Plain password ko secure hash mein convert karta hai (72-byte limit fix ke sath)."""
    # Bcrypt ki 72-bytes limit ko handle karne ke liye password ko safe tarike se truncate karte hain
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """Check karta hai ke entered password hash se match hota hai ya nahi."""
  return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  """User ke liye JWT access token generate karta hai."""
  to_encode = data.copy()
  expire = datetime.utcnow() + (
      expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  )
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)