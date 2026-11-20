from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import OrderLog
from app.schemas import OrderLogResponse
from app.auth import verify_api_key

router = APIRouter(prefix="/api/logs", tags=["Logs"])

@router.get("", response_model=List[OrderLogResponse])
async def list_all_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    logs = db.query(OrderLog).order_by(OrderLog.log_id.desc()).limit(limit).all()
    return logs
