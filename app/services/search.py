import asyncio
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

async def fetch_market_data(sector: str) -> str:
    queries = [
        f"{sector} India export trade opportunities 2025",
        f"{sector} India market growth trends recent news",
    ]
    snippets = []

    loop = asyncio.get_running_loop()
    for q in queries:
        try:
            results = await loop.run_in_executor(
                None, lambda q_inner=q: list(DDGS().text(q_inner, max_results=5, region="in-en"))
            )
            for r in results:
                snippets.append(f"### {r['title']}\n{r['body']}\n_Source: {r['href']}_")
        except Exception as e:
            logger.warning("DDG search failed | query=%r | err=%s", q, e)

        await asyncio.sleep(1)  # DDG rate-limits hard without this

    if not snippets:
        return "No recent market data found for this sector."
    return "\n\n---\n\n".join(snippets)


def trim_context(text: str, max_chars: int = 16000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n_[...search results truncated]_"
