from datetime import datetime, timezone

def build_report(sector: str, client_id: str, gemini_output: str) -> str:
    now = datetime.now(timezone.utc)
    header = f"""# Trade Opportunities Report: {sector.title()}

**Generated:** {now.strftime("%Y-%m-%d %H:%M UTC")}
**Session:** {client_id}
**Sector:** {sector}

---

"""
    return header + gemini_output
