from datetime import datetime, timedelta, timezone
from fastapi import Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

# Use HTTPBearer for a cleaner Swagger UI (Token-only input)
bearer_scheme = HTTPBearer()

def create_token(client_id: str) -> str:
    expires_delta = timedelta(minutes=settings.jwt_expiry_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": client_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt

def verify_token(auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    token = auth.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        client_id = payload.get("sub")
        if client_id is None:
            raise HTTPException(status_code=401, detail="invalid or expired token")
        return client_id
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid or expired token")

def extract_client_id(request: Request) -> str | None:
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return None
    token = token[7:]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None
