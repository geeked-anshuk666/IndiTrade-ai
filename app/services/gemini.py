import asyncio
import logging
import time

import google.generativeai as genai
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.gemini_api_key)

_model = genai.GenerativeModel(
    model_name="gemini-3.1-flash-lite-preview",
    generation_config=genai.GenerationConfig(
        temperature=0.3,
        max_output_tokens=2048,
    ),
    system_instruction=(
        "You are a trade analyst specializing in Indian export markets. "
        "Analyze market data and identify concrete trade opportunities for Indian businesses. "
        "Respond only with structured markdown. Do not discuss unrelated topics."
    ),
)


async def analyze(sector: str, market_data: str) -> str:
    from app.prompts.trade_analysis import build_prompt

    prompt = build_prompt(sector, market_data)
    start = time.monotonic()

    loop = asyncio.get_running_loop()
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Shift CPU-bound/blocking call to executor
            response = await loop.run_in_executor(None, lambda: _model.generate_content(prompt))
            elapsed = time.monotonic() - start
            logger.info("gemini done | sector=%s | %.2fs", sector, elapsed)
            return response.text

        except Exception as e:
            elapsed = time.monotonic() - start
            err_str = str(e).lower()
            
            # Identify retriable errors (Quota/Rate Limit/Transient 503)
            is_retriable = any(x in err_str for x in ["429", "quota", "503", "unavailable", "busy"])
            
            if is_retriable and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning("gemini transient error | sector=%s | attempt=%d | wait=%ds | err=%s", 
                               sector, attempt + 1, wait_time, e)
                await asyncio.sleep(wait_time)
                continue

            # Non-retriable or final attempt failed
            if "invalid api key" in err_str or "api_key" in err_str:
                logger.error("gemini bad api key")
                raise HTTPException(500, "AI service misconfigured — check server logs")

            if is_retriable:
                logger.error("gemini persistent rate limit | sector=%s | err=%s", sector, e)
                raise HTTPException(503, "AI service temporarily busy — please try again in a moment")

            logger.error("gemini failed | sector=%s | err=%s | %.2fs", sector, e, elapsed)
            raise HTTPException(500, "analysis failed — please try again later")
