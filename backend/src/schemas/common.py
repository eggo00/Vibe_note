"""
API 統一回應格式
對應 tasks.md T020, constitution.md §API 設計規範
"""
from typing import Any, Optional, Dict
from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """
    統一錯誤回應格式

    範例：
        {
            "error": "找不到指定的文件",
            "code": "DOCUMENT_NOT_FOUND",
            "details": {"document_id": "abc123"}
        }
    """
    error: str  # 錯誤描述（使用者友善訊息）
    code: str  # 錯誤代碼（全大寫，底線分隔）
    details: Optional[Dict[str, Any]] = None  # 額外錯誤細節（可選）

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "無法爬取 Notion 頁面，請確認 URL 是否正確",
                "code": "NOTION_SCRAPE_FAILED",
                "details": {"url": "https://notion.so/invalid", "status_code": 404}
            }
        }
    )


class SuccessResponse(BaseModel):
    """
    統一成功回應格式

    範例：
        {
            "success": true,
            "data": {...}
        }
    """
    success: bool = True
    data: Any  # 實際資料（可以是 dict, list, str 等）

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {"document_id": "550e8400-e29b-41d4-a716-446655440000", "title": "測試筆記"}
            }
        }
    )


# 預定義錯誤代碼常數
class ErrorCode:
    """預定義的 API 錯誤代碼"""

    # 通用錯誤 (1xxx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"

    # 文件相關 (2xxx)
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DOCUMENT_CREATE_FAILED = "DOCUMENT_CREATE_FAILED"
    DOCUMENT_UPDATE_FAILED = "DOCUMENT_UPDATE_FAILED"
    VERSION_NOT_FOUND = "VERSION_NOT_FOUND"
    VERSION_RESTORE_FAILED = "VERSION_RESTORE_FAILED"

    # 爬蟲相關 (3xxx)
    SCRAPE_FAILED = "SCRAPE_FAILED"
    NOTION_SCRAPE_FAILED = "NOTION_SCRAPE_FAILED"
    BLOG_SCRAPE_FAILED = "BLOG_SCRAPE_FAILED"
    GITHUB_SCRAPE_FAILED = "GITHUB_SCRAPE_FAILED"
    SCRAPE_RATE_LIMITED = "SCRAPE_RATE_LIMITED"
    SCRAPE_FORBIDDEN = "SCRAPE_FORBIDDEN"  # robots.txt 禁止
    SCRAPE_TIMEOUT = "SCRAPE_TIMEOUT"

    # 內容分析相關 (4xxx)
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    QUALITY_SCORE_FAILED = "QUALITY_SCORE_FAILED"
    NO_HIGH_QUALITY_BLOCKS = "NO_HIGH_QUALITY_BLOCKS"  # 所有 blocks 評分 < 60

    # 筆記生成相關 (5xxx)
    GENERATION_FAILED = "GENERATION_FAILED"
    GENERATION_TOO_SIMILAR = "GENERATION_TOO_SIMILAR"  # 相似度 > 0.7
    AI_API_ERROR = "AI_API_ERROR"  # AI API 呼叫失敗（通用）
    OPENAI_API_ERROR = "OPENAI_API_ERROR"
    OPENAI_RATE_LIMIT = "OPENAI_RATE_LIMIT"

    # 風格分析相關 (6xxx)
    STYLE_ANALYSIS_FAILED = "STYLE_ANALYSIS_FAILED"
    STYLE_PROFILE_NOT_FOUND = "STYLE_PROFILE_NOT_FOUND"

    # 匯出相關 (7xxx)
    EXPORT_FAILED = "EXPORT_FAILED"
    EXPORT_FORMAT_UNSUPPORTED = "EXPORT_FORMAT_UNSUPPORTED"
    EXPORT_FILE_NOT_FOUND = "EXPORT_FILE_NOT_FOUND"


def create_error_response(
    error_message: str,
    error_code: str = ErrorCode.INTERNAL_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    建立錯誤回應物件

    Args:
        error_message: 使用者友善的錯誤訊息
        error_code: 錯誤代碼（使用 ErrorCode 常數）
        details: 額外錯誤細節（可選）

    Returns:
        ErrorResponse 物件

    範例：
        >>> error = create_error_response(
        ...     "文件不存在",
        ...     ErrorCode.DOCUMENT_NOT_FOUND,
        ...     {"document_id": "abc123"}
        ... )
    """
    return ErrorResponse(
        error=error_message,
        code=error_code,
        details=details
    )


def create_success_response(data: Any) -> SuccessResponse:
    """
    建立成功回應物件

    Args:
        data: 要回傳的資料（dict, list, str 等）

    Returns:
        SuccessResponse 物件

    範例：
        >>> response = create_success_response({"document_id": "123", "title": "測試"})
    """
    return SuccessResponse(success=True, data=data)


def error_dict(
    error_message: str,
    error_code: str = ErrorCode.INTERNAL_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    直接返回錯誤 dict（不使用 Pydantic model）

    Args:
        error_message: 錯誤訊息
        error_code: 錯誤代碼
        details: 額外細節

    Returns:
        錯誤 dict

    範例：
        >>> return JSONResponse(
        ...     status_code=404,
        ...     content=error_dict("找不到文件", ErrorCode.DOCUMENT_NOT_FOUND)
        ... )
    """
    response = {
        "error": error_message,
        "code": error_code
    }
    if details is not None:
        response["details"] = details
    return response


def success_dict(data: Any) -> Dict[str, Any]:
    """
    直接返回成功 dict（不使用 Pydantic model）

    Args:
        data: 回傳資料

    Returns:
        成功 dict

    範例：
        >>> return success_dict({"user_id": 123, "name": "Alice"})
    """
    return {
        "success": True,
        "data": data
    }
