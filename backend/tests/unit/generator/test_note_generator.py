"""
Note Generator 測試
驗證筆記生成核心邏輯
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.generator.note_generator import NoteGenerator
from src.models.data_source import Block


@pytest.fixture
def sample_blocks():
    """建立範例 Blocks"""
    return [
        Block(
            block_id="b1",
            source_id="s1",
            block_type="heading",
            text_content="React Hooks 教學",
            hierarchy_level=1,
            position_index=0,
            quality_score=85.0
        ),
        Block(
            block_id="b2",
            source_id="s1",
            block_type="paragraph",
            text_content="useState 是最常用的 Hook，用於在函式組件中管理狀態。",
            position_index=1,
            quality_score=80.0
        ),
        Block(
            block_id="b3",
            source_id="s1",
            block_type="code",
            text_content="const [count, setCount] = useState(0);",
            code_language="javascript",
            position_index=2,
            quality_score=90.0
        ),
        Block(
            block_id="b4",
            source_id="s1",
            block_type="callout",
            text_content="⚠️ 注意：不要在 useEffect 中忘記清理副作用",
            position_index=3,
            quality_score=75.0
        ),
    ]


class TestNoteGenerator:
    """Note Generator 核心功能測試"""

    def test_init_with_api_key(self):
        """正常情境：使用 API key 初始化"""
        generator = NoteGenerator(api_key="test-key")
        assert generator.api_key == "test-key"
        assert generator.model == "gpt-3.5-turbo"
        assert generator.temperature == 0.7

    def test_init_without_api_key_raises_error(self):
        """異常情境：未提供 API key"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY 未設定"):
                NoteGenerator()

    def test_init_with_custom_params(self):
        """正常情境：自訂參數初始化"""
        generator = NoteGenerator(
            api_key="test-key",
            model="gpt-4",
            temperature=0.5,
            max_tokens=2000
        )
        assert generator.model == "gpt-4"
        assert generator.temperature == 0.5
        assert generator.max_tokens == 2000

    @pytest.mark.asyncio
    async def test_generate_note_success(self, sample_blocks):
        """正常情境：成功生成筆記"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="# React Hooks 學習筆記\n\n## 專案摘要\n..."))
        ]

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()

            with patch.object(generator.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)):
                result = await generator.generate_note(sample_blocks)

        assert isinstance(result, str)
        assert "React Hooks" in result or len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_note_with_project_context(self, sample_blocks):
        """正常情境：包含專案背景生成筆記"""
        context = "這是一個 React 學習專案，目標是理解 Hooks 的運作原理。"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="# 筆記內容"))
        ]

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()

            with patch.object(generator.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)) as mock_create:
                result = await generator.generate_note(sample_blocks, project_context=context)

                # 驗證 API 被呼叫
                assert mock_create.called
                call_args = mock_create.call_args
                messages = call_args.kwargs["messages"]

                # 檢查 context 有被包含在提示詞中
                user_message = messages[1]["content"]
                assert context in user_message

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_note_with_style_template(self, sample_blocks):
        """正常情境：套用風格模板生成筆記"""
        style_template = {
            "heading_pattern": "使用問句（如：「什麼是 React Hooks？」）",
            "paragraph_order": ["概念說明", "範例程式碼", "常見錯誤"],
            "tone": "輕鬆活潑"
        }

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="# 什麼是 React Hooks？\n\n..."))
        ]

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()

            with patch.object(generator.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)) as mock_create:
                result = await generator.generate_note(sample_blocks, style_template=style_template)

                # 驗證風格模板被應用到系統提示詞
                call_args = mock_create.call_args
                system_message = call_args.kwargs["messages"][0]["content"]

                assert "使用問句" in system_message or "風格要求" in system_message

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_note_empty_blocks_raises_error(self):
        """異常情境：空 blocks 列表"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()

            with pytest.raises(ValueError, match="至少需要一個 block"):
                await generator.generate_note([])

    @pytest.mark.asyncio
    async def test_generate_summary_success(self, sample_blocks):
        """正常情境：生成摘要"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="本文介紹 React Hooks 的基礎用法，包括 useState 和 useEffect。"))
        ]

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()

            with patch.object(generator.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)):
                summary = await generator.generate_summary(sample_blocks, max_length=300)

        assert isinstance(summary, str)
        assert len(summary) <= 300

    @pytest.mark.asyncio
    async def test_generate_summary_empty_blocks(self):
        """邊界情況：空 blocks 返回預設訊息"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            summary = await generator.generate_summary([])

        assert summary == "（無內容）"

    def test_get_default_style_template(self):
        """正常情境：取得預設風格模板"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            template = generator.get_default_style_template()

        assert isinstance(template, dict)
        assert "heading_pattern" in template
        assert "paragraph_order" in template
        assert "tone" in template
        assert template["paragraph_order"] == [
            "專案摘要",
            "核心功能說明",
            "關鍵程式碼與解說",
            "常見錯誤與解法"
        ]
        assert template["use_emojis"] is False
        assert template["max_heading_level"] == 3

    def test_build_generation_prompt_structure(self, sample_blocks):
        """正常情境：驗證提示詞結構"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            prompt = generator._build_generation_prompt(sample_blocks)

        assert "學習資料來源" in prompt
        assert "React Hooks" in prompt
        assert "useState" in prompt
        assert "javascript" in prompt or "程式碼" in prompt
        assert "請基於以上資料" in prompt

    def test_build_generation_prompt_with_context(self, sample_blocks):
        """正常情境：包含專案背景的提示詞"""
        context = "這是一個學習專案"

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            prompt = generator._build_generation_prompt(sample_blocks, project_context=context)

        assert "專案背景" in prompt
        assert context in prompt

    def test_build_generation_prompt_filters_by_block_type(self, sample_blocks):
        """正常情境：驗證按 block 類型分組"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            prompt = generator._build_generation_prompt(sample_blocks)

        # 驗證包含各類型 blocks
        assert "重要標題" in prompt
        assert "說明段落" in prompt
        assert "程式碼範例" in prompt
        assert "重要提示/警告" in prompt

    def test_get_system_prompt_default(self):
        """正常情境：預設系統提示詞"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            prompt = generator._get_system_prompt()

        assert "技術筆記撰寫助手" in prompt
        assert "專案摘要" in prompt
        assert "核心功能說明" in prompt
        assert "關鍵程式碼與解說" in prompt
        assert "常見錯誤與解法" in prompt

    def test_get_system_prompt_with_style(self):
        """正常情境：包含風格模板的系統提示詞"""
        style = {
            "heading_pattern": "問句式",
            "tone": "活潑輕鬆",
            "paragraph_order": ["摘要", "範例", "錯誤"]
        }

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            prompt = generator._get_system_prompt(style_template=style)

        assert "風格要求" in prompt
        assert "問句式" in prompt
        assert "活潑輕鬆" in prompt


class TestNoteGeneratorEdgeCases:
    """邊界情況與錯誤處理測試"""

    @pytest.mark.asyncio
    async def test_generate_note_handles_long_content(self):
        """邊界情況：處理超長內容"""
        long_blocks = [
            Block(
                block_id=f"b{i}",
                source_id="s1",
                block_type="paragraph",
                text_content="很長的文字" * 100,  # 超長內容
                position_index=i,
                quality_score=70.0
            )
            for i in range(20)  # 20 個超長 blocks
        ]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="# 摘要筆記"))]

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()

            with patch.object(generator.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)):
                result = await generator.generate_note(long_blocks)

        # 驗證能夠處理並生成結果
        assert isinstance(result, str)

    def test_build_generation_prompt_limits_blocks(self):
        """邊界情況：驗證 blocks 數量限制"""
        many_headings = [
            Block(
                block_id=f"h{i}",
                source_id="s1",
                block_type="heading",
                text_content=f"標題 {i}",
                hierarchy_level=2,
                position_index=i,
                quality_score=70.0
            )
            for i in range(30)  # 30 個標題
        ]

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()
            prompt = generator._build_generation_prompt(many_headings)

        # 驗證提示詞長度合理（應該有限制）
        # 系統應該只取前 10 個標題
        heading_count = prompt.count("標題")
        assert heading_count <= 15  # 有限制，不會全部包含

    @pytest.mark.asyncio
    async def test_generate_note_openai_api_error(self, sample_blocks):
        """異常情境：OpenAI API 呼叫失敗"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            generator = NoteGenerator()

            with patch.object(
                generator.client.chat.completions,
                "create",
                new=AsyncMock(side_effect=Exception("API Error"))
            ):
                with pytest.raises(Exception, match="API Error"):
                    await generator.generate_note(sample_blocks)
