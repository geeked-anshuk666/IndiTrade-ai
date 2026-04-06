import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse

from app.auth.jwt import verify_token
from app.middleware.rate_limit import limiter
from app.services import search, gemini, report
from app.session import store
from app.config import settings
from app.routers.validate import clean_sector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/analyze/{sector}", response_class=PlainTextResponse)
@limiter.limit(settings.rate_limit_analyze)
async def analyze(sector: str, request: Request, client_id: str = Depends(verify_token)):
    clean = clean_sector(sector)
    logger.info("analyze | sector=%s | client=%s", clean, client_id)

    await store.record(client_id, clean, "started")

    market_data = await search.fetch_market_data(clean)
    market_data = search.trim_context(market_data)

    analysis = await gemini.analyze(clean, market_data)
    md = report.build_report(clean, client_id, analysis)

    await store.record(client_id, clean, "done")
    return md

@router.get("/health")
@limiter.limit("30/minute")
async def health(request: Request):
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}
