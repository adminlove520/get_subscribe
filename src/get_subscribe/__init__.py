"""
get_subscribe - 免费机场/VPN 订阅自动获取工具
自动从公开 RSS 源抓取 clash/v2ray 订阅链接，间隔 12 小时持续更新。
"""

__version__ = "1.0.14"
__author__ = "adminlove520"

from .fetcher import GetSubscribe

__all__ = ["GetSubscribe", "__version__"]
