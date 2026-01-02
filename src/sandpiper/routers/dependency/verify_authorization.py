import os

from fastapi import Header, HTTPException, status


async def verify_authorization(authorization: str | None = Header(None)) -> str:
    """認証チェックdependency

    Args:
        authorization: Authorizationヘッダーの値

    Returns:
        認証済みのAuthorizationヘッダー値

    Raises:
        HTTPException: 認証失敗時(401)
    """
    if os.getenv("ENVIRONMENT") == "development":
        return "development"
    if authorization != "dummy":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization
