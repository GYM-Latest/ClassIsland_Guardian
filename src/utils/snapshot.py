# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import shutil
import zipfile
from datetime import datetime
from typing import Literal

from utils.database import Database
from utils.exec import ExecClass
from utils.log import LogClass
from utils.process import ProcessClass


class SnapshotClass:
    def __init__(self, db: Database, log: LogClass) -> None:
        self.db = db
        self.log = log
        self.exec = ExecClass(log)
        self.snapshot_path = os.path.join(self.exec.get_exe_path(), "data", "snapshot")
        self.recovery_snapshot_path = os.path.join(
            os.environ.get("SystemDrive", "C:") + "\\",
            "GuardianRecovery",
            "data",
            "snapshot",
        )
        self.process = ProcessClass(db, log)
        self.classisland_path = db.path.get("classisland_path")

    def _zip_dir(self, src: str, dst: str) -> bool:
        "压缩指定文件夹文件到指定路径。 成功返回 True ，失败返回 False"
        try:
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(src):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, src)
                        try:
                            zf.write(file_path, arcname)
                        except Exception as e:
                            self.log.warn(f"压缩文件 {file_path} 时出错，错误是：{e}")
                        self.db.state["snapshot_create_current"] += 1
            return True
        except Exception as e:
            self.log.error(f"压缩文件时出错，错误是：{e}")
            return False

    def list_snapshot(self) -> list[list[str | int]] | Literal[False]:
        "列出所有可用的快照，按创建时间倒序排列。成功返回 [[快照名称, 创建时间, 文件大小], ...]，失败返回 False"
        entries: list[tuple[float, str, int]] = []
        try:
            with os.scandir(self.snapshot_path) as scanned:
                for entry in scanned:
                    if not entry.is_file() or not entry.name.lower().endswith(".zip"):
                        continue
                    stat = entry.stat()
                    entries.append((stat.st_birthtime, entry.name, stat.st_size))

            entries.sort(key=lambda item: (item[0], item[1]), reverse=True)
            return [
                [
                    name,
                    datetime.fromtimestamp(birthtime).strftime("%Y-%m-%d %H:%M:%S"),
                    size,
                ]
                for birthtime, name, size in entries
            ]

        except Exception as e:
            self.log.error(f"列出快照时出错，错误为：{e}")
            return False

    def restore_snapshot(self, name: str) -> bool:
        "恢复到指定的快照。 传入要恢复快照的文件名(string) 成功返回True，失败返回False"
        self.db.state["snapshot_state"] = "restore"
        self.process.kill_classisland()
        if os.path.exists(os.path.join(self.snapshot_path, name)):
            try:
                try:
                    shutil.rmtree(self.classisland_path)
                except:
                    pass
                os.mkdir(self.classisland_path)
                with zipfile.ZipFile(os.path.join(self.snapshot_path, name), "r") as zf:
                    zf.extractall(path=self.classisland_path)
                    self.log.info(f"成功恢复到指定快照：{name}")
                    return True
            except Exception as e:
                self.log.error(f"恢复时出错，错误为：{e}")
                return False
        else:
            self.log.error("恢复时出错，指定的快照文件不存在")
            return False

    def create_snapshot(self, remark: str | None = None) -> str | Literal[False]:
        "创建一个快照。 可选传入一个备注信息(String)。成功返回快照名称，失败返回False。"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if remark:
            zip_name = f"snapshot_{timestamp}_({remark}).zip"
        else:
            zip_name = f"snapshot_{timestamp}.zip"

        try:
            snapshot_total = sum(
                len(files) for _, _, files in os.walk(self.classisland_path)
            )
            self.db.state["snapshot_state"] = "create"
            self.db.state["snapshot_create_total"] = snapshot_total * 2  # 压缩两次
            self.db.state["snapshot_create_current"] = 0
            if os.path.exists(self.classisland_path):
                os.makedirs(self.snapshot_path, exist_ok=True)
                if not self._zip_dir(
                    self.classisland_path, os.path.join(self.snapshot_path, zip_name)
                ):
                    return False
                os.makedirs(self.recovery_snapshot_path, exist_ok=True)
                if not self._zip_dir(
                    self.classisland_path,
                    os.path.join(self.recovery_snapshot_path, zip_name),
                ):
                    return False
                return zip_name
            else:
                return False
        except Exception as e:
            self.log.error(f"压缩文件时出错，错误是：{e}")
            return False

    def remove_snapshot(self, name: str) -> bool:
        "移除指定的快照。 传入要删除的快照名称(String) 成功返回True，失败返回False"
        try:
            self.db.state["snapshot_state"] = "remove"
            os.remove(os.path.join(self.snapshot_path, name))
            os.remove(os.path.join(self.recovery_snapshot_path, name))
            return True
        except Exception as e:
            self.log.error(f"移除快照时出错，错误为：{e}")
            return False
