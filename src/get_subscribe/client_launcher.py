import os
import sys
import shutil
import subprocess
from pathlib import Path


class ClientLauncher:
    def __init__(self, client, verbose=False):
        self.client = client
        self.verbose = verbose
    
    def find_executable(self):
        exe_name = self.client.exe_name
        if not exe_name:
            return None
        
        # Check common AppData locations
        appdata_paths = [
            Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs")),
            Path(os.path.expandvars(r"%APPDATA%")),
        ]
        
        # Special handling for Clash Verge (Windows Store app)
        if "verge" in self.client.name.lower():
            # Check Windows Apps directory
            windows_apps = Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps"))
            if windows_apps.exists():
                try:
                    for app_dir in windows_apps.glob("ClashVerge_*"):
                        exe = list(app_dir.glob("Clash Verge.exe")) or list(app_dir.glob("*.exe"))
                        if exe:
                            return exe[0]
                except (PermissionError, OSError):
                    pass
        
        # Search in AppData paths
        for base in appdata_paths:
            if not base.exists():
                continue
            try:
                for root, dirs, files in os.walk(base):
                    if exe_name in files:
                        return Path(root) / exe_name
            except (PermissionError, OSError):
                continue
        
        # Check PATH
        return shutil.which(exe_name)
    
    def launch(self):
        if self.verbose:
            print(f"  正在启动 {self.client.name}...")
        
        # Special handling for Windows Store apps
        if "verge" in self.client.name.lower():
            return self._launch_windows_store_app()
        
        exe_path = self.find_executable()
        if not exe_path:
            if self.verbose:
                print(f"  ✗ 无法找到 {self.client.name}")
            return False
        
        try:
            if sys.platform == "win32":
                os.startfile(str(exe_path))
            else:
                subprocess.Popen([str(exe_path)], start_new_session=True)
            
            if self.verbose:
                print(f"  ✓ {self.client.name} 已启动")
            return True
        except Exception as e:
            if self.verbose:
                print(f"  ✗ 启动失败: {e}")
            return False
    
    def _launch_windows_store_app(self):
        """Launch Windows Store app using URI scheme or explorer"""
        try:
            # Try to launch Windows Store app
            # Method 1: Use explorer to launch the app
            app_ids = [
                "io.github.clash-verge-rev.clash-verge-rev",
            ]
            
            for app_id in app_ids:
                try:
                    # Use Windows Start menu protocol
                    subprocess.run(["cmd", "/c", "start", "", "shell:AppsFolder\\\\" + app_id], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if self.verbose:
                        print(f"  ✓ {self.client.name} 已启动")
                    return True
                except:
                    continue
            
            # Method 2: Try explorer with AppData path
            appdata_path = Path(os.path.expandvars(r"%APPDATA%\io.github.clash-verge-rev.clash-verge-rev"))
            if appdata_path.exists():
                # Just show a message since the app is likely already running or in tray
                if self.verbose:
                    print(f"  ✓ {self.client.name} 已安装")
                    print(f"    请从系统托盘或开始菜单启动")
                    print(f"    然后刷新订阅选择 'get-subscribe'")
                return True
            
            if self.verbose:
                print(f"  ✗ 无法启动 {self.client.name}")
            return False
        except Exception as e:
            if self.verbose:
                print(f"  ✗ 启动失败: {e}")
            return False
