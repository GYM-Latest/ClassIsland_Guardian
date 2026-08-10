# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import random
import shutil
import tempfile
import time

import psutil

from utils.exec import Exec
from utils.log import Log

Log = Log("process")

# ClassIsland 主程序固定文件名
CLASSISLAND_PROCESS_NAME = "ClassIsland.Desktop.exe"


class Process:
    def __init__(self, db):
        self.db = db

    # 寻找最优的ClassIsland主程序路径并返回
    def _find_classisland_app_path(self):
        """寻找最优的 ClassIsland 主程序可执行文件路径。成功返回 路径(String) ，失败返回 False"""
        classisland_path = self.db.path.get("classisland_path")
        if not os.path.isdir(classisland_path):
            return False
        filelist = os.listdir(classisland_path)
        # 筛选可用的app目录
        applist = []
        for path in filelist:
            app_dir = os.path.join(classisland_path, path)
            if os.path.isdir(app_dir):
                if not path.startswith("app-"):
                    continue
                if os.path.exists(os.path.join(app_dir, ".partial")) or os.path.exists(
                    os.path.join(app_dir, ".destroy")
                ):
                    continue
                if not os.path.exists(os.path.join(app_dir, CLASSISLAND_PROCESS_NAME)):
                    continue
                applist.append(path)

        # 解析版本号函数
        def _get_version_tuple(dir_path):
            name = os.path.basename(dir_path)
            if not name.startswith("app-"):
                return (0, 0, 0, 0)
            parts = name[4:].split(".")
            try:
                return tuple(int(p) for p in parts[:4])
            except ValueError:
                return (0, 0, 0, 0)

        # 排序选出最优版本
        applist.sort(
            key=lambda x: (
                os.path.exists(os.path.join(classisland_path, x, ".current")),
                _get_version_tuple(x),
            ),
            reverse=True,
        )
        if applist and applist[0]:
            return os.path.join(classisland_path, applist[0], CLASSISLAND_PROCESS_NAME)
        else:
            return False

    # 检查ClassIsland进程数量并返回
    def check_classisland_status(self):
        "检查Classisland进程数量。 返回Classisland进程数量(int)"
        return Exec.check_process_status(self.db.path.get("classisland_process_name"))

    # 查找ClassIsland进程pid并返回
    def find_classisland_pid(self):
        "查找ClassIsland进程pid。 返回Classisland进程pid(int)，若未找到，返回False(bool)"
        classisland_process_name = self.db.path.get("classisland_process_name").lower()
        for proc in psutil.process_iter(["name", "pid"]):
            if (
                proc.info.get("name")
                and proc.info["name"].lower() == classisland_process_name
            ):
                return proc.info["pid"]
        return False

    # 启动ClassIsland
    def start_classisland(self):
        """依次尝试：删除 IFEO 劫持项，直接启动启动器，绕过启动器直接启动主程序。 成功返回 True ，失败返回 False"""
        Exec.remove_ifeo(self.db.path.get("classisland_process_name"))

        classisland_path = self.db.path.get("classisland_path")
        classisland_launcher_name = self.db.path.get("classisland_launcher_name")
        classisland_launcher_path = os.path.join(
            classisland_path, classisland_launcher_name
        )
        classisland_process_path = self._find_classisland_app_path()
        # 文件丢失就不尝试启动
        if not classisland_process_path or not os.path.exists(
            classisland_launcher_path
        ):
            return False
        # 直接启动启动器
        if Exec.start(classisland_launcher_path):
            time.sleep(5)
            status = self.check_classisland_status()
            if status == 1:
                Log.info("拉起成功，ClassIsland进程正常 ~")
                return True
        Log.warn("启动启动器失败，尝试直接启动主程序 ~")
        # 绕过启动器直接启动主程序
        if Exec.start(classisland_process_path):
            time.sleep(5)
            status = self.check_classisland_status()
            if status == 1:
                Log.info("拉起成功，ClassIsland进程正常 ~")
                return True
        Log.warn("直接启动主程序失败。")
        return False

    # 关闭ClassIsland
    def kill_classisland(self):
        "关闭Classisland。 成功返回True，失败返回False"
        if not Exec.kill_process(self.db.path.get("classisland_process_name")):
            Log.info("关闭失败")
            return False
        return True

    # 重启ClassIsland
    def reboot_classisland(self):
        "重启Classisland。 成功返回True，失败返回False"
        if not self.kill_classisland():
            Log.info("重启失败")
            return False
        time.sleep(3)
        if not self.start_classisland():
            Log.info("重启失败")
            return False
        Log.info("重启成功")
        return True

    # 生成随机文件名
    @staticmethod
    def _random_name(k=6):
        return "tmp_" + "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=k)
        )

    # 清理历史逃逸启动遗留的临时目录
    def _cleanup_old_escape_dirs(self):
        """清理历史逃逸启动遗留的临时目录。 成功返回True，失败返回False"""
        classisland_path = self.db.path.get("classisland_path")
        try:
            temp_path = os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
            for entry in os.listdir(temp_path):
                if entry.startswith("cig_"):
                    path = os.path.join(temp_path, entry)
                    if path == classisland_path:
                        continue  # 当前副本可能在运行/待复用，跳过
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
            return True
        except OSError:
            return False

    # 逃逸式启动ClassIsland
    def escape_start_classisland(self):
        """依次尝试：删除 IFEO 劫持项，复制到随机目录启动，改名启动，修改为 .com 后缀启动。 成功返回 True ，失败返回 False"""
        Exec.remove_ifeo(self.db.path.get("classisland_process_name"))

        classisland_path = self.db.path.get("classisland_path")
        classisland_launcher_name = self.db.path.get("classisland_launcher_name")
        classisland_process_path = self._find_classisland_app_path()

        self._cleanup_old_escape_dirs()
        escape_classisland_path = tempfile.mkdtemp(
            prefix="cig_", dir=os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
        )
        is_success = False
        escape_classisland_process_name = None
        try:
            # 复制整个安装目录到随机目录
            shutil.copytree(
                classisland_path, escape_classisland_path, dirs_exist_ok=True
            )
            escape_classisland_launcher_path = os.path.join(
                escape_classisland_path, classisland_launcher_name
            )
            escape_classisland_process_path = os.path.join(
                escape_classisland_path,
                os.path.relpath(classisland_process_path, classisland_path),
            )
            escape_classisland_app_path = os.path.dirname(
                escape_classisland_process_path
            )
            # 直接启动
            if Exec.start(escape_classisland_launcher_path):
                time.sleep(5)
                status = self.check_classisland_status()
                if status == 1:
                    Log.info("拉起成功，ClassIsland进程正常 ~")
                    is_success = True
                    escape_classisland_process_name = CLASSISLAND_PROCESS_NAME
                    return True
            if Exec.start(escape_classisland_process_path):
                time.sleep(5)
                status = self.check_classisland_status()
                if status == 1:
                    Log.info("拉起成功，ClassIsland进程正常 ~")
                    is_success = True
                    escape_classisland_process_name = CLASSISLAND_PROCESS_NAME
                    return True
            Log.warn("目录逃逸启动失败 ~")
            # 改名启动
            random_file_name = self._random_name() + ".exe"
            shutil.copy2(
                escape_classisland_process_path,
                os.path.join(escape_classisland_app_path, random_file_name),
            )
            if Exec.start(os.path.join(escape_classisland_app_path, random_file_name)):
                time.sleep(5)
                status = Exec.check_process_status(random_file_name)
                if status == 1:
                    Log.info("拉起成功，ClassIsland进程正常 ~")
                    is_success = True
                    escape_classisland_process_name = random_file_name
                    return True
            Log.warn("重命名启动失败 ~")
            # 修改为.com后缀启动
            random_com_name = CLASSISLAND_PROCESS_NAME.replace(".exe", ".com")
            shutil.copy2(
                escape_classisland_process_path,
                os.path.join(escape_classisland_app_path, random_com_name),
            )
            if Exec.start(os.path.join(escape_classisland_app_path, random_com_name)):
                time.sleep(5)
                status = Exec.check_process_status(random_com_name)
                if status == 1:
                    Log.info("拉起成功，ClassIsland进程正常 ~")
                    is_success = True
                    escape_classisland_process_name = random_com_name
                    return True
            # 复制主程序为随机名 .com 启动
            random_com_name = self._random_name() + ".com"
            shutil.copy2(
                escape_classisland_process_path,
                os.path.join(escape_classisland_app_path, random_com_name),
            )
            if Exec.start(os.path.join(escape_classisland_app_path, random_com_name)):
                time.sleep(5)
                status = Exec.check_process_status(random_com_name)
                if status == 1:
                    Log.info("拉起成功，ClassIsland进程正常 ~")
                    is_success = True
                    escape_classisland_process_name = random_com_name
                    return True
        except Exception as e:
            Log.error(f"启动时出错，错误是：{e}")
        finally:
            if is_success and escape_classisland_process_name:
                self.db.path["classisland_path"] = escape_classisland_path
                self.db.path["classisland_process_name"] = (
                    escape_classisland_process_name
                )
            elif not is_success:
                # 启动失败，清理文件
                shutil.rmtree(escape_classisland_path, ignore_errors=True)
        Log.warn("所有启动方法均失败。")
        return False
