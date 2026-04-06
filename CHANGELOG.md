# Changelog

## [0.1.0] - 2025-04-06

### Added
- initial project layout and config
- environment variable parsing via pydantic-settings
- requirements.txt, .gitignore, .env.example

### Added
- jwt auth with guest token endpoint
- security headers middleware applied to all requests
- slowapi rate limiting logic per client_id

### Added
- sector input validation (regex logic and known sectors lookup)
- in-memory session store with asyncio.Lock for sync safety

### Added
- duckduckgo search service (threaded via asyncio run_in_executor)
- 1s sleep logic added to Search API to prevent soft bans

### Added
- gemini client configured with error handling for 429 and 500
- trade analysis prompt template ensuring 7-section markdown
- report assembler prepending timestamp and session header

### Added
- analyze route explicitly wired end to end
- fastapi app assembly linking all routers and middleware
- local dockerfile and render.yaml ready for deployment
- complete markdown documentation suite inside docs/

### Fixed
- Fixed potential synchronous blocking on DDG library by leveraging run_in_executor
