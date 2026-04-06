import asyncio
from collections import defaultdict
from datetime import datetime, timezone

_store: dict[str, list] = defaultdict(list)
_lock = asyncio.Lock()
MAX_PER_CLIENT = 50

async def record(client_id: str, sector: str, status: str):
    async with _lock:
        history = _store[client_id]
        history.append({
            "sector": sector,
            "ts": datetime.now(timezone.utc).isoformat(),
            "status": status,
        })
        if len(history) > MAX_PER_CLIENT:
            _store[client_id] = history[-MAX_PER_CLIENT:]

async def get_history(client_id: str) -> list:
    async with _lock:
        return list(_store.get(client_id, []))
