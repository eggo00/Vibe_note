"""
Content Analysis API
處理內容品質評分與分析
對應 tasks.md T032
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from ..utils.db import get_db
from ..models.data_source import DataSource, Block
from ..services.analyzer.quality_scorer import QualityScorer
from ..schemas.common import SuccessResponse, ErrorCode, create_error_response, create_success_response
from ..config import settings

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])


class AnalyzeRequest(BaseModel):
    """分析請求"""
    source_id: str


class AnalyzeResponse(BaseModel):
    """分析回應"""
    source_id: str
    total_blocks: int
    high_quality_blocks: int
    average_score: float
    threshold: float
    blocks: List[Dict[str, Any]]


@router.post("", response_model=SuccessResponse)
async def analyze_content(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    分析內容品質並過濾高品質 Blocks

    流程：
    1. 驗證 DataSource 存在
    2. 載入所有 Blocks
    3. 呼叫 QualityScorer 評分
    4. 更新資料庫的 quality_score
    5. 過濾 score >= threshold 的 blocks
    6. 返回分析結果

    錯誤代碼：
    - NOT_FOUND: 找不到 DataSource
    - AI_API_ERROR: OpenAI API 呼叫失敗
    - INTERNAL_ERROR: 其他錯誤
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

        # 2. 載入所有 Blocks
        blocks = db.query(Block).filter_by(source_id=request.source_id).order_by(Block.position_index).all()

        if not blocks:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    "該資料來源沒有任何內容區塊",
                    ErrorCode.VALIDATION_ERROR,
                    {"source_id": request.source_id}
                ).model_dump()
            )

        # 3. 呼叫 QualityScorer 評分
        try:
            scorer = QualityScorer()
            scoring_results = await scorer.score_blocks_batch(blocks)
        except ValueError as e:
            # OpenAI API key 未設定
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    f"AI 評分器初始化失敗：{str(e)}",
                    ErrorCode.AI_API_ERROR
                ).model_dump()
            )
        except Exception as e:
            # OpenAI API 呼叫失敗
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    f"AI 評分失敗：{str(e)}",
                    ErrorCode.AI_API_ERROR
                ).model_dump()
            )

        # 4. 更新資料庫的 quality_score
        score_map = {item["block_id"]: item["score"] for item in scoring_results}

        for block in blocks:
            if block.block_id in score_map:
                block.quality_score = score_map[block.block_id]

        db.commit()

        # 5. 過濾高品質 blocks（score >= threshold）
        high_quality_results = [
            item for item in scoring_results
            if item["is_high_quality"]
        ]

        # 6. 計算統計資料
        total_blocks = len(blocks)
        high_quality_count = len(high_quality_results)
        average_score = sum(item["score"] for item in scoring_results) / total_blocks if total_blocks > 0 else 0.0

        # 7. 更新 DataSource 的 quality_score（整體平均分）
        data_source.quality_score = average_score
        db.commit()

        # 8. 返回結果
        response_data = AnalyzeResponse(
            source_id=request.source_id,
            total_blocks=total_blocks,
            high_quality_blocks=high_quality_count,
            average_score=round(average_score, 2),
            threshold=settings.QUALITY_SCORE_THRESHOLD,
            blocks=high_quality_results
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


@router.get("/source/{source_id}/stats", response_model=SuccessResponse)
def get_analysis_stats(source_id: str, db: Session = Depends(get_db)):
    """
    取得指定 DataSource 的分析統計

    用於檢視已評分的結果（不重新評分）
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

    blocks = db.query(Block).filter_by(source_id=source_id).all()

    if not blocks:
        return create_success_response({
            "source_id": source_id,
            "total_blocks": 0,
            "high_quality_blocks": 0,
            "average_score": 0.0,
            "threshold": settings.QUALITY_SCORE_THRESHOLD
        })

    # 計算統計
    total_blocks = len(blocks)
    high_quality_blocks = sum(1 for b in blocks if b.quality_score >= settings.QUALITY_SCORE_THRESHOLD)
    average_score = sum(b.quality_score for b in blocks) / total_blocks if total_blocks > 0 else 0.0

    return create_success_response({
        "source_id": source_id,
        "url": data_source.url,
        "total_blocks": total_blocks,
        "high_quality_blocks": high_quality_blocks,
        "average_score": round(average_score, 2),
        "threshold": settings.QUALITY_SCORE_THRESHOLD,
        "block_type_distribution": _get_block_type_distribution(blocks),
        "score_distribution": _get_score_distribution(blocks)
    })


def _get_block_type_distribution(blocks: List[Block]) -> Dict[str, int]:
    """計算區塊類型分布"""
    distribution = {}
    for block in blocks:
        block_type = block.block_type
        distribution[block_type] = distribution.get(block_type, 0) + 1
    return distribution


def _get_score_distribution(blocks: List[Block]) -> Dict[str, int]:
    """計算分數分布（區間統計）"""
    distribution = {
        "0-20": 0,
        "21-40": 0,
        "41-60": 0,
        "61-80": 0,
        "81-100": 0
    }

    for block in blocks:
        score = block.quality_score
        if score <= 20:
            distribution["0-20"] += 1
        elif score <= 40:
            distribution["21-40"] += 1
        elif score <= 60:
            distribution["41-60"] += 1
        elif score <= 80:
            distribution["61-80"] += 1
        else:
            distribution["81-100"] += 1

    return distribution
