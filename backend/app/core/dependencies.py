


from fastapi import HTTPException, Request
from app.core.security import decode_token

async def get_user_id(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    payload = decode_token(token)
    try:
        return int(payload["sub"])
    except KeyError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_company_id(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    payload = decode_token(token)
    try:
        return int(payload["company_id"])
    except KeyError:
        raise HTTPException(status_code=401, detail="You do not have a company yet")