# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import shutil
import pigzpp
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
            with pigzpp.ZipFile(dst, "w", pigzpp.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(src):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, src)
                        zf.write(file_path, arcname)
            return True
        except Exception as e:
            self.log.error(f"压缩文件时出错，错误是：{e}")
            return False

    def list_snapshot(self) -> list[list[str | int]] | Literal[False]:
        "列出所有可用的快照。 成功返回列表，失败返回False"
        try:
            list = []
            with os.scandir(self.snapshot_path) as entries:
                for entry in entries:
                    if entry.is_file():
                        stat = entry.stat()
                        list.append(
                            [
                                entry.name,
                                datetime.fromtimestamp(stat.st_birthtime).strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                stat.st_size,
                            ]
                        )
            list = sorted(list, key=lambda x: x[1], reverse=True)
            return list
        except Exception as e:
            self.log.error(f"列出快照时出错，错误为：{e}")
            return False

    def restore_snapshot(self, name: str) -> bool:
        "恢复到指定的快照。 传入要恢复快照的文件名(string) 成功返回True，失败返回False"
        self.process.kill_classisland()
        if os.path.exists(os.path.join(self.snapshot_path, name)):
            try:
                try:
                    shutil.rmtree(self.classisland_path)
                except:
                    pass
                os.mkdir(self.classisland_path)
                with pigzpp.ZipFile(os.path.join(self.snapshot_path, name), "r") as zf:
                    zf.extractall(path=self.classisland_path)
                    self.log.info(f"成功恢复到指定快照：{name}")
                    return True
            except Exception as e:
                self.log.error(f"恢复时出错，错误为：{e}")
                return False
        else:
            self.log.error("恢复时出错，指定的快照文件不存在")
            return False

    def create_snapshot(self, name: str | None = None) -> str | Literal[False]:
        "创建一个快照。 可选传入一个备注信息(String)。成功返回快照名称，失败返回False。"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if name:
            zip_name = f"snapshot_{timestamp}_({name}).zip"
        else:
            zip_name = f"snapshot_{timestamp}.zip"

        try:
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
            os.remove(os.path.join(self.snapshot_path, name))
            os.remove(os.path.join(self.recovery_snapshot_path, name))
            return True
        except Exception as e:
            self.log.error(f"移除快照时出错，错误为：{e}")
            return False
