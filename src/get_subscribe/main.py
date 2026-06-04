#!/usr/bin/env python3
"""get_subscribe - CLI entry point

This module provides the command-line interface for the get-subscribe package.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .fetcher import GetSubscribe
from . import __version__


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='get-subscribe',
        description='免费机场/VPN 订阅自动获取工具 - Clash / V2Ray / Trojan / SSR 订阅链接自动抓取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  get-subscribe                    # 抓取订阅并保存到默认目录
  get-subscribe --output ./subs    # 保存到指定目录
  get-subscribe --check-only       # 仅检查不保存
  get-subscribe --show-info        # 显示订阅信息
  get-subscribe --version          # 显示版本信息

输出文件:
  clash.yml  - Clash/Mihomo 配置文件
  v2ray.txt  - V2Ray/XRay 订阅文件

更多信息请访问: https://github.com/adminlove520/get_subscribe
        '''
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        type=str,
        default=None,
        help='订阅文件保存目录 (默认: ./subscribe)'
    )
    
    parser.add_argument(
        '-l', '--log-dir',
        dest='log_dir',
        type=str,
        default=None,
        help='日志文件保存目录 (默认: ./log)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='仅检查订阅可用性，不保存文件'
    )
    
    parser.add_argument(
        '--show-info',
        action='store_true',
        help='显示订阅文件详细信息'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    return parser.parse_args()


def show_subscription_info(subscribe_dir: Path) -> None:
    """显示订阅文件信息."""
    print("\n" + "="*60)
    print("订阅文件信息")
    print("="*60)
    
    clash_file = subscribe_dir / "clash.yml"
    v2ray_file = subscribe_dir / "v2ray.txt"
    
    if clash_file.exists():
        size = clash_file.stat().st_size
        mtime = clash_file.stat().st_mtime
        from datetime import datetime
        modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n✓ Clash 配置文件 (clash.yml)")
        print(f"  大小: {size:,} 字节")
        print(f"  更新: {modified}")
        print(f"  路径: {clash_file}")
    else:
        print("\n✗ Clash 配置文件不存在")
    
    if v2ray_file.exists():
        size = v2ray_file.stat().st_size
        mtime = v2ray_file.stat().st_mtime
        from datetime import datetime
        modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # 尝试读取节点数量
        try:
            content = v2ray_file.read_text(encoding='utf-8')
            lines = [l for l in content.split('\n') if l.strip() and not l.startswith('#')]
            node_count = len(lines)
        except:
            node_count = "未知"
        
        print(f"\n✓ V2Ray 订阅文件 (v2ray.txt)")
        print(f"  大小: {size:,} 字节")
        print(f"  节点: ~{node_count} 条")
        print(f"  更新: {modified}")
        print(f"  路径: {v2ray_file}")
    else:
        print("\n✗ V2Ray 订阅文件不存在")
    
    print("\n" + "="*60)
    print("使用提示")
    print("="*60)
    print("\nClash 订阅导入:")
    print("  - Clash for Windows: 复制文件 -> 导入")
    print("  - ClashX: 拖拽文件到窗口")
    print("  - Android: 导入配置文件")
    
    print("\nV2Ray 订阅导入:")
    print("  - v2rayN: 订阅 -> 从剪贴板导入")
    print("  - Qv2ray: 配置 -> 导入")
    print("  - Shadowrocket: 订阅 -> 添加")
    print()


def main():
    """CLI entry point for get-subscribe command."""
    args = parse_args()
    
    # 如果只显示信息
    if args.show_info:
        # 获取默认订阅目录
        base = Path(__file__).parent.parent
        subscribe_dir = Path(args.output_dir or base / "subscribe")
        show_subscription_info(subscribe_dir)
        return
    
    # 设置日志级别
    import logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # 创建 fetcher 实例
    fetcher = GetSubscribe(
        subscribe_dir=args.output_dir,
        log_dir=args.log_dir,
        check_only=args.check_only
    )
    
    # 执行抓取
    print(f"\n{'='*60}")
    print(f"get-subscribe v{__version__} - 免费订阅获取工具")
    print(f"{'='*60}\n")
    
    results = fetcher.run()
    
    # 显示结果摘要
    if results:
        print(f"\n{'='*60}")
        print("抓取完成！")
        print(f"{'='*60}")
        for name, status in results.items():
            status_icon = "✓" if status == 200 else "✗"
            print(f"{status_icon} {name.upper()}: HTTP {status}")
        
        if not args.check_only:
            print(f"\n文件已保存到: {fetcher.subscribe_dir}")
            print("\n使用 'get-subscribe --show-info' 查看详细信息")
    else:
        print(f"\n{'='*60}")
        print("抓取失败或暂无更新")
        print(f"{'='*60}")
        print("\n可能的原因:")
        print("  1. RSS 源暂时无法访问")
        print("  2. 网络连接问题")
        print("  3. 暂无新的订阅内容")
        print("\n请稍后重试或检查网络连接")


if __name__ == "__main__":
    main()
