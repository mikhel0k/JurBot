


from fastapi import HTTPException, Request
from app.core.security import decode_token

async def get_user_id(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    payload = decode_token(token)
    return int(payload["sub"])