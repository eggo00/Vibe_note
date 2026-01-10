"""
健康檢查 API
對應 tasks.md T023
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..utils.db import get_db
from ..schemas.common import SuccessResponse, create_success_response
from ..config import Settings, get_settings
import time

router = APIRouter(prefix="", tags=["Health"])


@router.get("/health", response_model=SuccessResponse)
def health_check(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> SuccessResponse:
    """
    健康檢查端點

    驗證：
    - API 伺服器運作正常
    - 資料庫連線正常

    Returns:
        成功回應，包含狀態資訊
    """
    # 測試資料庫連線
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return create_success_response({
        "status": "ok",
        "timestamp": time.time(),
        "database": db_status,
        "environment": "production" if settings.is_production else "development"
    })
