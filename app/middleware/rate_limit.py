from slowapi import Limiter
from slowapi.util import get_remote_address

def get_rate_key(request):
    # use client_id from JWT if available, else fall back to IP
    from app.auth.jwt import extract_client_id
    client_id = extract_client_id(request)
    return client_id or request.client.host

limiter = Limiter(key_func=get_rate_key)
