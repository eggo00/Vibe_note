"""
Analyze API 測試
驗證內容分析與品質評分 API
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.main import app
from src.utils.db import get_db, Base
from src.models.data_source import DataSource, Block


# 測試資料庫設定
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """為每個測試建立獨立的 engine"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """為每個測試建立獨立的資料庫 session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="function")
def test_client(test_engine):
    """為每個測試建立獨立的 TestClient"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_data_source(test_db):
    """建立範例 DataSource"""
    source = DataSource(
        source_id="test-source-1",
        source_type="notion",
        url="https://notion.so/test-page",
        fetched_at=datetime.utcnow(),
        quality_score=None
    )
    test_db.add(source)
    test_db.commit()
    return source


@pytest.fixture
def sample_blocks(test_db, sample_data_source):
    """建立範例 Blocks"""
    blocks = [
        Block(
            block_id="block-1",
            source_id=sample_data_source.source_id,
            block_type="heading",
            text_content="React Hooks 教學",
            hierarchy_level=1,
            position_index=0,
            quality_score=0.0
        ),
        Block(
            block_id="block-2",
            source_id=sample_data_source.source_id,
            block_type="paragraph",
            text_content="React Hooks 是 React 16.8 引入的新特性，允許在函式組件中使用 state 和生命週期特性。",
            position_index=1,
            quality_score=0.0
        ),
        Block(
            block_id="block-3",
            source_id=sample_data_source.source_id,
            block_type="code",
            text_content="import { useState } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n  return <button onClick={() => setCount(count + 1)}>{count}</button>;\n}",
            code_language="javascript",
            position_index=2,
            quality_score=0.0
        ),
    ]
    test_db.add_all(blocks)
    test_db.commit()
    return blocks


class TestAnalyzeAPI:
    """Analyze API 測試"""

    @pytest.mark.asyncio
    async def test_analyze_content_success(self, test_client, test_db, sample_data_source, sample_blocks):
        """正常情境：成功分析內容"""
        # Mock QualityScorer
        mock_scoring_results = [
            {"block_id": "block-1", "score": 75.0, "reasoning": "標題清晰", "is_high_quality": True},
            {"block_id": "block-2", "score": 80.0, "reasoning": "內容完整", "is_high_quality": True},
            {"block_id": "block-3", "score": 90.0, "reasoning": "程式碼完整", "is_high_quality": True},
        ]

        with patch("src.api.analyze.QualityScorer") as MockScorer:
            mock_instance = MockScorer.return_value
            mock_instance.score_blocks_batch = AsyncMock(return_value=mock_scoring_results)

            response = test_client.post(
                "/api/analyze",
                json={"source_id": "test-source-1"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["source_id"] == "test-source-1"
        assert data["data"]["total_blocks"] == 3
        assert data["data"]["high_quality_blocks"] == 3
        assert 75.0 <= data["data"]["average_score"] <= 85.0
        assert data["data"]["threshold"] == 60.0

        # 驗證資料庫已更新
        updated_blocks = test_db.query(Block).filter_by(source_id="test-source-1").all()
        assert updated_blocks[0].quality_score == 75.0
        assert updated_blocks[1].quality_score == 80.0
        assert updated_blocks[2].quality_score == 90.0

    @pytest.mark.asyncio
    async def test_analyze_content_partial_high_quality(self, test_client, test_db, sample_data_source, sample_blocks):
        """正常情境：部分 blocks 為高品質"""
        mock_scoring_results = [
            {"block_id": "block-1", "score": 45.0, "reasoning": "標題過短", "is_high_quality": False},
            {"block_id": "block-2", "score": 85.0, "reasoning": "內容完整", "is_high_quality": True},
            {"block_id": "block-3", "score": 30.0, "reasoning": "程式碼不完整", "is_high_quality": False},
        ]

        with patch("src.api.analyze.QualityScorer") as MockScorer:
            mock_instance = MockScorer.return_value
            mock_instance.score_blocks_batch = AsyncMock(return_value=mock_scoring_results)

            response = test_client.post(
                "/api/analyze",
                json={"source_id": "test-source-1"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_blocks"] == 3
        assert data["data"]["high_quality_blocks"] == 1  # 只有 block-2
        assert len(data["data"]["blocks"]) == 1

    @pytest.mark.asyncio
    async def test_analyze_content_source_not_found(self, test_client):
        """異常情境：DataSource 不存在"""
        response = test_client.post(
            "/api/analyze",
            json={"source_id": "non-existent-source"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "找不到指定的資料來源" in data["error"]
        assert data["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_analyze_content_no_blocks(self, test_client, sample_data_source):
        """異常情境：沒有 blocks"""
        response = test_client.post(
            "/api/analyze",
            json={"source_id": "test-source-1"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "沒有任何內容區塊" in data["error"]
        assert data["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_analyze_content_openai_api_error(self, test_client, sample_data_source, sample_blocks):
        """異常情境：OpenAI API 呼叫失敗"""
        with patch("src.api.analyze.QualityScorer") as MockScorer:
            mock_instance = MockScorer.return_value
            mock_instance.score_blocks_batch = AsyncMock(side_effect=Exception("API Error"))

            response = test_client.post(
                "/api/analyze",
                json={"source_id": "test-source-1"}
            )

        assert response.status_code == 500
        data = response.json()
        assert "AI 評分失敗" in data["error"]
        assert data["code"] == "AI_API_ERROR"

    @pytest.mark.asyncio
    async def test_analyze_content_api_key_missing(self, test_client, sample_data_source, sample_blocks):
        """異常情境：OpenAI API key 未設定"""
        with patch("src.api.analyze.QualityScorer") as MockScorer:
            MockScorer.side_effect = ValueError("OPENAI_API_KEY 未設定")

            response = test_client.post(
                "/api/analyze",
                json={"source_id": "test-source-1"}
            )

        assert response.status_code == 500
        data = response.json()
        assert "AI 評分器初始化失敗" in data["error"]
        assert data["code"] == "AI_API_ERROR"

    @pytest.mark.asyncio
    async def test_analyze_updates_data_source_quality_score(self, test_client, test_db, sample_data_source, sample_blocks):
        """正常情境：更新 DataSource 的整體品質分數"""
        mock_scoring_results = [
            {"block_id": "block-1", "score": 70.0, "reasoning": "好", "is_high_quality": True},
            {"block_id": "block-2", "score": 80.0, "reasoning": "很好", "is_high_quality": True},
            {"block_id": "block-3", "score": 90.0, "reasoning": "優秀", "is_high_quality": True},
        ]

        with patch("src.api.analyze.QualityScorer") as MockScorer:
            mock_instance = MockScorer.return_value
            mock_instance.score_blocks_batch = AsyncMock(return_value=mock_scoring_results)

            response = test_client.post(
                "/api/analyze",
                json={"source_id": "test-source-1"}
            )

        assert response.status_code == 200
        # 驗證 DataSource 的 quality_score 已更新
        updated_source = test_db.query(DataSource).filter_by(source_id="test-source-1").first()
        assert updated_source.quality_score == 80.0  # (70+80+90)/3


class TestAnalysisStatsAPI:
    """Analysis Stats API 測試"""

    def test_get_analysis_stats_success(self, test_client, test_db, sample_data_source, sample_blocks):
        """正常情境：取得分析統計"""
        # 先更新 blocks 的 quality_score
        blocks = test_db.query(Block).filter_by(source_id="test-source-1").all()
        blocks[0].quality_score = 75.0
        blocks[1].quality_score = 85.0
        blocks[2].quality_score = 45.0
        test_db.commit()

        response = test_client.get("/api/analyze/source/test-source-1/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["source_id"] == "test-source-1"
        assert data["data"]["total_blocks"] == 3
        assert data["data"]["high_quality_blocks"] == 2  # 75 和 85
        assert 65.0 <= data["data"]["average_score"] <= 70.0
        assert "block_type_distribution" in data["data"]
        assert "score_distribution" in data["data"]

    def test_get_analysis_stats_source_not_found(self, test_client):
        """異常情境：DataSource 不存在"""
        response = test_client.get("/api/analyze/source/non-existent/stats")

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "NOT_FOUND"

    def test_get_analysis_stats_no_blocks(self, test_client, sample_data_source):
        """邊界情況：沒有 blocks"""
        response = test_client.get("/api/analyze/source/test-source-1/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_blocks"] == 0
        assert data["data"]["high_quality_blocks"] == 0

    def test_get_analysis_stats_block_type_distribution(self, test_client, test_db, sample_data_source, sample_blocks):
        """正常情境：驗證區塊類型分布"""
        blocks = test_db.query(Block).filter_by(source_id="test-source-1").all()
        for block in blocks:
            block.quality_score = 70.0
        test_db.commit()

        response = test_client.get("/api/analyze/source/test-source-1/stats")

        distribution = response.json()["data"]["block_type_distribution"]
        assert distribution["heading"] == 1
        assert distribution["paragraph"] == 1
        assert distribution["code"] == 1

    def test_get_analysis_stats_score_distribution(self, test_client, test_db, sample_data_source, sample_blocks):
        """正常情境：驗證分數分布"""
        blocks = test_db.query(Block).filter_by(source_id="test-source-1").all()
        blocks[0].quality_score = 15.0  # 0-20
        blocks[1].quality_score = 45.0  # 41-60
        blocks[2].quality_score = 95.0  # 81-100
        test_db.commit()

        response = test_client.get("/api/analyze/source/test-source-1/stats")

        distribution = response.json()["data"]["score_distribution"]
        assert distribution["0-20"] == 1
        assert distribution["21-40"] == 0
        assert distribution["41-60"] == 1
        assert distribution["61-80"] == 0
        assert distribution["81-100"] == 1


class TestHelperFunctions:
    """輔助函數測試"""

    def test_get_block_type_distribution(self):
        """正常情境：計算區塊類型分布"""
        from src.api.analyze import _get_block_type_distribution

        blocks = [
            Block(block_id="1", source_id="s1", block_type="heading", text_content="h1", position_index=0, quality_score=0.0),
            Block(block_id="2", source_id="s1", block_type="heading", text_content="h2", position_index=1, quality_score=0.0),
            Block(block_id="3", source_id="s1", block_type="code", text_content="code", position_index=2, quality_score=0.0),
        ]

        distribution = _get_block_type_distribution(blocks)

        assert distribution["heading"] == 2
        assert distribution["code"] == 1

    def test_get_score_distribution(self):
        """正常情境：計算分數分布"""
        from src.api.analyze import _get_score_distribution

        blocks = [
            Block(block_id="1", source_id="s1", block_type="p", text_content="t1", position_index=0, quality_score=10.0),
            Block(block_id="2", source_id="s1", block_type="p", text_content="t2", position_index=1, quality_score=35.0),
            Block(block_id="3", source_id="s1", block_type="p", text_content="t3", position_index=2, quality_score=55.0),
            Block(block_id="4", source_id="s1", block_type="p", text_content="t4", position_index=3, quality_score=75.0),
            Block(block_id="5", source_id="s1", block_type="p", text_content="t5", position_index=4, quality_score=95.0),
        ]

        distribution = _get_score_distribution(blocks)

        assert distribution["0-20"] == 1
        assert distribution["21-40"] == 1
        assert distribution["41-60"] == 1
        assert distribution["61-80"] == 1
        assert distribution["81-100"] == 1

    def test_get_score_distribution_edge_cases(self):
        """邊界情況：分數邊界值"""
        from src.api.analyze import _get_score_distribution

        blocks = [
            Block(block_id="1", source_id="s1", block_type="p", text_content="t1", position_index=0, quality_score=20.0),
            Block(block_id="2", source_id="s1", block_type="p", text_content="t2", position_index=1, quality_score=40.0),
            Block(block_id="3", source_id="s1", block_type="p", text_content="t3", position_index=2, quality_score=60.0),
            Block(block_id="4", source_id="s1", block_type="p", text_content="t4", position_index=3, quality_score=80.0),
        ]

        distribution = _get_score_distribution(blocks)

        # 驗證邊界值分類
        assert distribution["0-20"] == 1  # 20.0
        assert distribution["21-40"] == 1  # 40.0
        assert distribution["41-60"] == 1  # 60.0
        assert distribution["61-80"] == 1  # 80.0
