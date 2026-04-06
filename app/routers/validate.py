import re
from fastapi import HTTPException

_SECTOR_RE = re.compile(r"^[a-zA-Z\s\-]{2,50}$")

KNOWN_SECTORS = {
    "pharmaceuticals", "technology", "agriculture", "textiles",
    "automotive", "chemicals", "electronics", "steel",
    "renewable energy", "food processing", "defence", "gems",
}

def clean_sector(raw: str) -> str:
    s = raw.strip()
    if not _SECTOR_RE.match(s):
        raise HTTPException(
            status_code=400,
            detail="sector must be 2-50 letters only (no numbers or special chars)"
        )
    return s.lower()
