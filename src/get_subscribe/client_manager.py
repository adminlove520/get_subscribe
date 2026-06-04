#!/usr/bin/env python3
"""VPN Client Manager"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from typing import Tuple


class VPNClient:
    def __init__(self, name, config_dir, exe_name=None, import_method="copy"):
        self.name = name
        self.config_dir = Path(os.path.expandvars(config_dir))
        self.exe_name = exe_name
        self.import_method = import_method


class ClientDetector:
    WINDOWS_CLIENTS = [
        VPNClient("Clash for Windows", r"%USERPROFILE%\.config\Clash"),
        VPNClient("ClashX", r"%USERPROFILE%\.config\clash"),
        VPNClient("Clash Verge", r"%USERPROFILE%\.config\clash", import_method="profiles"),
        VPNClient("v2rayN", r"%USERPROFILE%\v2rayN", import_method="clipboard"),
    ]
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.installed_clients = []
    
    def detect_all(self):
        self.installed_clients = []
        for client in self.WINDOWS_CLIENTS:
            if client.config_dir.exists():
                self.installed_clients.append(client)
        return self.installed_clients


class SubscriptionImporter:
    def __init__(self, client, subscribe_dir, verbose=False):
        self.client = client
        self.subscribe_dir = subscribe_dir
        self.verbose = verbose
    
    def import_subscription(self):
        if "verge" in self.client.name.lower():
            return self._import_clash_verge()
        elif "clash" in self.client.name.lower():
            return self._import_clash()
        elif "v2ray" in self.client.name.lower():
            return self._import_v2ray()
        return False
    
    def _import_clash_verge(self):
        clash_file = self.subscribe_dir / "clash.yml"
        if not clash_file.exists():
            return False
        
        try:
            timestamp = int(time.time() * 1000)
            profile_name = f"get-subscribe-{timestamp}.yml"
            profiles_dir = self.client.config_dir / "profiles"
            list_file = profiles_dir / "list.yml"
            
            profiles_dir.mkdir(parents=True, exist_ok=True)
            target = profiles_dir / profile_name
            shutil.copy2(clash_file, target)
            
            self._update_clash_verge_list(list_file, profile_name)
            
            if self.verbose:
                print(f"  ✓ Clash Verge 订阅已导入: {profile_name}")
                print(f"    请在 Clash Verge 中点击订阅管理刷新")
            return True
        except Exception as e:
            if self.verbose:
                print(f"  ✗ 导入失败: {e}")
            return False
    
    def _update_clash_verge_list(self, list_file, profile_name):
        if not list_file.exists():
            default_content = f"""files:
  - time: {profile_name}
    name: get-subscribe
    mode: rule
    interval: 12
index: 0
"""
            list_file.write_text(default_content, encoding='utf-8')
            return
        
        content = list_file.read_text(encoding='utf-8')
        
        if profile_name in content:
            return
        
        new_entry = f"""  - time: {profile_name}
    name: get-subscribe
    mode: rule
    interval: 12
"""
        
        if 'index:' in content:
            content = content.replace('index:', new_entry + 'index:')
        else:
            content = content.rstrip() + '\n' + new_entry + 'index: 0\n'
        
        list_file.write_text(content, encoding='utf-8')
    
    def _import_clash(self):
        clash_file = self.subscribe_dir / "clash.yml"
        if not clash_file.exists():
            return False
        
        try:
            profiles_dir = self.client.config_dir / "profiles"
            if profiles_dir.exists():
                timestamp = int(time.time() * 1000)
                target = profiles_dir / f"get-subscribe-{timestamp}.yml"
                shutil.copy2(clash_file, target)
            else:
                target = self.client.config_dir / "get-subscribe.yml"
                shutil.copy2(clash_file, target)
            
            if self.verbose:
                print(f"  ✓ Clash 订阅已导入")
            return True
        except Exception as e:
            if self.verbose:
                print(f"  ✗ 导入失败: {e}")
            return False
    
    def _import_v2ray(self):
        v2ray_file = self.subscribe_dir / "v2ray.txt"
        if not v2ray_file.exists():
            return False
        
        try:
            content = v2ray_file.read_text(encoding='utf-8')
            subprocess.run(['clip'], input=content.encode('utf-16-le'), check=True)
            
            if self.verbose:
                print(f"  ✓ V2Ray 订阅已复制到剪贴板")
                print(f"    请在 {self.client.name} 中从剪贴板导入")
            return True
        except Exception as e:
            if self.verbose:
                print(f"  ✗ 导入失败: {e}")
            return False


def auto_detect_and_import(subscribe_dir, verbose=False):
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
        
        importer = SubscriptionImporter(client, subscribe_dir, verbose=verbose)
        if importer.import_subscription():
            success_count += 1
    
    return len(clients), success_count
