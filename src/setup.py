# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import ctypes
import getpass
import hashlib
import os
import shutil
import subprocess
import sys
import time
import winreg

import psutil
from prompt_toolkit import prompt

from utils.bcd import Bcd
from utils.database import Database
from utils.exec import Exec
from utils.snapshot import Snapshot
from utils.version import CODENAME, VERSION


class config:
    def __init__(self):
        self.classisland_path = None
        self.guardian_path = None
        self.password = ""


def find_classisland():
    """寻找 ClassIsland 的安装路径。 返回 ClassIsland 的安装路径(String)"""
    process_names = ["ClassIsland.Desktop.exe"]
    for proc in psutil.process_iter(["name", "exe"]):
        if proc.info["name"] in process_names:
            exe_path = proc.info["exe"]
            classisland_path = os.path.dirname(os.path.dirname(exe_path))
            return classisland_path
    return None


def install():
    def _copy_and_log(src, dst):
        print(f"正在安装：{dst}")
        shutil.copy2(src, dst)

    Exec.clear_terminal()

    print("将在倒计时结束后开始安装 ~")
    for i in range(5, 0, -1):
        print(i, end=" ", flush=True)
        time.sleep(1)

    print("\n")

    # 关闭ClassIsland
    Exec.kill_process("ClassIsland.Desktop.exe")

    # 创建目录
    recovery_path = os.path.join(
        os.environ.get("SystemDrive", "C:") + "\\", "GuardianRecovery"
    )
    guardian_path = os.path.join(
        os.environ.get("ProgramFiles", r"C:\Program Files"), "Guardian"
    )

    if not os.path.exists(recovery_path):
        os.makedirs(recovery_path)
        print(f"已创建 {recovery_path} ~")

    # 生成配置文件
    os.makedirs(os.path.join(guardian_path, "data"), exist_ok=True)
    db = Database(guardian_path)
    db.new_database(
        {
            "classisland_path": config.classisland_path,
            "guardian_path": guardian_path,
            "password": hashlib.sha256(config.password.encode("utf-8")).hexdigest()
            if config.password
            else "",
        }
    )
    os.makedirs(os.path.join(recovery_path, "data"), exist_ok=True)
    db = Database(recovery_path)
    db.new_database(
        {
            "classisland_path": config.classisland_path,
            "guardian_path": guardian_path,
            "password": hashlib.sha256(config.password.encode("utf-8")).hexdigest()
            if config.password
            else "",
        }
    )
    print("配置文件已生成 ~\n")

    # 复制 guardian 目录
    shutil.copytree(
        os.path.join(Exec.get_exe_path(), "appdata"),
        guardian_path,
        copy_function=_copy_and_log,
        dirs_exist_ok=True,
    )
    # 复制 GuardianRecovery\stable
    shutil.copytree(
        os.path.join(Exec.get_exe_path(), "appdata"),
        os.path.join(recovery_path, "stable", "appdata"),
        copy_function=_copy_and_log,
        dirs_exist_ok=True,
    )
    shutil.copytree(
        os.path.join(Exec.get_exe_path(), "drivers"),
        os.path.join(recovery_path, "stable", "drivers"),
        copy_function=_copy_and_log,
        dirs_exist_ok=True,
    )
    # 复制并注册内核驱动
    src_drivers_path = os.path.join(Exec.get_exe_path(), "drivers")
    drivers_path = os.path.join(
        os.environ.get("SystemRoot", r"C:\Windows"), "System32", "drivers"
    )

    # file
    shutil.copy2(
        os.path.join(src_drivers_path, "file.sys"),
        os.path.join(drivers_path, "file.sys"),
    )
    subprocess.run(
        [
            "sc",
            "create",
            "file",
            "type=",
            "kernel",
            "start=",
            "boot",
            "binPath=",
            os.path.join(drivers_path, "file.sys"),
        ],
        capture_output=True,
        check=True,
    )
    key = winreg.CreateKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Services\file\Instances\file_Instance",
    )
    winreg.SetValueEx(key, "Altitude", 0, winreg.REG_SZ, "328000")
    winreg.SetValueEx(key, "Flags", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    key = winreg.CreateKey(
        winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\file\Instances"
    )
    winreg.SetValueEx(key, "DefaultInstance", 0, winreg.REG_SZ, "file_Instance")
    winreg.CloseKey(key)
    print("file.sys 已就绪 ~")

    # process
    shutil.copy2(
        os.path.join(src_drivers_path, "process.sys"),
        os.path.join(drivers_path, "process.sys"),
    )
    subprocess.run(
        [
            "sc",
            "create",
            "process",
            "type=",
            "kernel",
            "start=",
            "boot",
            "binPath=",
            os.path.join(drivers_path, "process.sys"),
        ],
        capture_output=True,
        check=True,
    )
    print("process.sys 已就绪 ~")

    # registry
    shutil.copy2(
        os.path.join(src_drivers_path, "registry.sys"),
        os.path.join(drivers_path, "registry.sys"),
    )
    subprocess.run(
        [
            "sc",
            "create",
            "registry",
            "type=",
            "kernel",
            "start=",
            "boot",
            "binPath=",
            os.path.join(drivers_path, "registry.sys"),
        ],
        capture_output=True,
        check=True,
    )
    print("registry.sys 已就绪 ~")

    # 注册 guardian 守护进程服务
    launcher_exe_path = os.path.join(guardian_path, "launcher.exe")
    if os.path.exists(launcher_exe_path):
        # Belike 无保护单兵突入大气层
        subprocess.run(
            [
                "sc",
                "create",
                "launcher",
                "type=",
                "own",
                "start=",
                "auto",
                "binPath=",
                launcher_exe_path,
                "error=",
                "critical",
            ],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["sc", "failure", "launcher", "reset=", "0", "actions=", "reboot/0"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("guardian 已就绪 ~")

    # 创建首个快照
    db.read_database()
    snapshot = Snapshot(db)
    snapshot.snapshot_path = os.path.join(guardian_path, "data", "snapshot")
    print(f"创建了首个快照：{snapshot.create_snapshot('安装时生成的初始快照')} ~")

    # 创建预启动修复环境
    shutil.copy2(
        os.path.join(Exec.get_exe_path(), "recovery", "recovery.wim"),
        os.path.join(recovery_path, "recovery.wim"),
    )
    if not Bcd.create_recovery_bcd():
        print("创建预启动修复环境失败（BCD/boot.sdi） ~")
        sys.exit(1)

    print("安装完成，重启后生效 ~")


def configure():
    # 起始页面
    while True:
        Exec.clear_terminal()
        print("ClassIsland Guardian Installer")
        print(f"版本 {VERSION} | {CODENAME}")
        print("欢迎，该配置向导会帮你完成 ClassIsland Guardian 的安装与配置 ~\n")
        print("要开始，请输入 y 再按 ENTER")
        print("要退出向导，请输入 n 再按 ENTER")
        result = input(">")
        if result == "y":
            break
        elif result == "n":
            return

    # 选择classisland路径
    while True:
        Exec.clear_terminal()
        print("请输入 ClassIsland 的路径 ~")
        print("输好后按 ENTER 就好 ~")
        path = prompt(">", default=(find_classisland() or ""))
        if path != "":
            config.classisland_path = path
            break
        else:
            print("唔... 路径不能为空哦 ~")
            time.sleep(1)

    # 选择密码保护
    while True:
        Exec.clear_terminal()
        print("请设置管理密码 ~（留空则不启用）\n")
        print("为安全起见，输入不会显示出来哦")
        password = getpass.getpass(">")
        if password:
            print("确认密码")
            password_twice = getpass.getpass(">")
            if password == password_twice:
                config.password = password
                break
            else:
                print("唔... 两次密码不一样呢，再试一次吧 ~")
                time.sleep(1)
        else:
            break

    # 开始安装
    while True:
        Exec.clear_terminal()
        print("所有配置都填好啦 ~\n")
        print("输入 install 再按 ENTER 就可以开始安装了")
        print("安装过程中 ClassIsland 会稍微歇一下下 ~")
        print("如果安装过程中杀软的大手发力了，麻烦关一下，非常感谢！ ~")
        if input(">") == "install":
            install()
            break


def main():
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

    global config
    config = config()

    configure()


if __name__ == "__main__":
    main()
