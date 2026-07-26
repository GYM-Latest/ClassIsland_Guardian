# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import sys
import subprocess
import winreg

from utils.log import Log

class Exec:
    # 获取当前运行目录 
    @staticmethod
    def get_exe_path():
        '返回当前程序运行的目录。'
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
    
    # 映像劫持清除
    @staticmethod
    def remove_ifeo(name):
        '检测并尝试清除指定项的映像劫持。 传入要启动文件的名称(string) 成功返回True，失败返回False'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}', 0, winreg.KEY_WRITE)    
            winreg.DeleteValue(key, 'Debugger')
            winreg.CloseKey(key)
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, f'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}')
            Log.warn(f'成功删除了映像劫持： SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}')
            return True
        except FileNotFoundError:
            return True
        except OSError:
            return True
        except Exception as e:
            Log.warn(f'尝试删除映像劫持失败，错误为：{e}')
            return False
    
    # 带映像劫持对抗的启动应用程序
    @staticmethod
    def start(path):
        '带映像劫持对抗的启动指定程序。 传入要启动文件的目录(string) 成功返回True，失败返回False'
        name = os.path.basename(path)
        if not Exec.remove_ifeo(name):
            return False
        
        if os.path.exists(os.path.dirname(path)):
            try:
                subprocess.Popen(
                    [path],
                    cwd=os.path.dirname(path),
                    )
                return True
            except Exception as e:
                Log.error(f'启动进程失败，错误是：{e}')
                return False
        else:
            Log.error(f'启动进程失败，目录不存在')
            return False

    # 结束指定进程
    @staticmethod
    def kill_process(name):
        '结束指定进程。 传入要结束的进程名(string)。 成功返回True，失败返回False'
        result = subprocess.run(
        ["TASKKILL", "/F", "/IM", name],
        creationflags=subprocess.CREATE_NO_WINDOW,
        capture_output=True
        )

        if result.returncode == 0 or result.returncode == 128:
            return True
        else:
            return False

    # 清空控制台
    @staticmethod
    def clear_terminal():
        subprocess.run('cls', shell=True)