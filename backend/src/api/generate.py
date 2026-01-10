"""
筆記生成 API
處理筆記生成請求，建立 Document 與 Version
對應 tasks.md T035
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from ..utils.db import get_db
from ..models.data_source import DataSource, Block
from ..models.document import Document, Version
from ..services.generator.note_generator import NoteGenerator
from ..schemas.common import SuccessResponse, ErrorCode, create_error_response, create_success_response
from ..config import settings

router = APIRouter(prefix="/api/generate", tags=["Generation"])


class GenerateRequest(BaseModel):
    """筆記生成請求"""
    source_id: str = Field(..., description="資料來源 ID")
    project_context: Optional[str] = Field(None, description="專案背景資訊（對話紀錄、README 等）")
    title: Optional[str] = Field(None, description="筆記標題（若不提供則自動生成）")
    use_custom_style: bool = Field(False, description="是否使用自訂風格（若為 True 需提供 style_profile_id）")
    style_profile_id: Optional[str] = Field(None, description="風格模板 ID（選用）")


class GenerateResponse(BaseModel):
    """筆記生成回應"""
    document_id: str
    version_id: str
    title: str
    content_preview: str  # 前 200 字
    total_blocks_used: int
    quality_score: float


@router.post("", response_model=SuccessResponse)
async def generate_note(
    request: GenerateRequest,
    db: Session = Depends(get_db)
):
    """
    生成筆記

    流程：
    1. 驗證 DataSource 存在且已評分
    2. 載入高品質 blocks（score >= threshold）
    3. 呼叫 NoteGenerator 生成 Markdown 筆記
    4. 建立 Document 與 Version 紀錄
    5. 返回生成結果

    錯誤代碼：
    - NOT_FOUND: 找不到 DataSource
    - VALIDATION_ERROR: 尚未進行品質評分
    - NO_HIGH_QUALITY_BLOCKS: 沒有高品質 blocks（score >= 60）
    - GENERATION_FAILED: 筆記生成失敗
    - AI_API_ERROR: OpenAI API 呼叫失敗
    """
    try:
        # 1. 驗證 DataSource 存在
        data_source = db.query(DataSource).filter_by(source_id=request.source_id).first()
        if not data_source:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    "找不到指定的資料來源",
                    ErrorCode.NOT_FOUND,
                    {"source_id": request.source_id}
                ).model_dump()
            )

        # 2. 檢查是否已評分
        if data_source.quality_score is None:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "該資料來源尚未進行品質評分，請先呼叫 /api/analyze",
                    ErrorCode.VALIDATION_ERROR,
                    {"source_id": request.source_id}
                ).model_dump()
            )

        # 3. 載入高品質 blocks
        high_quality_blocks = (
            db.query(Block)
            .filter(
                Block.source_id == request.source_id,
                Block.quality_score >= settings.QUALITY_SCORE_THRESHOLD
            )
            .order_by(Block.position_index)
            .all()
        )

        if not high_quality_blocks:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    f"沒有達到品質門檻（>= {settings.QUALITY_SCORE_THRESHOLD}）的內容區塊",
                    ErrorCode.NO_HIGH_QUALITY_BLOCKS,
                    {
                        "source_id": request.source_id,
                        "threshold": settings.QUALITY_SCORE_THRESHOLD
                    }
                ).model_dump()
            )

        # 4. 取得或建立風格模板
        style_template = None
        if request.use_custom_style and request.style_profile_id:
            # TODO: 從資料庫載入 StyleProfile（Phase 4 實作）
            # style_profile = db.query(StyleProfile).filter_by(profile_id=request.style_profile_id).first()
            # if style_profile:
            #     style_template = json.loads(style_profile.style_data)
            pass

        # 若無自訂風格，使用預設模板（這裡先建立 generator 取得預設值）
        try:
            generator = NoteGenerator()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    f"筆記生成器初始化失敗：{str(e)}",
                    ErrorCode.AI_API_ERROR
                ).model_dump()
            )

        if not style_template:
            style_template = generator.get_default_style_template()

        # 5. 生成筆記內容
        try:
            markdown_content = await generator.generate_note(
                blocks=high_quality_blocks,
                project_context=request.project_context,
                style_template=style_template
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    f"筆記生成失敗：{str(e)}",
                    ErrorCode.GENERATION_FAILED
                ).model_dump()
            )

        # 6. 生成標題（若未提供）
        if not request.title:
            try:
                title = await generator.generate_summary(high_quality_blocks, max_length=100)
            except Exception:
                # 標題生成失敗時使用預設值
                title = f"技術筆記 - {datetime.utcnow().strftime('%Y-%m-%d')}"
        else:
            title = request.title

        # 7. 建立 Document
        document_id = str(uuid.uuid4())
        document = Document(
            document_id=document_id,
            title=title,
            aggregate_score=data_source.quality_score or 0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            current_version_id=None  # 稍後更新
        )
        db.add(document)
        db.flush()  # 確保 document_id 可用

        # 8. 建立 Version（第一版）
        version_id = str(uuid.uuid4())
        version = Version(
            version_id=version_id,
            document_id=document_id,
            version_number=1,
            content=markdown_content,
            created_at=datetime.utcnow(),
            change_summary="初始版本 - AI 自動生成"
        )
        db.add(version)
        db.flush()

        # 9. 更新 Document 的 current_version_id 和關聯 DataSource
        document.current_version_id = version_id
        data_source.document_id = document_id
        db.commit()

        # 10. 返回結果
        response_data = GenerateResponse(
            document_id=document_id,
            version_id=version_id,
            title=title,
            content_preview=markdown_content[:200] + "..." if len(markdown_content) > 200 else markdown_content,
            total_blocks_used=len(high_quality_blocks),
            quality_score=data_source.quality_score or 0.0
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


@router.post("/regenerate/{document_id}", response_model=SuccessResponse)
async def regenerate_note(
    document_id: str,
    project_context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    重新生成筆記（建立新版本）

    使用相同的資料來源重新生成筆記內容
    """
    # 1. 驗證 Document 存在
    document = db.query(Document).filter_by(document_id=document_id).first()
    if not document:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                "找不到指定的文件",
                ErrorCode.DOCUMENT_NOT_FOUND,
                {"document_id": document_id}
            ).model_dump()
        )

    # 2. 取得資料來源（使用第一個關聯的 DataSource）
    if not document.data_sources:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                "該文件沒有關聯的資料來源",
                ErrorCode.VALIDATION_ERROR
            ).model_dump()
        )

    source_id = document.data_sources[0].source_id

    # 3. 載入高品質 blocks
    high_quality_blocks = (
        db.query(Block)
        .filter(
            Block.source_id == source_id,
            Block.quality_score >= settings.QUALITY_SCORE_THRESHOLD
        )
        .order_by(Block.position_index)
        .all()
    )

    if not high_quality_blocks:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                "沒有可用的高品質內容區塊",
                ErrorCode.NO_HIGH_QUALITY_BLOCKS
            ).model_dump()
        )

    # 4. 重新生成
    try:
        generator = NoteGenerator()
        style_template = generator.get_default_style_template()

        markdown_content = await generator.generate_note(
            blocks=high_quality_blocks,
            project_context=project_context,
            style_template=style_template
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"筆記重新生成失敗：{str(e)}",
                ErrorCode.GENERATION_FAILED
            ).model_dump()
        )

    # 5. 建立新版本
    latest_version = (
        db.query(Version)
        .filter_by(document_id=document_id)
        .order_by(Version.version_number.desc())
        .first()
    )
    next_version_number = (latest_version.version_number + 1) if latest_version else 1

    version_id = str(uuid.uuid4())
    new_version = Version(
        version_id=version_id,
        document_id=document_id,
        version_number=next_version_number,
        content=markdown_content,
        created_at=datetime.utcnow(),
        change_summary="重新生成 - AI 自動生成"
    )
    db.add(new_version)

    # 6. 更新 Document
    document.current_version_id = version_id
    document.updated_at = datetime.utcnow()
    db.commit()

    return create_success_response({
        "document_id": document_id,
        "version_id": version_id,
        "version_number": next_version_number,
        "content_preview": markdown_content[:200] + "..." if len(markdown_content) > 200 else markdown_content
    })
