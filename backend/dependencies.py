from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.services.auth_service import verify_access_token


security = HTTPBearer()


def get_current_username(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:

    token = credentials.credentials

    try:
        username = verify_access_token(token)
        return username

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )