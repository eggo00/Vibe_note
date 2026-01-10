"""
Mock Note Generator
用於開發測試，不需要 OpenAI API Key
"""
from typing import List, Optional, Dict, Any
from ...models.data_source import Block


class MockNoteGenerator:
    """
    模擬筆記生成器

    產生結構化的測試筆記內容
    """

    def __init__(self, **kwargs):
        """初始化（相容原本的參數）"""
        pass

    async def generate_note(
        self,
        blocks: List[Block],
        project_context: Optional[str] = None,
        style_template: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成模擬筆記

        Returns:
            Markdown 格式的筆記內容
        """
        if not blocks:
            raise ValueError("至少需要一個 block 才能生成筆記")

        # 提取內容摘要
        headings = [b.text_content for b in blocks if b.block_type == 'heading']
        code_blocks = [b for b in blocks if b.block_type == 'code']
        paragraphs = [b.text_content for b in blocks if b.block_type == 'paragraph']

        title = headings[0] if headings else "技術學習筆記"

        # 生成 Markdown 內容
        markdown = f"""# {title}

## 專案摘要

本筆記基於高品質學習內容自動生成（Mock 模式）。

"""

        if project_context:
            markdown += f"**專案背景**: {project_context}\n\n"

        markdown += f"**內容來源**: 共 {len(blocks)} 個高品質區塊\n\n"

        # 核心功能說明
        markdown += """## 核心功能說明

"""
        if paragraphs:
            for i, para in enumerate(paragraphs[:3], 1):
                markdown += f"{i}. {para[:100]}{'...' if len(para) > 100 else ''}\n"
        else:
            markdown += "本節包含核心概念與功能說明。\n"

        # 關鍵程式碼與解說
        markdown += """

## 關鍵程式碼與解說

"""
        if code_blocks:
            for i, block in enumerate(code_blocks[:2], 1):
                lang = block.code_language or 'plaintext'
                code = block.text_content[:200] + '...' if len(block.text_content) > 200 else block.text_content
                markdown += f"""
### 範例 {i}

```{lang}
{code}
```

這段程式碼展示了核心功能的實作方式。

"""
        else:
            markdown += "```python\n# 程式碼範例將在此展示\nprint('Hello, World!')\n```\n\n"

        # 常見錯誤與解法
        markdown += """## 常見錯誤與解法

### 錯誤 1: 環境設定問題
**症狀**: 套件安裝失敗或版本衝突
**解法**: 使用虛擬環境並確認依賴版本

### 錯誤 2: API 呼叫失敗
**症狀**: 連線逾時或回應錯誤
**解法**: 檢查 API Key 設定和網路連線

---

**註**: 此筆記由 Vibe Note AI 自動生成（Mock 模式）
"""

        return markdown

    async def generate_summary(self, blocks: List[Block], max_length: int = 300) -> str:
        """生成摘要"""
        if not blocks:
            return "（無內容）"

        headings = [b.text_content for b in blocks if b.block_type == 'heading']
        if headings:
            summary = f"{headings[0]} - 學習筆記"
        else:
            summary = f"基於 {len(blocks)} 個區塊的技術學習筆記"

        return summary[:max_length]

    def get_default_style_template(self) -> Dict[str, Any]:
        """取得預設風格模板"""
        return {
            "heading_pattern": "清晰直白",
            "paragraph_order": [
                "專案摘要",
                "核心功能說明",
                "關鍵程式碼與解說",
                "常見錯誤與解法"
            ],
            "tone": "專業友善",
            "use_emojis": False,
            "max_heading_level": 3
        }
