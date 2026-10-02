# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import random
import re
import shutil
import tempfile
import time

import psutil
import pywinctl as pwc

from utils.exec import ExecClass

# ClassIsland 主程序固定文件名
CLASSISLAND_PROCESS_NAME = "ClassIsland.Desktop.exe"


class ProcessClass:
    def __init__(self, db, log):
        self.db = db
        self.log = log
        self.exec = ExecClass(log)

    # 寻找最优的ClassIsland主程序路径并返回
    def _get_classisland_app_path(self, classisland_path):
        """寻找最优的 ClassIsland 版本路径，传入ClassIsland根路径。成功返回 路径(String) ，失败返回 False"""
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
            return os.path.join(classisland_path, applist[0])
        else:
            return False

    # 校验进程exe路径是否在classisland_path下
    def _is_real_classisland(self, exe):
        "校验进程 exe 路径是否在 classisland_path 下。 真实返回 True，伪造返回 False"
        if not exe:
            return True
        classisland_path = self.db.path.get("classisland_path")
        if not classisland_path:
            return False
        try:
            return os.path.normcase(
                os.path.dirname(os.path.dirname(exe))
            ) == os.path.normcase(classisland_path)
        except Exception:
            return False

    # 检查ClassIsland进程数量并返回
    def get_classisland_status(self):
        "检查Classisland进程数量。 返回Classisland进程数量(int)"
        classisland_process_name = self.db.path.get("classisland_process_name").lower()
        count = 0
        for proc in psutil.process_iter(["name", "exe"]):
            if (
                proc.info.get("name")
                and proc.info["name"].lower() == classisland_process_name
            ) and self._is_real_classisland(proc.info.get("exe")):
                count += 1
        return count

    # 查找ClassIsland进程pid并返回
    def get_classisland_pid(self):
        "查找ClassIsland进程pid。 返回Classisland进程pid(int)，若未找到，返回False(bool)"
        classisland_process_name = self.db.path.get("classisland_process_name").lower()
        classisland_pid = None
        for proc in psutil.process_iter(["name", "pid", "exe"]):
            if (
                proc.info.get("name")
                and proc.info["name"].lower() == classisland_process_name
            ) and self._is_real_classisland(proc.info.get("exe")):
                classisland_pid = proc.info["pid"]
        if classisland_pid:
            return classisland_pid
        else:
            return False

    # 查杀不在安装目录下的ClassIsland
    def kill_non_install_classisland(self):
        "尝试查杀不在安装目录下的 ClassIsland 。"
        classisland_process_name = self.db.path.get("classisland_process_name").lower()
        for proc in psutil.process_iter(["name", "exe"]):
            if (
                proc.info.get("name")
                and proc.info["name"].lower() == classisland_process_name
            ) and not self._is_real_classisland(proc.info.get("exe")):
                try:
                    proc.kill()
                    self.log.info("已经成功清除伪造 ClassIsland 进程 ~")
                except Exception as e:
                    self.log.warn(f"清除伪造进程时失败，错误是：{e}")
        return False

    # 检查classisland是否崩溃并返回
    def is_classisland_crash(self):
        "检查 ClassIsland 是否崩溃。 已崩溃返回 True，未崩溃返回 False"
        for win in pwc.getAllWindows():
            if "ClassIsland 崩溃报告" in win.title:
                pass  # 没写完

    # 启动ClassIsland
    def start_classisland(self):
        """依次尝试：删除 IFEO 劫持项，直接启动启动器，绕过启动器直接启动主程序。 成功返回 True ，失败返回 False"""
        self.exec.remove_ifeo(self.db.path.get("classisland_process_name"))

        classisland_path = self.db.path.get("classisland_path")
        classisland_launcher_name = self.db.path.get("classisland_launcher_name")
        classisland_launcher_path = os.path.join(
            classisland_path, classisland_launcher_name
        )
        classisland_process_name = self.db.path.get("classisland_process_name")
        if not self._get_classisland_app_path(classisland_path):
            # 找不到可用版本不尝试启动
            return False
        classisland_process_path = os.path.join(
            self._get_classisland_app_path(classisland_path), classisland_process_name
        )
        # 文件丢失就不尝试启动
        if not classisland_process_path or not os.path.exists(
            classisland_launcher_path
        ):
            return False
        # 直接启动启动器
        if self.exec.start(classisland_launcher_path):
            time.sleep(5)
            status = self.get_classisland_status()
            if status >= 1:
                self.log.info("拉起成功，ClassIsland进程正常 ~")
                return True
        self.log.warn("启动启动器失败，尝试直接启动主程序 ~")
        # 绕过启动器直接启动主程序
        if self.exec.start(classisland_process_path):
            time.sleep(5)
            status = self.get_classisland_status()
            if status >= 1:
                self.log.info("拉起成功，ClassIsland进程正常 ~")
                return True
        self.log.warn("直接启动主程序失败。")
        return False

    # 关闭ClassIsland
    def kill_classisland(self):
        "关闭Classisland。 成功返回True，失败返回False"
        if not self.exec.kill_process(self.db.path.get("classisland_process_name")):
            self.log.info("关闭失败")
            return False
        return True

    # 重启ClassIsland
    def reboot_classisland(self):
        "重启Classisland。 成功返回True，失败返回False"
        if not self.kill_classisland():
            self.log.info("重启失败")
            return False
        time.sleep(3)
        if not self.start_classisland():
            self.log.info("重启失败")
            return False
        self.log.info("重启成功")
        return True

    # 生成随机文件名
    @staticmethod
    def _get_random_name(k=6):
        return "tmp_" + "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=k)
        )

    # 清理历史逃逸启动遗留的临时目录
    def _cleanup_old_escape_dirs(self):
        """清理历史逃逸启动遗留的临时目录与文件。 成功返回True，失败返回False"""
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
                        self.log.info(f"成功清理了遗留的逃逸目录：{path}")

            current_name = self.db.path.get("classisland_process_name", "")
            tmp_pattern = re.compile(
                r"^tmp_[a-z0-9]{6}\.(exe|com|hellowrc)$", re.IGNORECASE
            )
            if classisland_path and os.path.isdir(classisland_path):
                for root, _, files in os.walk(classisland_path):
                    for fname in files:
                        if not tmp_pattern.match(fname):
                            continue
                        if fname.lower() == current_name.lower():
                            continue
                        try:
                            os.remove(os.path.join(root, fname))
                            self.log.info(
                                f"成功清理了遗留的逃逸文件：{os.path.join(root, fname)}"
                            )
                        except OSError:
                            pass

            return True
        except OSError:
            return False

    # 逃逸式启动ClassIsland
    def escape_start_classisland(self):
        """依次尝试：删除 IFEO 劫持项，原目录改名启动，复制到随机目录启动，随机目录改名启动。 成功返回 True ，失败返回 False"""
        self.exec.remove_ifeo(self.db.path.get("classisland_process_name"))

        classisland_path = self.db.path.get("classisland_path")
        classisland_process_name = self.db.path.get("classisland_process_name")
        classisland_process_dir = self._get_classisland_app_path(classisland_path)
        if not classisland_process_dir:
            return False

        self._cleanup_old_escape_dirs()

        _tmp_file_name = self._get_random_name()
        # 原目录改名启动
        for _suffix in (".exe", ".com", ".HelloWRC"):
            _renamed_path = os.path.join(
                classisland_process_dir, f"{_tmp_file_name}{_suffix}"
            )
            try:
                shutil.copy2(
                    os.path.join(classisland_process_dir, classisland_process_name),
                    _renamed_path,
                )
            except OSError as e:
                self.log.warn(f"原目录改名启动复制失败，错误是：{e}")
                continue
            if self.exec.start_and_check(_renamed_path):
                self.log.info("拉起成功，ClassIsland进程正常 ~")
                self.db.path["classisland_process_name"] = f"{_tmp_file_name}{_suffix}"
                return True

        # 复制到随机目录启动
        escape_classisland_path = tempfile.mkdtemp(
            prefix="cig_", dir=os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
        )
        is_success = False
        try:
            shutil.copytree(
                classisland_path, escape_classisland_path, dirs_exist_ok=True
            )
            escape_classisland_process_path = self._get_classisland_app_path(
                escape_classisland_path
            )
            if not escape_classisland_process_path:
                return False
            # 立刻指向逃逸目录
            self.db.path["classisland_path"] = escape_classisland_path

            # 原名启动
            if self.exec.start_and_check(
                os.path.join(escape_classisland_process_path, classisland_process_name)
            ):
                self.log.info("拉起成功，ClassIsland进程正常 ~")
                is_success = True
                return True

            # 随机目录改名启动
            for _suffix in (".exe", ".com", ".HelloWRC"):
                _renamed_path = os.path.join(
                    escape_classisland_process_path, f"{_tmp_file_name}{_suffix}"
                )
                shutil.copy2(
                    os.path.join(
                        escape_classisland_process_path, classisland_process_name
                    ),
                    _renamed_path,
                )
                if self.exec.start_and_check(_renamed_path):
                    self.log.info("拉起成功，ClassIsland进程正常 ~")
                    is_success = True
                    self.db.path["classisland_process_name"] = (
                        f"{_tmp_file_name}{_suffix}"
                    )
                    return True
        except Exception as e:
            self.log.error(f"启动时出错，错误是：{e}")
        finally:
            if not is_success:
                # 失败：还原路径并清理逃逸目录
                self.db.path["classisland_path"] = classisland_path
                shutil.rmtree(escape_classisland_path, ignore_errors=True)
        self.log.warn("所有启动方法均失败。")
        return False

    # 检查ClassIsland日志写入最后日期来检查ClassIsland是否卡死
    def is_classisland_frozen(self):
        classisland_log_path = os.path.join(
            self.db.path.get("classisland_path"), "data", "Logs"
        )
        files = [
            os.path.join(classisland_log_path, f)
            for f in os.listdir(classisland_log_path)
            if f.startswith("log-") and f.endswith(".log")
        ]
        if not files:
            return True
        latest_file = max(files, key=os.path.getmtime)

        last_mtime = os.path.getmtime(latest_file)
        now = time.time()
        elapsed = now - last_mtime

        self.log.info(
            f"检查了 ClassIsland 日志，最后写入日期是：{time.ctime(last_mtime)}，距现在：{int(elapsed)}s"
        )
        return elapsed < 70
