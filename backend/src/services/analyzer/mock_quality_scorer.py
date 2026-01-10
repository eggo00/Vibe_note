"""
Mock Quality Scorer
用於開發測試，不需要 OpenAI API Key
"""
from typing import List, Tuple, Dict, Any
from ...models.data_source import Block
import random


class MockQualityScorer:
    """
    模擬品質評分器

    根據內容長度和類型給予隨機分數，用於測試
    """

    def __init__(self, threshold: float = 60.0):
        self.threshold = threshold

    async def score_block(self, block: Block) -> Tuple[float, str]:
        """
        模擬單一 block 評分

        Returns:
            (分數, 理由)
        """
        # 根據 block 類型給予不同分數範圍
        score_ranges = {
            'heading': (70, 90),      # 標題通常品質較高
            'code': (75, 95),         # 程式碼通常品質高
            'paragraph': (50, 80),    # 段落分數變化較大
            'list': (60, 85),         # 列表中等偏高
            'callout': (65, 90),      # 提示框通常有重要資訊
        }

        min_score, max_score = score_ranges.get(block.block_type, (40, 70))

        # 內容越長，分數略高
        content_length = len(block.text_content or '')
        if content_length > 200:
            min_score += 5
            max_score += 5
        elif content_length < 50:
            min_score -= 10
            max_score -= 10

        score = random.uniform(min_score, max_score)
        score = max(0.0, min(100.0, score))  # 限制在 0-100

        # 生成理由
        if score >= 80:
            reasoning = f"內容完整、結構清晰（{block.block_type}）"
        elif score >= 60:
            reasoning = f"內容尚可，有學習價值（{block.block_type}）"
        else:
            reasoning = f"內容較簡略（{block.block_type}）"

        return score, reasoning

    async def score_blocks_batch(self, blocks: List[Block]) -> List[Dict[str, Any]]:
        """
        批次評分

        Returns:
            評分結果列表
        """
        results = []

        for block in blocks:
            score, reasoning = await self.score_block(block)
            results.append({
                'block_id': block.block_id,
                'score': score,
                'reasoning': reasoning,
                'is_high_quality': score >= self.threshold
            })

        return results

    def filter_high_quality_blocks(
        self,
        scoring_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """過濾高品質 blocks"""
        return [
            result for result in scoring_results
            if result['is_high_quality']
        ]
