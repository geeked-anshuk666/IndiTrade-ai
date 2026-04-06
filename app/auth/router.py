from fastapi import APIRouter, Request

from app.config import settings
from app.models.schemas import TokenRequest, TokenResponse
from app.auth.jwt import create_token
from app.middleware.rate_limit import limiter

router = APIRouter()

@router.post("/auth/token", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
async def get_token(body: TokenRequest, request: Request):
    token = create_token(body.client_id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expiry_minutes * 60,
    )
