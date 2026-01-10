"""
Notion API 端點
處理 Notion 頁面爬取與匯入
對應 tasks.md T030
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ..utils.db import get_db
from ..models.data_source import DataSource, Block
from ..models.document import Document
from ..services.scraper.notion import NotionScraper
from ..services.scraper.rate_limiter import RateLimiter
from ..schemas.common import SuccessResponse, ErrorCode, create_error_response, create_success_response
from ..config import settings

router = APIRouter(prefix="/api/notion", tags=["Notion"])

# 全域 RateLimiter 實例
rate_limiter = RateLimiter(requests_per_second=settings.RATE_LIMIT_PER_SECOND)


class NotionImportRequest(BaseModel):
    """Notion 匯入請求"""
    url: HttpUrl
    document_id: str | None = None  # 可選：關聯到現有文件


class NotionImportResponse(BaseModel):
    """Notion 匯入回應"""
    source_id: str
    document_id: str | None
    url: str
    blocks_count: int
    page_title: str | None


@router.post("/import", response_model=SuccessResponse)
async def import_notion_page(
    request: NotionImportRequest,
    db: Session = Depends(get_db)
):
    """
    匯入 Notion 公開頁面

    流程：
    1. 檢查 robots.txt
    2. 爬取頁面內容
    3. 儲存 DataSource 與 Blocks
    4. 返回結果

    錯誤代碼：
    - SCRAPE_FORBIDDEN: robots.txt 禁止
    - NOTION_SCRAPE_FAILED: 爬取失敗
    - SCRAPE_RATE_LIMITED: 速率限制
    """
    scraper = NotionScraper()
    url_str = str(request.url)

    try:
        # 1. 檢查 robots.txt
        is_allowed, error_msg = await scraper.check_robots_txt(url_str)
        if not is_allowed:
            raise HTTPException(
                status_code=403,
                detail=create_error_response(
                    error_msg or "robots.txt 禁止爬取此頁面",
                    ErrorCode.SCRAPE_FORBIDDEN,
                    {"url": url_str}
                ).model_dump()
            )

        # 2. 速率限制
        await rate_limiter.wait_async()

        # 3. 爬取頁面
        blocks, error_msg = await scraper.scrape_page(url_str)
        if error_msg:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    f"爬取失敗：{error_msg}",
                    ErrorCode.NOTION_SCRAPE_FAILED,
                    {"url": url_str}
                ).model_dump()
            )

        if not blocks:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "頁面中沒有找到任何內容",
                    ErrorCode.NOTION_SCRAPE_FAILED,
                    {"url": url_str}
                ).model_dump()
            )

        # 4. 儲存 DataSource
        source_id = str(uuid.uuid4())
        data_source = DataSource(
            source_id=source_id,
            document_id=request.document_id,  # 可能為 None
            source_type="notion",
            url=url_str,
            fetched_at=datetime.utcnow(),
            raw_content_snapshot=None,  # 可選：儲存原始 HTML
            quality_score=None,  # 後續分析時填入
            meta_data='{"blocks_count": ' + str(len(blocks)) + '}'
        )
        db.add(data_source)
        db.flush()  # 確保 source_id 可用

        # 5. 儲存 Blocks（品質評分後續由 analyzer 填入）
        db_blocks = []
        for block in blocks:
            db_block = Block(
                block_id=f"{source_id}-{block.block_id}",
                source_id=source_id,
                block_type=block.block_type,
                text_content=block.text_content,
                code_language=block.code_language,
                hierarchy_level=block.hierarchy_level,
                position_index=block.position_index,
                quality_score=0.0  # 預設值，後續填入
            )
            db_blocks.append(db_block)

        db.add_all(db_blocks)
        db.commit()

        # 6. 返回結果
        response_data = NotionImportResponse(
            source_id=source_id,
            document_id=request.document_id,
            url=url_str,
            blocks_count=len(blocks),
            page_title=None  # 可選：提取標題
        )

        return create_success_response(response_data.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"內部錯誤：{str(e)}",
                ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.get("/source/{source_id}/blocks", response_model=SuccessResponse)
def get_source_blocks(source_id: str, db: Session = Depends(get_db)):
    """
    取得指定 DataSource 的所有 Blocks

    用於檢視爬取結果
    """
    data_source = db.query(DataSource).filter_by(source_id=source_id).first()
    if not data_source:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                "找不到指定的資料來源",
                ErrorCode.NOT_FOUND,
                {"source_id": source_id}
            ).model_dump()
        )

    blocks = db.query(Block).filter_by(source_id=source_id).order_by(Block.position_index).all()

    blocks_data = [
        {
            "block_id": b.block_id,
            "block_type": b.block_type,
            "text_content": b.text_content[:200] + "..." if len(b.text_content) > 200 else b.text_content,
            "code_language": b.code_language,
            "hierarchy_level": b.hierarchy_level,
            "position_index": b.position_index,
            "quality_score": b.quality_score
        }
        for b in blocks
    ]

    return create_success_response({
        "source": {
            "source_id": data_source.source_id,
            "url": data_source.url,
            "source_type": data_source.source_type,
            "fetched_at": data_source.fetched_at.isoformat() if data_source.fetched_at else None
        },
        "blocks": blocks_data,
        "total_blocks": len(blocks_data)
    })
