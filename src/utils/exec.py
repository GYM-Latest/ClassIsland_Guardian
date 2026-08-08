# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import ctypes
import os
import subprocess
import sys
import winreg
from ctypes import wintypes

from utils.log import Log


class Exec:
    # 获取当前运行目录
    @staticmethod
    def get_exe_path():
        "返回当前程序运行的目录。"
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    # 映像劫持清除
    @staticmethod
    def remove_ifeo(name):
        "检测并尝试清除指定项的映像劫持。 传入要启动文件的名称(string) 成功返回True，失败返回False"
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                f"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}",
                0,
                winreg.KEY_WRITE,
            )
            winreg.DeleteValue(key, "Debugger")
            winreg.CloseKey(key)
            winreg.DeleteKey(
                winreg.HKEY_LOCAL_MACHINE,
                f"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}",
            )
            Log.warn(
                f"成功删除了映像劫持： SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{name}"
            )
            return True
        except FileNotFoundError:
            return True
        except OSError:
            return True
        except Exception as e:
            Log.warn(f"尝试删除映像劫持失败，错误为：{e}")
            return False

    # 带映像劫持对抗的启动应用程序
    @staticmethod
    def start(path):
        "带映像劫持对抗的启动指定程序。 传入要启动文件的目录(string) 成功返回True，失败返回False"
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
                Log.error(f"启动进程失败，错误是：{e}")
                return False
        else:
            Log.error("启动进程失败，目录不存在")
            return False

    # 结束指定进程
    @staticmethod
    def kill_process(name):
        "结束指定进程。 传入要结束的进程名(string)。 成功返回True"
        import psutil

        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] == name:
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass
        return True

    # 清空控制台
    @staticmethod
    def clear_terminal():
        subprocess.run("cls", shell=True, check=False)

    # 标记为系统关键进程
    @staticmethod
    def make_process_critical():
        """标记当前进程为系统关键进程。 成功返回 True (bool)， 失败返回 False (Bool)"""
        ntdll = ctypes.WinDLL("ntdll.dll")
        RtlSetProcessIsCritical = ntdll.RtlSetProcessIsCritical
        RtlSetProcessIsCritical.argtypes = [
            wintypes.BOOL,
            wintypes.PBOOL,
            wintypes.BOOL,
        ]
        RtlSetProcessIsCritical.restype = wintypes.LONG

        result = RtlSetProcessIsCritical(True, None, False)
        if result == 0:
            Log.info("进程已成功标记为关键进程 ~")
            return True
        else:
            Log.error(f"操作失败，错误码: {result}")
            return False

    # 取消标记为系统关键进程
    @staticmethod
    def unmake_process_critical():
        """取消标记当前进程为系统关键进程。 成功返回 True (bool)， 失败返回 False (Bool)"""
        ntdll = ctypes.WinDLL("ntdll.dll")
        RtlSetProcessIsCritical = ntdll.RtlSetProcessIsCritical
        RtlSetProcessIsCritical.argtypes = [
            wintypes.BOOL,
            wintypes.PBOOL,
            wintypes.BOOL,
        ]
        RtlSetProcessIsCritical.restype = wintypes.LONG

        result = RtlSetProcessIsCritical(False, None, False)
        if result == 0:
            Log.info("已成功取消标记为关键进程 ~")
            return True
        else:
            Log.error(f"操作失败，错误码: {result}")
            return False
