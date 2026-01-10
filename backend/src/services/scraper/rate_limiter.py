"""
RateLimiter: 爬蟲請求限速器
確保遵守 rate limiting 規範（預設每秒最多 1 次請求）
對應 tasks.md T018, constitution.md §資料處理
"""
import time
import asyncio
from typing import Optional
from datetime import datetime, timedelta


class RateLimiter:
    """
    Token Bucket 演算法實作的 Rate Limiter

    使用方式：
        limiter = RateLimiter(requests_per_second=1)

        # 同步版本
        limiter.wait()
        # ... 執行請求 ...

        # 非同步版本
        await limiter.wait_async()
        # ... 執行請求 ...
    """

    def __init__(self, requests_per_second: float = 1.0):
        """
        初始化 Rate Limiter

        Args:
            requests_per_second: 每秒允許的請求數（預設 1.0）
        """
        if requests_per_second <= 0:
            raise ValueError("requests_per_second 必須大於 0")

        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second  # 兩次請求之間的最小間隔（秒）
        self.last_request_time: Optional[float] = None

    def wait(self) -> None:
        """
        同步版本：等待至可以發送下一個請求
        若距離上次請求時間不足 min_interval，則 sleep 至滿足條件
        """
        current_time = time.time()

        if self.last_request_time is not None:
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_interval:
                sleep_duration = self.min_interval - elapsed
                time.sleep(sleep_duration)

        self.last_request_time = time.time()

    async def wait_async(self) -> None:
        """
        非同步版本：等待至可以發送下一個請求
        使用 asyncio.sleep 避免阻塞事件循環
        """
        current_time = time.time()

        if self.last_request_time is not None:
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_interval:
                sleep_duration = self.min_interval - elapsed
                await asyncio.sleep(sleep_duration)

        self.last_request_time = time.time()

    def reset(self) -> None:
        """重置 limiter 狀態（測試用）"""
        self.last_request_time = None

    def get_time_until_next_request(self) -> float:
        """
        取得距離下次可請求的剩餘時間（秒）

        Returns:
            剩餘等待時間（秒），若可立即請求則返回 0.0
        """
        if self.last_request_time is None:
            return 0.0

        elapsed = time.time() - self.last_request_time
        remaining = self.min_interval - elapsed
        return max(0.0, remaining)

    def can_request_now(self) -> bool:
        """
        檢查當前是否可以發送請求

        Returns:
            True 若可立即請求，False 若需等待
        """
        return self.get_time_until_next_request() == 0.0

    def __repr__(self) -> str:
        return f"<RateLimiter(rps={self.requests_per_second}, interval={self.min_interval:.3f}s)>"
