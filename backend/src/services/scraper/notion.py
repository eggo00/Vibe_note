"""
Notion 爬蟲模組
使用 BeautifulSoup 解析 Notion 公開頁面
對應 tasks.md T028, T029
"""
import httpx
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from ...config import settings


class NotionBlock:
    """Notion Block 資料結構"""

    def __init__(
        self,
        block_id: str,
        block_type: str,
        text_content: str,
        code_language: Optional[str] = None,
        hierarchy_level: int = 0,
        position_index: int = 0
    ):
        self.block_id = block_id
        self.block_type = block_type
        self.text_content = text_content
        self.code_language = code_language
        self.hierarchy_level = hierarchy_level
        self.position_index = position_index

    def to_dict(self) -> Dict:
        return {
            "block_id": self.block_id,
            "block_type": self.block_type,
            "text_content": self.text_content,
            "code_language": self.code_language,
            "hierarchy_level": self.hierarchy_level,
            "position_index": self.position_index
        }


class NotionScraper:
    """
    Notion 公開頁面爬蟲

    使用方式：
        scraper = NotionScraper()
        if await scraper.check_robots_txt("https://notion.so/page"):
            blocks = await scraper.scrape_page("https://notion.so/page")
    """

    def __init__(self):
        self.user_agent = settings.USER_AGENT
        self.timeout = settings.SCRAPER_TIMEOUT

    async def check_robots_txt(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        檢查 robots.txt 是否允許爬取

        Args:
            url: Notion 頁面 URL

        Returns:
            (is_allowed, error_message):
                - is_allowed: True 若允許爬取
                - error_message: 若不允許，返回錯誤訊息
        """
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    robots_url,
                    headers={"User-Agent": self.user_agent},
                    timeout=10.0,
                    follow_redirects=True
                )

                if response.status_code == 404:
                    # 沒有 robots.txt，預設允許
                    return True, None

                robots_content = response.text.lower()

                # 簡化版 robots.txt 解析
                # 檢查是否有針對我們 user-agent 的 Disallow 規則
                user_agent_block = False
                for line in robots_content.splitlines():
                    line = line.strip()

                    if line.startswith("user-agent:"):
                        agent = line.split(":", 1)[1].strip()
                        if agent == "*" or "vibecoding" in agent:
                            user_agent_block = True
                        else:
                            user_agent_block = False

                    if user_agent_block and line.startswith("disallow:"):
                        disallow_path = line.split(":", 1)[1].strip()
                        if disallow_path == "/" or parsed_url.path.startswith(disallow_path):
                            return False, f"robots.txt 禁止爬取此頁面（Disallow: {disallow_path}）"

                return True, None

        except Exception as e:
            # robots.txt 檢查失敗時，預設允許爬取（但記錄錯誤）
            return True, None

    async def scrape_page(self, url: str) -> Tuple[List[NotionBlock], Optional[str]]:
        """
        爬取 Notion 公開頁面

        Args:
            url: Notion 頁面 URL

        Returns:
            (blocks, error_message):
                - blocks: NotionBlock 列表
                - error_message: 若失敗，返回錯誤訊息

        Raises:
            httpx.HTTPError: HTTP 請求失敗
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": self.user_agent,
                        "Accept": "text/html,application/xhtml+xml",
                    },
                    timeout=float(self.timeout),
                    follow_redirects=True
                )

                # 檢查狀態碼
                if response.status_code == 403:
                    return [], "此 Notion 頁面需要登入或權限"
                elif response.status_code == 404:
                    return [], "找不到此 Notion 頁面（404）"
                elif response.status_code != 200:
                    return [], f"HTTP 錯誤：{response.status_code}"

                # 解析 HTML
                soup = BeautifulSoup(response.text, 'lxml')
                blocks = self._parse_notion_blocks(soup)

                if not blocks:
                    return [], "頁面中沒有找到任何內容區塊"

                return blocks, None

        except httpx.TimeoutException:
            return [], f"請求超時（{self.timeout} 秒）"
        except httpx.HTTPError as e:
            return [], f"HTTP 請求失敗：{str(e)}"
        except Exception as e:
            return [], f"爬取失敗：{str(e)}"

    def _parse_notion_blocks(self, soup: BeautifulSoup) -> List[NotionBlock]:
        """
        解析 Notion HTML 結構，提取 blocks

        Notion 公開頁面的典型 HTML 結構：
        - 標題：<h1>, <h2>, <h3>
        - 段落：<p>
        - 程式碼：<pre><code>
        - 列表：<ul><li>, <ol><li>
        - Callout：<div class="callout">
        """
        blocks: List[NotionBlock] = []
        position = 0

        # 尋找主要內容區域
        # Notion 公開頁面通常在 <article> 或 <main> 標籤內
        main_content = soup.find('article') or soup.find('main') or soup

        # 解析標題
        for tag in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = tag.get_text(strip=True)
            if text:
                level = int(tag.name[1])  # h1 -> 1, h2 -> 2, ...
                blocks.append(NotionBlock(
                    block_id=f"heading-{position}",
                    block_type="heading",
                    text_content=text,
                    hierarchy_level=level,
                    position_index=position
                ))
                position += 1

        # 解析段落
        for tag in main_content.find_all('p'):
            text = tag.get_text(strip=True)
            if text and len(text) > 10:  # 過濾太短的段落
                blocks.append(NotionBlock(
                    block_id=f"paragraph-{position}",
                    block_type="paragraph",
                    text_content=text,
                    position_index=position
                ))
                position += 1

        # 解析程式碼區塊
        for tag in main_content.find_all('pre'):
            code_tag = tag.find('code')
            if code_tag:
                code_text = code_tag.get_text()
                if code_text and len(code_text.strip()) > 5:
                    # 嘗試識別語言（從 class 屬性）
                    language = None
                    code_class = code_tag.get('class', [])
                    for cls in code_class:
                        if cls.startswith('language-'):
                            language = cls.replace('language-', '')
                            break

                    blocks.append(NotionBlock(
                        block_id=f"code-{position}",
                        block_type="code",
                        text_content=code_text,
                        code_language=language,
                        position_index=position
                    ))
                    position += 1

        # 解析列表
        for tag in main_content.find_all(['ul', 'ol']):
            list_items = tag.find_all('li', recursive=False)
            list_text = '\n'.join([li.get_text(strip=True) for li in list_items if li.get_text(strip=True)])
            if list_text:
                blocks.append(NotionBlock(
                    block_id=f"list-{position}",
                    block_type="list",
                    text_content=list_text,
                    position_index=position
                ))
                position += 1

        # 解析 Callout（警告、提示框）
        for tag in main_content.find_all('div', class_=lambda x: x and 'callout' in x):
            text = tag.get_text(strip=True)
            if text:
                blocks.append(NotionBlock(
                    block_id=f"callout-{position}",
                    block_type="callout",
                    text_content=text,
                    position_index=position
                ))
                position += 1

        return blocks

    def extract_page_title(self, soup: BeautifulSoup) -> Optional[str]:
        """提取 Notion 頁面標題"""
        # 嘗試多種方式提取標題
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()

        return None
