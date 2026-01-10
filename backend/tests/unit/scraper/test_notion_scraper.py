"""
Notion 爬蟲測試
驗證 Notion 公開頁面爬取功能
"""
import pytest
from bs4 import BeautifulSoup
from src.services.scraper.notion import NotionScraper, NotionBlock


class TestNotionBlock:
    """NotionBlock 資料結構測試"""

    def test_create_block(self):
        """正常情境：建立 NotionBlock"""
        block = NotionBlock(
            block_id="test-1",
            block_type="paragraph",
            text_content="測試內容",
            position_index=0
        )

        assert block.block_id == "test-1"
        assert block.block_type == "paragraph"
        assert block.text_content == "測試內容"
        assert block.position_index == 0

    def test_block_to_dict(self):
        """正常情境：轉換為 dict"""
        block = NotionBlock(
            block_id="code-1",
            block_type="code",
            text_content="print('hello')",
            code_language="python",
            hierarchy_level=0,
            position_index=1
        )

        result = block.to_dict()

        assert result["block_id"] == "code-1"
        assert result["block_type"] == "code"
        assert result["code_language"] == "python"


class TestNotionScraperParsing:
    """Notion HTML 解析測試"""

    def test_parse_heading(self):
        """正常情境：解析標題"""
        html = """
        <article>
            <h1>主標題</h1>
            <h2>次標題</h2>
        </article>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        blocks = scraper._parse_notion_blocks(soup)

        headings = [b for b in blocks if b.block_type == "heading"]
        assert len(headings) >= 2
        assert any(b.text_content == "主標題" for b in headings)
        assert any(b.hierarchy_level == 2 for b in headings)

    def test_parse_paragraph(self):
        """正常情境：解析段落"""
        html = """
        <article>
            <p>這是一個測試段落，內容要夠長才會被保留。</p>
            <p>短文</p>
        </article>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        blocks = scraper._parse_notion_blocks(soup)

        paragraphs = [b for b in blocks if b.block_type == "paragraph"]
        # 只有長段落會被保留
        assert any("測試段落" in b.text_content for b in paragraphs)

    def test_parse_code_block(self):
        """正常情境：解析程式碼區塊"""
        html = """
        <article>
            <pre><code class="language-python">def hello():
    print("world")</code></pre>
        </article>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        blocks = scraper._parse_notion_blocks(soup)

        code_blocks = [b for b in blocks if b.block_type == "code"]
        assert len(code_blocks) >= 1
        assert code_blocks[0].code_language == "python"
        assert "def hello()" in code_blocks[0].text_content

    def test_parse_list(self):
        """正常情境：解析列表"""
        html = """
        <article>
            <ul>
                <li>項目 1</li>
                <li>項目 2</li>
                <li>項目 3</li>
            </ul>
        </article>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        blocks = scraper._parse_notion_blocks(soup)

        list_blocks = [b for b in blocks if b.block_type == "list"]
        assert len(list_blocks) >= 1
        assert "項目 1" in list_blocks[0].text_content
        assert "項目 2" in list_blocks[0].text_content

    def test_parse_callout(self):
        """正常情境：解析 Callout"""
        html = """
        <article>
            <div class="callout-warning">
                ⚠️ 注意事項：這是重要提示
            </div>
        </article>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        blocks = scraper._parse_notion_blocks(soup)

        callouts = [b for b in blocks if b.block_type == "callout"]
        assert len(callouts) >= 1
        assert "注意事項" in callouts[0].text_content

    def test_parse_empty_html(self):
        """邊界情況：空 HTML"""
        html = "<article></article>"
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        blocks = scraper._parse_notion_blocks(soup)

        assert blocks == []

    def test_parse_mixed_content(self):
        """正常情境：混合內容"""
        html = """
        <article>
            <h1>React Hooks 教學</h1>
            <p>React Hooks 是 React 16.8 引入的新特性。</p>
            <pre><code class="language-javascript">
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
            </code></pre>
            <ul>
                <li>useState 管理狀態</li>
                <li>useEffect 處理副作用</li>
            </ul>
        </article>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        blocks = scraper._parse_notion_blocks(soup)

        # 驗證各種類型都有
        assert any(b.block_type == "heading" for b in blocks)
        assert any(b.block_type == "paragraph" for b in blocks)
        assert any(b.block_type == "code" for b in blocks)
        assert any(b.block_type == "list" for b in blocks)

        # 驗證位置索引遞增
        positions = [b.position_index for b in blocks]
        assert positions == sorted(positions)


class TestNotionScraperRobotsTxt:
    """robots.txt 檢查測試"""

    @pytest.mark.asyncio
    async def test_robots_txt_allow_all(self):
        """正常情境：robots.txt 允許所有（實際測試需 mock）"""
        scraper = NotionScraper()

        # 這裡僅測試函數簽名，實際測試需要 mock httpx
        is_allowed, error = await scraper.check_robots_txt("https://notion.so/test")

        assert isinstance(is_allowed, bool)
        assert error is None or isinstance(error, str)


class TestNotionScraperIntegration:
    """整合測試（需要實際網路或 mock）"""

    def test_extract_page_title(self):
        """正常情境：提取頁面標題"""
        html = """
        <html>
            <head><title>React Hooks 教學 | Notion</title></head>
            <body>
                <article>
                    <h1>React Hooks 教學</h1>
                </article>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        title = scraper.extract_page_title(soup)

        assert title is not None
        assert "React Hooks" in title

    def test_extract_title_from_h1(self):
        """正常情境：從 h1 提取標題"""
        html = """
        <html>
            <body>
                <article>
                    <h1>專案標題</h1>
                </article>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        title = scraper.extract_page_title(soup)

        assert title == "專案標題"

    def test_extract_title_no_title(self):
        """邊界情況：沒有標題"""
        html = "<html><body><p>只有段落</p></body></html>"
        soup = BeautifulSoup(html, 'lxml')
        scraper = NotionScraper()

        title = scraper.extract_page_title(soup)

        assert title is None


class TestNotionScraperErrorHandling:
    """錯誤處理測試"""

    @pytest.mark.asyncio
    async def test_scrape_invalid_url(self):
        """異常情境：無效 URL（需要實際網路測試）"""
        scraper = NotionScraper()

        # 測試不會拋出異常，而是返回錯誤訊息
        blocks, error = await scraper.scrape_page("https://notion.so/this-page-does-not-exist-12345")

        assert blocks == []
        assert error is not None
        # 可能是 404 或 timeout


class TestNotionScraperConfig:
    """配置測試"""

    def test_scraper_uses_config(self):
        """正常情境：Scraper 使用環境配置"""
        scraper = NotionScraper()

        assert scraper.user_agent is not None
        assert scraper.timeout > 0
        assert "VibeCoding" in scraper.user_agent or "Bot" in scraper.user_agent
