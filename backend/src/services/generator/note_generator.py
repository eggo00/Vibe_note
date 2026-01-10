"""
筆記生成器
基於高品質 blocks 使用 OpenAI API 生成結構化 Markdown 筆記
對應 tasks.md T033
"""
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
import os
from ...models.data_source import Block


class NoteGenerator:
    """
    筆記生成器

    根據 FR-014~FR-017 需求：
    - 基於高品質 blocks 產出結構化 Markdown 筆記
    - 包含：專案摘要、核心功能說明、關鍵程式碼與解說、常見錯誤與解法
    - 套用風格模板（style_profile）
    - 程式碼區塊包含語言標註與解說
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,  # 較高溫度以產生更有創意的內容
        max_tokens: int = 3000
    ):
        """
        初始化筆記生成器

        Args:
            api_key: OpenAI API Key（若為 None 則從環境變數讀取）
            model: OpenAI 模型名稱
            temperature: 生成溫度（0.0-1.0，越高越有創意）
            max_tokens: 最大生成 tokens 數
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 未設定，請設定環境變數或傳入 api_key 參數")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate_note(
        self,
        blocks: List[Block],
        project_context: Optional[str] = None,
        style_template: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成結構化 Markdown 筆記

        Args:
            blocks: 高品質 blocks 列表（quality_score >= 60）
            project_context: 專案背景資訊（對話紀錄、README 等）
            style_template: 風格模板（包含段落順序、標題格式等）

        Returns:
            Markdown 格式的筆記內容
        """
        if not blocks:
            raise ValueError("至少需要一個 block 才能生成筆記")

        # 建構提示詞
        prompt = self._build_generation_prompt(blocks, project_context, style_template)

        # 呼叫 OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self._get_system_prompt(style_template)
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        markdown_content = response.choices[0].message.content.strip()
        return markdown_content

    def _get_system_prompt(self, style_template: Optional[Dict[str, Any]] = None) -> str:
        """
        建構系統提示詞

        根據風格模板調整生成風格
        """
        base_prompt = """你是一個專業的技術筆記撰寫助手。
你的任務是將學習資料整理成結構化、易懂的 Markdown 技術筆記。

**重要規則**：
1. 不得直接複製原文句子，只能學習結構與概念
2. 必須包含以下段落：
   - 專案摘要（Project Overview）
   - 核心功能說明（Core Features）
   - 關鍵程式碼與解說（Key Code Examples）
   - 常見錯誤與解法（Common Pitfalls）
3. 每個程式碼區塊必須標註語言（如 ```python）並附上簡短解說
4. 使用清晰的標題階層（# ## ###）
5. 內容應教學友善、初學者也能理解"""

        if style_template:
            # 若有風格模板，追加風格指引
            heading_style = style_template.get("heading_pattern", "清晰直白")
            paragraph_order = style_template.get("paragraph_order", [])
            tone = style_template.get("tone", "專業友善")

            style_guidance = f"""

**風格要求**：
- 標題風格：{heading_style}
- 段落順序：{' → '.join(paragraph_order) if paragraph_order else '標準結構'}
- 語氣：{tone}"""

            base_prompt += style_guidance

        return base_prompt

    def _build_generation_prompt(
        self,
        blocks: List[Block],
        project_context: Optional[str] = None,
        style_template: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        建構使用者提示詞

        將 blocks 內容整理成結構化輸入
        """
        prompt_parts = []

        # 1. 專案背景（若有）
        if project_context:
            prompt_parts.append(f"## 專案背景\n\n{project_context}\n")

        # 2. 整理 blocks 內容
        prompt_parts.append("## 學習資料來源\n")
        prompt_parts.append("以下是從多個來源篩選的高品質學習內容：\n")

        # 按類型分組
        headings = [b for b in blocks if b.block_type == "heading"]
        paragraphs = [b for b in blocks if b.block_type == "paragraph"]
        code_blocks = [b for b in blocks if b.block_type == "code"]
        callouts = [b for b in blocks if b.block_type == "callout"]

        if headings:
            prompt_parts.append("\n### 重要標題\n")
            for h in headings[:10]:  # 最多 10 個
                level = h.hierarchy_level or 1
                prompt_parts.append(f"{'#' * level} {h.text_content}\n")

        if paragraphs:
            prompt_parts.append("\n### 說明段落\n")
            for p in paragraphs[:15]:  # 最多 15 個
                prompt_parts.append(f"- {p.text_content[:200]}...\n" if len(p.text_content) > 200 else f"- {p.text_content}\n")

        if code_blocks:
            prompt_parts.append("\n### 程式碼範例\n")
            for idx, c in enumerate(code_blocks[:8], 1):  # 最多 8 個
                lang = c.code_language or "plaintext"
                code = c.text_content[:300] + "..." if len(c.text_content) > 300 else c.text_content
                prompt_parts.append(f"\n範例 {idx} ({lang}):\n```{lang}\n{code}\n```\n")

        if callouts:
            prompt_parts.append("\n### 重要提示/警告\n")
            for callout in callouts[:5]:  # 最多 5 個
                prompt_parts.append(f"- {callout.text_content}\n")

        # 3. 生成指令
        prompt_parts.append("\n---\n\n")
        prompt_parts.append("請基於以上資料，生成一份完整的技術筆記（Markdown 格式）。\n")
        prompt_parts.append("要求：\n")
        prompt_parts.append("1. 包含專案摘要、核心功能說明、關鍵程式碼與解說、常見錯誤與解法四個段落\n")
        prompt_parts.append("2. 不要直接複製原文，用自己的話重新組織與解說\n")
        prompt_parts.append("3. 程式碼區塊要加上語言標註和解說\n")
        prompt_parts.append("4. 標題要清晰、段落要有邏輯層次\n")

        if style_template and style_template.get("paragraph_order"):
            order = style_template["paragraph_order"]
            prompt_parts.append(f"5. 段落順序建議：{' → '.join(order)}\n")

        return "".join(prompt_parts)

    async def generate_summary(self, blocks: List[Block], max_length: int = 300) -> str:
        """
        生成簡短摘要

        Args:
            blocks: Block 列表
            max_length: 最大字元數

        Returns:
            簡短摘要文字
        """
        if not blocks:
            return "（無內容）"

        # 提取關鍵資訊
        headings_text = " | ".join([b.text_content for b in blocks if b.block_type == "heading"][:5])

        prompt = f"""請用 1-2 句話總結以下技術內容的核心主題：

標題：{headings_text if headings_text else '（無標題）'}

內容片段：
{blocks[0].text_content[:200] if blocks else ''}

要求：簡潔明瞭，最多 {max_length} 字元。"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一個專業的技術文件總結助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )

        summary = response.choices[0].message.content.strip()
        return summary[:max_length]  # 確保不超過長度限制

    def get_default_style_template(self) -> Dict[str, Any]:
        """
        取得預設風格模板（教學友善風格）

        對應 FR-013：若無老師 Blog 資料，使用預設模板

        Returns:
            預設風格模板字典
        """
        return {
            "heading_pattern": "清晰直白（如：「React Hooks 完整教學」而非「淺談 Hooks」）",
            "paragraph_order": [
                "專案摘要",
                "核心功能說明",
                "關鍵程式碼與解說",
                "常見錯誤與解法"
            ],
            "tone": "專業友善，適合初學者",
            "code_explanation_style": "每個程式碼區塊後加上「這段程式碼...」開頭的解說",
            "use_emojis": False,  # 預設不使用 emoji
            "max_heading_level": 3  # 最多使用到 h3
        }
