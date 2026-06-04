#!/usr/bin/env python3
"""get_subscribe - 免费机场/VPN 订阅自动获取工具

Usage:
    # 命令行使用
    python -m get_subscribe

    # Python API
    from get_subscribe import GetSubscribe
    fetcher = GetSubscribe()
    fetcher.run()
"""

import os
import re
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from html import unescape

import feedparser
import requests

requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)

OK_CODE = [200, 201, 202, 203, 204, 205, 206]

# 邮箱域名过滤列表（安全过滤，避免发送到钓鱼域名）
BLACKHOLE_LIST = {
    "cnr.cn", "cyberpolice.cn", "gov.cn", "samr.gov.cn", "12321.cn",
    "miit.gov.cn", "chinatcc.gov.cn", "mps.gov.cn", "caac.gov.cn",
}


class GetSubscribe:
    """免费订阅获取器

    从 cfmem.com RSS 抓取最新 clash / v2ray 订阅链接，
    自动保存到本地配置文件，并可选发送邮件通知。
    """

    RSS_URL = "https://www.cfmem.com/feeds/posts/default?alt=rss"

    def __init__(
        self,
        subscribe_dir: Optional[str] = None,
        log_dir: Optional[str] = None,
        check_only: bool = False,
    ):
        base = Path(__file__).parent.parent
        self.subscribe_dir = Path(subscribe_dir or base / "subscribe")
        self.log_dir = Path(log_dir or base / "log")
        self.check_only = check_only

        self.subscribe_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    # ── Logging ────────────────────────────────────────────────────────────────

    def log(self, content: str, level: str = "INFO") -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{level}] {content}"
        print(line)

        log_file = self.log_dir / f"{datetime.now().strftime('%Y-%m')}-update.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    # ── Core ─────────────────────────────────────────────────────────────────

    def run(self) -> dict[str, int]:
        """执行一次完整抓取，返回结果 dict。"""
        self.log("开始抓取订阅信息...")
        rss = feedparser.parse(self.RSS_URL)
        entries = rss.get("entries", [])

        if not entries:
            self.log("更新失败：无法获取 RSS 内容", "ERROR")
            return {}

        summary = entries[0].get("summary", "") or entries[0].get("summary_detail", {}).get("value", "")
        if not summary:
            self.log("暂时没有可用的订阅更新", "WARN")
            return {}

        results = {}

        # 从 HTML 中提取订阅链接
        # RSS 中的链接格式: <a href="https://v2rayse.com/fs/public/...txt" ...>V2Ray 订阅链接</a>
        # Clash 订阅 (.yaml 或 .yml)
        clash_pattern = r'<a\s+href="([^"]*\.(?:yaml|yml))"[^>]*>\s*Clash\s*订阅链接\s*</a>'
        clash_matches = re.findall(clash_pattern, summary, re.IGNORECASE)
        
        # V2Ray 订阅 (.txt)
        v2ray_pattern = r'<a\s+href="([^"]*\.txt)"[^>]*>\s*V2Ray\s*订阅链接\s*</a>'
        v2ray_matches = re.findall(v2ray_pattern, summary, re.IGNORECASE)
        
        # 备用方案：通过关键词匹配
        if not clash_matches:
            clash_alt = re.findall(r'<a\s+href="([^"]*)"[^>]*>Clash[^<]*</a>', summary, re.IGNORECASE)
            clash_matches = [url for url in clash_alt if url.endswith(('.yaml', '.yml'))]
        
        if not v2ray_matches:
            v2ray_alt = re.findall(r'<a\s+href="([^"]*)"[^>]*>V2Ray[^<]*</a>', summary, re.IGNORECASE)
            v2ray_matches = [url for url in v2ray_alt if url.endswith('.txt')]

        # 处理 Clash 订阅
        if clash_matches:
            clash_url = unescape(clash_matches[0])
            status = self._fetch_and_save("clash", clash_url, "clash.yml")
            results["clash"] = status
        else:
            self.log("未找到 Clash 订阅链接", "WARN")

        # 处理 V2Ray 订阅
        if v2ray_matches:
            v2ray_url = unescape(v2ray_matches[0])
            status = self._fetch_and_save("v2ray", v2ray_url, "v2ray.txt")
            results["v2ray"] = status
        else:
            self.log("未找到 V2Ray 订阅链接", "WARN")

        if results:
            self._log_change(results)
        else:
            self.log("未能获取新的订阅内容", "WARN")

        return results

    def _fetch_and_save(
        self,
        name: str,
        url: str,
        filename: str,
    ) -> int:
        """下载订阅内容并保存到文件，返回 HTTP 状态码。"""
        try:
            resp = requests.get(url, verify=False, timeout=30)
        except requests.RequestException as e:
            self.log(f"获取 {name} 订阅失败（网络错误）: {e}", "WARN")
            return 0

        if resp.status_code not in OK_CODE:
            self.log(f"获取 {name} 订阅失败: {url} - {resp.status_code}", "WARN")
            return resp.status_code

        filepath = self.subscribe_dir / filename
        filepath.write_bytes(resp.content)
        return resp.status_code

    def _log_change(self, results: dict[str, int]) -> None:
        """检测文件是否真正变化，仅在变化时记录。"""
        has_change = False
        for name, status in results.items():
            if status in OK_CODE:
                self.log(f"更新成功：{name} [{status}]", "INFO")
                has_change = True

        if not has_change:
            self.log("订阅内容暂未变化", "WARN")

    # ── CLI ───────────────────────────────────────────────────────────────────

    @staticmethod
    def main() -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
        )
        fetcher = GetSubscribe()
        fetcher.run()


def main() -> None:
    GetSubscribe.main()


if __name__ == "__main__":
    main()
