from pydantic import BaseModel, constr

class TokenRequest(BaseModel):
    client_id: constr(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9\-]+$")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class ErrorResponse(BaseModel):
    detail: str
