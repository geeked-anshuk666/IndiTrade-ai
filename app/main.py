import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from app.middleware.security_headers import SecurityHeaders
from app.middleware.rate_limit import limiter
from app.auth.router import router as auth_router
from app.routers.analyze import router as analyze_router

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s"
)

app = FastAPI(
    title="Trade Opportunities API",
    description="Market analysis for Indian trade sectors",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeaders)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(analyze_router)
