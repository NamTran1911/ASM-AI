from typing import Optional
from fastapi import Header, Query, HTTPException, status
from app.config import settings

def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = Query(None, alias="api_key")
):
    token = x_api_key or api_key
    
    # Neu he thong bat buoc xac thuc API Key
    if settings.REQUIRE_API_KEY:
        if not token or token != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key khong hop le hoac bi thieu."
            )
    return token
