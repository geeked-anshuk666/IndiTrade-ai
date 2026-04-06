def build_prompt(sector: str, market_data: str) -> str:
    return f"""Analyze the following market data for the **{sector}** sector in India.

## Raw Market Data

{market_data}

## Report Requirements

Generate a markdown trade opportunity report with exactly these sections:

1. **Executive Summary** — 2-3 sentences covering the current state and headline opportunity
2. **Current Market Trends** — 3-5 bullet points with specific data points where available
3. **Key Trade Opportunities** — 3-5 opportunities with brief rationale for each
4. **Target Export Markets** — Top 3 countries with reasoning (demand, existing relationships, growth)
5. **Challenges & Risk Factors** — 2-3 items (regulatory, competitive, supply chain)
6. **Recommended Next Steps** — 3 concrete, actionable steps for an Indian exporter
7. **Data Sources** — List the source URLs from the raw data above

Use INR/USD figures where available. Be specific — avoid generic statements like "significant growth potential".
If market data is limited, say so clearly rather than speculating."""
