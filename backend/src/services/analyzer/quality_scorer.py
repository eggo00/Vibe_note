"""
Block 品質評分器
使用 OpenAI API 評估內容區塊的學習價值
對應 tasks.md T031
"""
from typing import List, Dict, Tuple
from openai import AsyncOpenAI
from ...config import settings
from ...models.data_source import Block


class QualityScorer:
    """
    內容品質評分器

    評分維度（總分 100）：
    1. 結構清晰度（0-25 分）
    2. 技術密度（0-25 分）
    3. 可操作性（0-25 分）
    4. 程式碼完整度（0-25 分）

    閾值：score >= 60 視為「可學習內容」
    """

    def __init__(self, api_key: str | None = None):
        """
        初始化評分器

        Args:
            api_key: OpenAI API Key（若未提供，從環境變數讀取）
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 未設定")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.OPENAI_MODEL

    async def score_block(self, block: Block) -> Tuple[float, str]:
        """
        評估單個 Block 的品質

        Args:
            block: Block 物件

        Returns:
            (score, reasoning):
                - score: 品質分數（0-100）
                - reasoning: 評分理由
        """
        # 建立評分 prompt
        prompt = self._build_scoring_prompt(block)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個教學內容品質評估專家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 降低隨機性，確保評分一致
                max_tokens=300
            )

            result = response.choices[0].message.content
            if not result:
                return 0.0, "API 回應為空"

            # 解析回應（預期格式："分數: 75\n理由: ..."）
            score, reasoning = self._parse_openai_response(result)
            return score, reasoning

        except Exception as e:
            # 評分失敗時返回預設分數
            return 0.0, f"評分失敗：{str(e)}"

    async def score_blocks_batch(self, blocks: List[Block]) -> List[Dict]:
        """
        批次評估多個 Blocks

        Args:
            blocks: Block 列表

        Returns:
            結果列表，格式：[{"block_id": str, "score": float, "reasoning": str}, ...]
        """
        results = []

        for block in blocks:
            score, reasoning = await self.score_block(block)
            results.append({
                "block_id": block.block_id,
                "score": score,
                "reasoning": reasoning,
                "is_high_quality": score >= settings.QUALITY_SCORE_THRESHOLD
            })

        return results

    def _build_scoring_prompt(self, block: Block) -> str:
        """建立評分 prompt"""
        content_preview = block.text_content[:500] + "..." if len(block.text_content) > 500 else block.text_content

        prompt = f"""請評估以下內容區塊的學習價值（總分 100 分）：

**區塊類型**: {block.block_type}
{f"**程式語言**: {block.code_language}" if block.code_language else ""}
**內容**:
```
{content_preview}
```

**評分標準**（總分 100）：
1. 結構清晰度（0-25）：內容組織是否清晰易懂
2. 技術密度（0-25）：包含的技術知識深度
3. 可操作性（0-25）：是否提供可實作的步驟或範例
4. 程式碼完整度（0-25）：程式碼是否完整可執行（僅程式碼區塊）

**回應格式**（請嚴格遵守）：
分數: [0-100的整數]
理由: [簡短說明（50字內）]

範例：
分數: 75
理由: 程式碼範例完整，包含清晰的註解與說明，具有高度學習價值。
"""
        return prompt

    def _parse_openai_response(self, response: str) -> Tuple[float, str]:
        """
        解析 OpenAI 回應

        Args:
            response: OpenAI 回應文字

        Returns:
            (score, reasoning)
        """
        try:
            lines = response.strip().split("\n")
            score = 0.0
            reasoning = "無法解析評分理由"

            for line in lines:
                line = line.strip()
                if line.startswith("分數:") or line.startswith("分数:") or line.startswith("Score:"):
                    # 提取分數
                    score_str = line.split(":", 1)[1].strip()
                    # 移除非數字字元
                    score_str = ''.join(c for c in score_str if c.isdigit() or c == '.')
                    score = float(score_str)
                    score = max(0.0, min(100.0, score))  # 限制在 0-100

                elif line.startswith("理由:") or line.startswith("理由：") or line.startswith("Reasoning:"):
                    reasoning = line.split(":", 1)[1].strip()

            return score, reasoning

        except Exception as e:
            # 解析失敗，嘗試直接提取數字
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                score = float(numbers[0])
                score = max(0.0, min(100.0, score))
                return score, response[:100]
            else:
                return 0.0, f"解析失敗：{str(e)}"

    def filter_high_quality_blocks(self, blocks: List[Block], scores: List[Dict]) -> List[Block]:
        """
        過濾出高品質 Blocks（score >= threshold）

        Args:
            blocks: 原始 Block 列表
            scores: 評分結果列表

        Returns:
            高品質 Block 列表
        """
        # 建立 block_id -> score 對應
        score_map = {item["block_id"]: item["score"] for item in scores}

        high_quality_blocks = [
            block for block in blocks
            if score_map.get(block.block_id, 0) >= settings.QUALITY_SCORE_THRESHOLD
        ]

        return high_quality_blocks
