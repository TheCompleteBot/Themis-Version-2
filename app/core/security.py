# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Security configuration
class SecurityConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret-key-keep-it-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Create settings instance
settings = SecurityConfig()

class SecurityUtils:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta
            if expires_delta
            else timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not create access token: {str(e)}"
            )

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify JWT access token."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token validation error: {str(e)}"
            )

# Create a single instance to be imported by other modules
security = SecurityUtils()

# Test the functionality if run directly
if __name__ == "__main__":
    try:
        # Create a test token
        test_data = {"sub": "user@example.com"}
        token = security.create_access_token(test_data)
        print(f"Generated token: {token}")
        
        # Decode the token
        decoded = security.decode_access_token(token)
        print(f"Decoded payload: {decoded}")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
