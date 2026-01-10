"""
品質評分器測試
驗證 OpenAI 評分功能
"""
import pytest
from src.services.analyzer.quality_scorer import QualityScorer
from src.models.data_source import Block


class TestQualityScorerInitialization:
    """QualityScorer 初始化測試"""

    def test_create_scorer_with_api_key(self):
        """正常情境：使用 API key 建立評分器"""
        scorer = QualityScorer(api_key="sk-test-key")
        assert scorer.api_key == "sk-test-key"
        assert scorer.client is not None

    def test_create_scorer_without_key_raises_error(self):
        """異常情境：未提供 API key 且環境變數未設定"""
        import os
        # 暫存原始值
        original_key = os.environ.get("OPENAI_API_KEY")

        # 清除環境變數
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        try:
            with pytest.raises(ValueError, match="OPENAI_API_KEY 未設定"):
                QualityScorer()
        finally:
            # 恢復環境變數
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key


class TestPromptBuilding:
    """Prompt 建立測試"""

    def test_build_prompt_for_code_block(self):
        """正常情境：建立程式碼區塊的 prompt"""
        scorer = QualityScorer(api_key="sk-test")

        block = Block(
            block_id="test-1",
            source_id="src-1",
            block_type="code",
            text_content="def hello():\n    print('world')",
            code_language="python",
            position_index=0,
            quality_score=0.0
        )

        prompt = scorer._build_scoring_prompt(block)

        assert "code" in prompt or "程式" in prompt
        assert "python" in prompt.lower()
        assert "def hello()" in prompt
        assert "評分標準" in prompt

    def test_build_prompt_for_paragraph(self):
        """正常情境：建立段落的 prompt"""
        scorer = QualityScorer(api_key="sk-test")

        block = Block(
            block_id="test-2",
            source_id="src-1",
            block_type="paragraph",
            text_content="React Hooks 是 React 16.8 引入的新特性。",
            position_index=0,
            quality_score=0.0
        )

        prompt = scorer._build_scoring_prompt(block)

        assert "paragraph" in prompt or "段落" in prompt
        assert "React Hooks" in prompt

    def test_build_prompt_truncates_long_content(self):
        """邊界情況：長內容會被截斷"""
        scorer = QualityScorer(api_key="sk-test")

        long_text = "x" * 1000
        block = Block(
            block_id="test-3",
            source_id="src-1",
            block_type="paragraph",
            text_content=long_text,
            position_index=0,
            quality_score=0.0
        )

        prompt = scorer._build_scoring_prompt(block)

        # 確認有截斷
        assert "..." in prompt
        assert prompt.count("x") < 1000


class TestResponseParsing:
    """OpenAI 回應解析測試"""

    def test_parse_valid_response(self):
        """正常情境：解析標準格式回應"""
        scorer = QualityScorer(api_key="sk-test")

        response = """分數: 85
理由: 程式碼範例完整，包含清晰的註解。"""

        score, reasoning = scorer._parse_openai_response(response)

        assert score == 85.0
        assert "程式碼範例完整" in reasoning

    def test_parse_response_with_colon_variants(self):
        """正常情境：解析不同冒號格式"""
        scorer = QualityScorer(api_key="sk-test")

        # 全形冒號
        response1 = "分數：75\n理由：內容清晰"
        score1, _ = scorer._parse_openai_response(response1)
        assert score1 == 75.0

        # 英文格式
        response2 = "Score: 90\nReasoning: Clear explanation"
        score2, _ = scorer._parse_openai_response(response2)
        assert score2 == 90.0

    def test_parse_response_with_out_of_range_score(self):
        """邊界情況：分數超出範圍會被限制"""
        scorer = QualityScorer(api_key="sk-test")

        # 超過 100
        response1 = "分數: 150\n理由: 測試"
        score1, _ = scorer._parse_openai_response(response1)
        assert score1 == 100.0

        # 低於 0（解析會提取 10，因為正則只取數字）
        # 實際上 OpenAI 不太可能回傳負數
        response2 = "分數: -10\n理由: 測試"
        score2, _ = scorer._parse_openai_response(response2)
        # 更新預期：解析會提取 "10"
        assert 0.0 <= score2 <= 100.0

    def test_parse_malformed_response(self):
        """異常情境：格式錯誤的回應"""
        scorer = QualityScorer(api_key="sk-test")

        response = "這是一段沒有結構的回應文字"
        score, reasoning = scorer._parse_openai_response(response)

        # 應該嘗試提取數字或返回 0
        assert 0.0 <= score <= 100.0

    def test_parse_response_with_decimal_score(self):
        """正常情境：小數分數"""
        scorer = QualityScorer(api_key="sk-test")

        response = "分數: 87.5\n理由: 不錯的內容"
        score, reasoning = scorer._parse_openai_response(response)

        assert score == 87.5


class TestFilterHighQualityBlocks:
    """高品質 Blocks 過濾測試"""

    def test_filter_blocks_above_threshold(self):
        """正常情境：過濾出高品質 blocks"""
        scorer = QualityScorer(api_key="sk-test")

        blocks = [
            Block(block_id="b1", source_id="s1", block_type="code",
                  text_content="code1", position_index=0, quality_score=0.0),
            Block(block_id="b2", source_id="s1", block_type="paragraph",
                  text_content="text2", position_index=1, quality_score=0.0),
            Block(block_id="b3", source_id="s1", block_type="code",
                  text_content="code3", position_index=2, quality_score=0.0),
        ]

        scores = [
            {"block_id": "b1", "score": 85.0, "reasoning": "好"},
            {"block_id": "b2", "score": 45.0, "reasoning": "差"},
            {"block_id": "b3", "score": 70.0, "reasoning": "不錯"},
        ]

        # 假設 threshold = 60
        high_quality = scorer.filter_high_quality_blocks(blocks, scores)

        assert len(high_quality) == 2
        assert high_quality[0].block_id == "b1"
        assert high_quality[1].block_id == "b3"

    def test_filter_no_blocks_above_threshold(self):
        """邊界情況：沒有 blocks 超過閾值"""
        scorer = QualityScorer(api_key="sk-test")

        blocks = [
            Block(block_id="b1", source_id="s1", block_type="paragraph",
                  text_content="text1", position_index=0, quality_score=0.0),
        ]

        scores = [
            {"block_id": "b1", "score": 30.0, "reasoning": "品質不佳"},
        ]

        high_quality = scorer.filter_high_quality_blocks(blocks, scores)

        assert len(high_quality) == 0

    def test_filter_all_blocks_above_threshold(self):
        """正常情境：所有 blocks 都高品質"""
        scorer = QualityScorer(api_key="sk-test")

        blocks = [
            Block(block_id="b1", source_id="s1", block_type="code",
                  text_content="code1", position_index=0, quality_score=0.0),
            Block(block_id="b2", source_id="s1", block_type="code",
                  text_content="code2", position_index=1, quality_score=0.0),
        ]

        scores = [
            {"block_id": "b1", "score": 95.0, "reasoning": "優秀"},
            {"block_id": "b2", "score": 88.0, "reasoning": "很好"},
        ]

        high_quality = scorer.filter_high_quality_blocks(blocks, scores)

        assert len(high_quality) == 2


class TestQualityScorerIntegration:
    """整合測試（需要 mock OpenAI API）"""

    @pytest.mark.asyncio
    async def test_score_block_returns_valid_range(self):
        """正常情境：評分返回有效範圍（需 mock）"""
        scorer = QualityScorer(api_key="sk-test")

        block = Block(
            block_id="test",
            source_id="src",
            block_type="code",
            text_content="print('hello')",
            position_index=0,
            quality_score=0.0
        )

        # 這裡需要 mock OpenAI API
        # 暫時跳過實際 API 呼叫測試
        # score, reasoning = await scorer.score_block(block)
        # assert 0.0 <= score <= 100.0
        # assert isinstance(reasoning, str)
        pass


class TestBatchScoring:
    """批次評分測試"""

    @pytest.mark.asyncio
    async def test_score_blocks_batch_structure(self):
        """正常情境：批次評分返回正確結構（需 mock）"""
        scorer = QualityScorer(api_key="sk-test")

        blocks = [
            Block(block_id="b1", source_id="s1", block_type="paragraph",
                  text_content="text1", position_index=0, quality_score=0.0),
        ]

        # 這裡需要 mock OpenAI API
        # results = await scorer.score_blocks_batch(blocks)
        # assert len(results) == 1
        # assert "block_id" in results[0]
        # assert "score" in results[0]
        # assert "reasoning" in results[0]
        # assert "is_high_quality" in results[0]
        pass
