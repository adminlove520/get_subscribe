#!/usr/bin/env python3
"""get_subscribe - CLI entry point"""

import argparse
import sys
from pathlib import Path

from .fetcher import GetSubscribe
from .client_manager import auto_detect_and_import
from . import __version__


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='get-subscribe',
        description='免费机场/VPN 订阅自动获取工具 - Clash / V2Ray / Trojan / SSR 订阅链接自动抓取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  get-subscribe                    # 抓取订阅并保存
  get-subscribe --auto-import      # 抓取并自动导入到已安装的客户端
  get-subscribe --show-info        # 显示订阅信息
  get-subscribe --version          # 显示版本

支持的客户端:
  Clash for Windows, ClashX, Clash Verge, v2rayN, Qv2ray

更多信息: https://github.com/adminlove520/get_subscribe
        '''
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('-o', '--output', dest='output_dir', type=str, default=None, help='订阅文件保存目录')
    parser.add_argument('-l', '--log-dir', dest='log_dir', type=str, default=None, help='日志文件保存目录')
    parser.add_argument('--check-only', action='store_true', help='仅检查不保存')
    parser.add_argument('--show-info', action='store_true', help='显示订阅文件信息')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    # Auto import feature
    parser.add_argument('--auto-import', action='store_true', help='自动导入到已安装的 VPN 客户端')
    parser.add_argument('--import-only', action='store_true', help='仅导入已有订阅（不抓取）')
    
    return parser.parse_args()


def show_subscription_info(subscribe_dir: Path) -> None:
    """Display subscription file info."""
    print("\n" + "="*60)
    print("订阅文件信息")
    print("="*60)
    
    clash_file = subscribe_dir / "clash.yml"
    v2ray_file = subscribe_dir / "v2ray.txt"
    
    from datetime import datetime
    
    if clash_file.exists():
        size = clash_file.stat().st_size
        mtime = clash_file.stat().st_mtime
        modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n✓ Clash 配置 (clash.yml)")
        print(f"  大小: {size:,} 字节 | 更新: {modified}")
    else:
        print("\n✗ Clash 配置不存在")
    
    if v2ray_file.exists():
        size = v2ray_file.stat().st_size
        mtime = v2ray_file.stat().st_mtime
        modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        content = v2ray_file.read_text(encoding='utf-8')
        lines = [l for l in content.split('\n') if l.strip()]
        print(f"\n✓ V2Ray 订阅 (v2ray.txt)")
        print(f"  大小: {size:,} 字节 | 节点: ~{len(lines)} 条 | 更新: {modified}")
    else:
        print("\n✗ V2Ray 订阅不存在")
    
    print("\n" + "="*60)


def main():
    """CLI entry point."""
    args = parse_args()
    
    import logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    base = Path(__file__).parent.parent
    subscribe_dir = Path(args.output_dir or base / "subscribe")
    
    # Show info only
    if args.show_info:
        show_subscription_info(subscribe_dir)
        return
    
    print(f"\n{'='*60}")
    print(f"get-subscribe v{__version__} - 免费订阅获取工具")
    print(f"{'='*60}\n")
    
    # Skip fetching if import-only
    if not args.import_only:
        fetcher = GetSubscribe(
            subscribe_dir=args.output_dir,
            log_dir=args.log_dir,
            check_only=args.check_only
        )
        results = fetcher.run()
        
        if not results:
            print("\n抓取失败或暂无更新")
            return
    
    # Auto import to VPN clients
    if args.auto_import or args.import_only:
        detected, imported = auto_detect_and_import(subscribe_dir, verbose=True)
        
        print(f"\n{'='*60}")
        if detected > 0:
            print(f"✓ 检测到 {detected} 个客户端，成功导入 {imported} 个")
        else:
            print("未检测到已安装的 VPN 客户端")
            print("\n支持的客户端:")
            print("  • Clash for Windows")
            print("  • ClashX / Clash Verge")  
            print("  • v2rayN / Qv2ray")
        print(f"{'='*60}")
    elif not args.check_only:
        print(f"\n✓ 订阅已保存到: {subscribe_dir}")
        print("\n使用 'get-subscribe --auto-import' 自动导入到 VPN 客户端")


if __name__ == "__main__":
    main()
