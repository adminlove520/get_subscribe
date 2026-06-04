#!/usr/bin/env python3
"""VPN Client Manager - Auto-detect and import subscriptions"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VPNClient:
    """VPN Client Info"""
    
    def __init__(self, name: str, config_dir: str, exe_name: str = None,
                 import_method: str = "copy"):
        self.name = name
        self.config_dir = Path(config_dir)
        self.exe_name = exe_name
        self.import_method = import_method


class ClientDetector:
    """VPN Client Detector"""
    
    WINDOWS_CLIENTS = [
        VPNClient("Clash for Windows", r"%USERPROFILE%\.config\Clash", "Clash for Windows.exe"),
        VPNClient("ClashX", r"%USERPROFILE%\.config\clash", "ClashX.exe"),
        VPNClient("Clash Verge", r"%USERPROFILE%\.config\clash-verge", "clash-verge.exe"),
        VPNClient("v2rayN", r"%USERPROFILE%\v2rayN", "v2rayN.exe"),
        VPNClient("Qv2ray", r"%USERPROFILE%\Qv2ray\config", "Qv2ray.exe"),
    ]
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.installed_clients: List[VPNClient] = []
    
    def detect_all(self) -> List[VPNClient]:
        """Detect all installed clients"""
        self.installed_clients = []
        
        for client in self.WINDOWS_CLIENTS:
            client.config_dir = Path(os.path.expandvars(str(client.config_dir)))
            
            # Check if installed
            if self._is_client_installed(client):
                self.installed_clients.append(client)
        
        return self.installed_clients
    
    def _is_client_installed(self, client: VPNClient) -> bool:
        """Check if client is installed"""
        # Check config directory
        if client.config_dir.exists():
            return True
        
        # Check executable in common paths
        if client.exe_name:
            search_paths = [
                os.path.expandvars(r"%PROGRAMFILES%"),
                os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
            ]
            
            for base in search_paths:
                for root, dirs, files in os.walk(base):
                    if client.exe_name in files:
                        return True
        
        return False


class SubscriptionImporter:
    """Subscription Importer"""
    
    def __init__(self, client: VPNClient, subscribe_dir: Path, verbose: bool = False):
        self.client = client
        self.subscribe_dir = subscribe_dir
        self.verbose = verbose
    
    def import_subscription(self) -> bool:
        """Import subscription to client"""
        # Determine subscription type
        if "clash" in self.client.name.lower():
            return self._import_clash()
        elif "v2ray" in self.client.name.lower() or "qv2ray" in client.name.lower():
            return self._import_v2ray()
        else:
            # Try both
            return self._import_clash() or self._import_v2ray()
    
    def _import_clash(self) -> bool:
        """Import Clash subscription"""
        clash_file = self.subscribe_dir / "clash.yml"
        if not clash_file.exists():
            return False
        
        try:
            self.client.config_dir.mkdir(parents=True, exist_ok=True)
            target = self.client.config_dir / "get-subscribe.yml"
            shutil.copy2(clash_file, target)
            
            if self.verbose:
                print(f"  ✓ Clash 订阅已导入到 {target}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"  ✗ 导入失败: {e}")
            return False
    
    def _import_v2ray(self) -> bool:
        """Import V2Ray subscription"""
        v2ray_file = self.subscribe_dir / "v2ray.txt"
        if not v2ray_file.exists():
            return False
        
        try:
            # Copy to clipboard for v2rayN
            if "v2rayn" in client.name.lower():
                content = v2ray_file.read_text(encoding='utf-8')
                subprocess.run(['clip'], input=content.encode('utf-16-le'), check=True)
                if self.verbose:
                    print(f"  ✓ V2Ray 订阅已复制到剪贴板")
                return True
            else:
                self.client.config_dir.mkdir(parents=True, exist_ok=True)
                target = self.client.config_dir / "get-subscribe.txt"
                shutil.copy2(v2ray_file, target)
                if self.verbose:
                    print(f"  ✓ V2Ray 订阅已导入到 {target}")
                return True
        except Exception as e:
            if self.verbose:
                print(f"  ✗ 导入失败: {e}")
            return False


def auto_detect_and_import(subscribe_dir: Path, verbose: bool = False) -> Tuple[int, int]:
    """Auto detect clients and import subscriptions"""
    detector = ClientDetector(verbose=verbose)
    clients = detector.detect_all()
    
    if not clients:
        return 0, 0
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"检测到 {len(clients)} 个 VPN 客户端")
        print(f"{'='*60}")
    
    success_count = 0
    for i, client in enumerate(clients, 1):
        if verbose:
            print(f"\n{i}. {client.name}")
        
        importer = SubscriptionImporter(client, subscribe_dir, verbose)
        if importer.import_subscription():
            success_count += 1
    
    return len(clients), success_count
