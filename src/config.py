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

import readchar

from utils.database import Database
from utils.exec import Exec
from utils.log import Log
from utils.snapshot import Snapshot
from utils.version import CODENAME, VERSION


def check_password():
    while True:
        Exec.clear_terminal()
        print("请输入管理员密码 ~\n")
        print("(为安全考虑，输入将不可见)")
        password = getpass.getpass(">")
        if hashlib.sha256(password.encode("utf-8")).hexdigest() == db.config.get(
            "password"
        ):
            return True
        else:
            print("唔... 密码不对呢，再试试吧")
            time.sleep(1)


def _delete_key_tree(root, sub_key):
    """递归删除注册表键（含子键和值）。 成功返回 True，键不存在返回 False。"""
    try:
        key = winreg.OpenKey(root, sub_key, 0, winreg.KEY_READ)
    except FileNotFoundError:
        return False
    subkeys = []
    try:
        i = 0
        while True:
            try:
                subkeys.append(winreg.EnumKey(key, i))
                i += 1
            except OSError:
                break
    finally:
        winreg.CloseKey(key)
    for child in subkeys:
        _delete_key_tree(root, f"{sub_key}\\{child}")
    winreg.DeleteKey(root, sub_key)
    return True


def prepare_uninstall():
    """准备卸载程序：删除 launcher、file、process、registry 服务及注册表键。"""
    try:
        Exec.clear_terminal()

        print("将在倒计时结束后开始卸载 ~")
        for i in range(5, 0, -1):
            print(i, end=" ", flush=True)
            time.sleep(1)

        print("\n")

        # 直接删除服务注册表键
        for service in ["launcher", "file", "process", "registry"]:
            deleted = _delete_key_tree(
                winreg.HKEY_LOCAL_MACHINE,
                f"SYSTEM\\CurrentControlSet\\Services\\{service}",
            )
            if deleted:
                print(f"{service} 服务已删除 ~")
            else:
                print(f"{service} 服务不存在，跳过 ~")

        # 创建卸载标识符
        with open(os.path.join(Exec.get_exe_path(), ".uninstall"), "w") as f:
            f.write("")

        # 为卸载程序创建计划任务
        task_name = "ClassIslandGuardianUninstall"
        exe_path = os.path.join(Exec.get_exe_path(), "uninstall.exe")
        subprocess.run(
            [
                "schtasks",
                "/Create",
                "/TN",
                task_name,
                "/TR",
                f'"{exe_path}"',
                "/SC",
                "ONLOGON",
                "/RL",
                "HIGHEST",
                "/F",
            ],
            capture_output=True,
            check=False,
        )
        print("卸载准备完成，重启后将会自动卸载 ~")
        return True
    except Exception as e:
        Log.error(f"卸载准备时出错，错误是：{e}")
        return False


def main():
    # 确保以管理员权限运行
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return

    global db
    global Snapshot
    db = Database(Exec.get_exe_path())
    if not db.read_database():
        sys.exit()
    Snapshot = Snapshot(db)

    # 身份验证
    if db.config.get("password"):
        check_password()

    # 显示主菜单
    while True:
        Exec.clear_terminal()
        print(f"""ClassIsland Guardian Config
版本：{VERSION} | ({CODENAME})
    """)
        print("身份验证通过，欢迎回来 ~\n")
        print("""[1] 保护控制
[2] ClassIsland 快照管理
[3] 查看日志
[4] 系统设置
[5] 关于
[0] 退出管理程序
""")
        result = readchar.readchar()
        # 保护设置
        if result == "1":
            while True:
                Exec.clear_terminal()
                if os.path.exists(
                    os.path.join(Exec.get_exe_path(), ".tempstopprotect")
                ):
                    print("当前状态：保护暂时关闭，下次启动将会恢复 ~")
                elif os.path.exists(os.path.join(Exec.get_exe_path(), ".stopprotect")):
                    print("当前状态：保护关闭 QwQ")
                else:
                    print("当前状态：保护运行中")
                print()
                print("""请选择要进行的操作 ~
[1] 暂时关闭保护（重启后自动恢复）
[2] 关闭保护（需要手动恢复...）
[3] 重新启动保护
[0] 返回
""")
                result = readchar.readchar()
                if result == "1":
                    with open(
                        os.path.join(Exec.get_exe_path(), ".tempstopprotect"), "w"
                    ) as f:
                        f.write("")
                elif result == "2":
                    with open(
                        os.path.join(Exec.get_exe_path(), ".stopprotect"), "w"
                    ) as f:
                        f.write("")
                elif result == "3":
                    if os.path.exists(
                        os.path.join(Exec.get_exe_path(), ".tempstopprotect")
                    ):
                        os.remove(os.path.join(Exec.get_exe_path(), ".tempstopprotect"))
                    if os.path.exists(
                        os.path.join(Exec.get_exe_path(), ".stopprotect")
                    ):
                        os.remove(os.path.join(Exec.get_exe_path(), ".stopprotect"))
                elif result == "0":
                    break
        # 快照管理
        elif result == "2":
            while True:
                Exec.clear_terminal()
                print("""请选择要进行的操作 ~
[1] 查看与管理 ClassIsland 当前已有快照
[2] 拍摄新 ClassIsland 快照
[0] 返回
    """)
                result = readchar.readchar()
                try:
                    if result == "1":
                        while True:
                            Exec.clear_terminal()
                            snapshot_list = Snapshot.list_snapshot()
                            if snapshot_list:
                                for num, this_snapshot in enumerate(
                                    snapshot_list, start=1
                                ):
                                    print(f"[{num}] {this_snapshot}")
                                print("请输入要操作的快照序号 ~ (输入 0 以返回)")
                                result = input(">")
                                if result == "0":
                                    break
                                else:
                                    select_snapshot = result
                                    while True:
                                        Exec.clear_terminal()
                                        print("""请选择要进行的操作 ~
[1] 恢复到所选快照
[2] 删除所选快照
[0] 返回
""")
                                        result = readchar.readchar()
                                        if result == "1":
                                            print("正在恢复快照，稍安勿躁 ~")
                                            Snapshot.restore_snapshot(
                                                snapshot_list[int(select_snapshot) - 1]
                                            )
                                            time.sleep(1)
                                            break
                                        elif result == "2":
                                            print("正在删除快照，稍安勿躁 ~")
                                            Snapshot.remove_snapshot(
                                                snapshot_list[int(select_snapshot) - 1]
                                            )
                                            time.sleep(1)
                                            break
                                        elif result == "0":
                                            break

                    elif result == "2":
                        print("正在创建快照，稍安勿躁 ~~~")
                        result = Snapshot.create_snapshot()
                        if result:
                            print(f"成功创建了新快照 ~ ：{result}")
                        time.sleep(1)
                        break
                    elif result == "0":
                        break
                except Exception as e:
                    Log.error(f"快照操作失败，错误为：{e}")
                    time.sleep(1)
        # 日志菜单
        elif result == "3":
            while True:
                Exec.clear_terminal()
                print("""请选择要查看的日志类型 ~
[1] Guardian 主程序日志
[2] Recovery 预启动修复日志
[0] 返回
""")
                result = readchar.readchar()
                try:
                    if result == "1":
                        os.startfile(
                            os.path.join(Exec.get_exe_path(), "data", "guardian.log")
                        )
                        break
                    if result == "2":
                        shutil.copy2(
                            os.path.join(
                                os.path.splitdrive(Exec.get_exe_path())[0] + "\\",
                                "GuardianRecovery",
                                "recovery.log",
                            ),
                            os.path.join(os.environ.get("TEMP"), "recovery.log"),
                        )
                        os.startfile(
                            os.path.join(os.environ.get("TEMP"), "recovery.log")
                        )
                        break
                    if result == "0":
                        break
                except Exception as e:
                    Log.error(f"打开日志文件失败，错误为：{e}")
                    time.sleep(1)
        # 系统设置
        elif result == "4":
            while True:
                Exec.clear_terminal()
                print("""请选择要进行的操作
[1] 卸载 Guardian
[0] 退出""")
                result = readchar.readchar()
                if result == "1":
                    prepare_uninstall()
                    break
                elif result == "0":
                    break

        # 关于
        elif result == "5":
            Exec.clear_terminal()
            print(f"""ClassIsland Guardian 配置管理程序
版本：{VERSION} ({CODENAME})
作者：GYM_Latest
许可证：GPL-3.0-only
仓库：https://github.com/SXSJGYM/ClassIsland_Guardian

本程序是 ClassIsland 的守护程序，采用应用层守护、驱动层保护与预启动修复
三层防护架构，保护 ClassIsland 不被意外退出或恶意终止。

使用的第三方库：
- psutil —— 进程检测与快照压缩
- APScheduler —— 守护任务线程调度
- pywin32 —— Windows API 交互（提权、关机拦截等）
- readchar —— 单键菜单交互
- prompt-toolkit —— 安装向导交互（setup）

内嵌的第三方开源模块（基于上游代码做了少量修改）：
- grintor/win_graceful_shutdown —— Windows 优雅关机处理（拦截结束请求、优雅退出）
  （https://github.com/grintor/win_graceful_shutdown）
- murrayju/CreateProcessAsUser —— 在用户会话中启动进程（launcher 服务使用）
  （https://github.com/murrayju/CreateProcessAsUser）

关联的第三方项目：
- ClassIsland —— 本程序守护的对象（https://github.com/ClassIsland/ClassIsland）
""")
            print("按任意键返回 ~")
            readchar.readchar()
        # 退出
        elif result == "0":
            sys.exit(0)
        else:
            pass


if __name__ == "__main__":
    main()
