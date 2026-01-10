"""
文件管理 API
處理文件的讀取與更新
對應 tasks.md T036, T037
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from ..utils.db import get_db
from ..models.document import Document, Version
from ..schemas.common import SuccessResponse, ErrorCode, create_error_response, create_success_response

router = APIRouter(prefix="/api/doc", tags=["Documents"])


class DocumentResponse(BaseModel):
    """文件回應"""
    document_id: str
    title: str
    content: str  # 當前版本的 Markdown 內容
    current_version_id: str
    aggregate_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    version_count: int


class VersionInfo(BaseModel):
    """版本資訊"""
    version_id: str
    version_number: int
    created_at: datetime
    change_summary: Optional[str]
    content_preview: str  # 前 100 字


class UpdateDocumentRequest(BaseModel):
    """更新文件請求"""
    content: str = Field(..., description="更新後的 Markdown 內容")
    change_summary: Optional[str] = Field(None, description="變更摘要")


@router.get("/{document_id}", response_model=SuccessResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """
    取得文件詳情

    返回當前版本的完整內容
    對應 T036
    """
    # 1. 查詢文件
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

    # 2. 取得當前版本內容
    if not document.current_version_id:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                "文件沒有有效的版本",
                ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )

    current_version = db.query(Version).filter_by(version_id=document.current_version_id).first()
    if not current_version:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                "找不到當前版本",
                ErrorCode.VERSION_NOT_FOUND
            ).model_dump()
        )

    # 3. 統計版本數量
    version_count = db.query(Version).filter_by(document_id=document_id).count()

    # 4. 建構回應
    response_data = DocumentResponse(
        document_id=document.document_id,
        title=document.title,
        content=current_version.content,
        current_version_id=document.current_version_id,
        aggregate_score=document.aggregate_score,
        created_at=document.created_at,
        updated_at=document.updated_at,
        version_count=version_count
    )

    return create_success_response(response_data.model_dump())


@router.get("/{document_id}/versions", response_model=SuccessResponse)
def get_document_versions(document_id: str, db: Session = Depends(get_db)):
    """
    取得文件的所有版本歷史

    返回版本列表（按版本號降序）
    """
    # 1. 驗證文件存在
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

    # 2. 查詢所有版本
    versions = (
        db.query(Version)
        .filter_by(document_id=document_id)
        .order_by(Version.version_number.desc())
        .all()
    )

    # 3. 建構版本資訊列表
    version_list = [
        VersionInfo(
            version_id=v.version_id,
            version_number=v.version_number,
            created_at=v.created_at,
            change_summary=v.change_summary,
            content_preview=v.content[:100] + "..." if len(v.content) > 100 else v.content
        )
        for v in versions
    ]

    return create_success_response({
        "document_id": document_id,
        "title": document.title,
        "total_versions": len(version_list),
        "versions": [v.model_dump() for v in version_list]
    })


@router.get("/{document_id}/version/{version_id}", response_model=SuccessResponse)
def get_specific_version(document_id: str, version_id: str, db: Session = Depends(get_db)):
    """
    取得特定版本的完整內容
    """
    # 1. 驗證文件存在
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

    # 2. 查詢指定版本
    version = db.query(Version).filter_by(
        version_id=version_id,
        document_id=document_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                "找不到指定的版本",
                ErrorCode.VERSION_NOT_FOUND,
                {"version_id": version_id}
            ).model_dump()
        )

    # 3. 返回完整內容
    return create_success_response({
        "version_id": version.version_id,
        "version_number": version.version_number,
        "document_id": version.document_id,
        "content": version.content,
        "created_at": version.created_at.isoformat(),
        "change_summary": version.change_summary,
        "is_current": version.version_id == document.current_version_id
    })


@router.put("/{document_id}", response_model=SuccessResponse)
def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    db: Session = Depends(get_db)
):
    """
    更新文件內容

    建立新版本並設為當前版本
    對應 T037
    """
    try:
        # 1. 驗證文件存在
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

        # 2. 檢查內容是否有變更
        current_version = db.query(Version).filter_by(version_id=document.current_version_id).first()
        if current_version and current_version.content == request.content:
            # 內容沒變，不建立新版本
            return create_success_response({
                "message": "內容未變更，未建立新版本",
                "document_id": document_id,
                "current_version_id": document.current_version_id
            })

        # 3. 取得下一個版本號
        latest_version = (
            db.query(Version)
            .filter_by(document_id=document_id)
            .order_by(Version.version_number.desc())
            .first()
        )
        next_version_number = (latest_version.version_number + 1) if latest_version else 1

        # 4. 建立新版本
        new_version_id = str(uuid.uuid4())
        new_version = Version(
            version_id=new_version_id,
            document_id=document_id,
            version_number=next_version_number,
            content=request.content,
            created_at=datetime.utcnow(),
            change_summary=request.change_summary or f"版本 {next_version_number} - 手動更新"
        )
        db.add(new_version)

        # 5. 更新 Document
        document.current_version_id = new_version_id
        document.updated_at = datetime.utcnow()

        db.commit()

        # 6. 返回結果
        return create_success_response({
            "document_id": document_id,
            "version_id": new_version_id,
            "version_number": next_version_number,
            "title": document.title,
            "content_preview": request.content[:200] + "..." if len(request.content) > 200 else request.content,
            "change_summary": new_version.change_summary
        })

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"更新文件失敗：{str(e)}",
                ErrorCode.DOCUMENT_UPDATE_FAILED
            ).model_dump()
        )


@router.delete("/{document_id}", response_model=SuccessResponse)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    刪除文件及所有版本

    級聯刪除所有關聯的版本紀錄
    """
    # 1. 驗證文件存在
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

    try:
        # 2. 刪除文件（版本會自動級聯刪除）
        db.delete(document)
        db.commit()

        return create_success_response({
            "message": "文件已成功刪除",
            "document_id": document_id
        })

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"刪除文件失敗：{str(e)}",
                ErrorCode.INTERNAL_ERROR
            ).model_dump()
        )


@router.post("/{document_id}/restore/{version_id}", response_model=SuccessResponse)
def restore_version(
    document_id: str,
    version_id: str,
    db: Session = Depends(get_db)
):
    """
    恢復到指定版本

    將指定版本設為當前版本（不建立新版本紀錄）
    """
    # 1. 驗證文件存在
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

    # 2. 驗證版本存在
    version = db.query(Version).filter_by(
        version_id=version_id,
        document_id=document_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                "找不到指定的版本",
                ErrorCode.VERSION_NOT_FOUND,
                {"version_id": version_id}
            ).model_dump()
        )

    try:
        # 3. 更新當前版本指向
        document.current_version_id = version_id
        document.updated_at = datetime.utcnow()

        db.commit()

        return create_success_response({
            "message": f"已恢復到版本 {version.version_number}",
            "document_id": document_id,
            "version_id": version_id,
            "version_number": version.version_number,
            "content_preview": version.content[:200] + "..." if len(version.content) > 200 else version.content
        })

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"恢復版本失敗：{str(e)}",
                ErrorCode.VERSION_RESTORE_FAILED
            ).model_dump()
        )
