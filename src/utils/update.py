# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import shutil
import zipfile

import requests

from utils.bcd import BcdClass
from utils.exec import ExecClass
from utils.version import VERSION

OWNER = "GYM-Latest"
REPO = "ClassIsland_Guardian"
# 镜像站地址，感谢所有提供这些镜像站服务的同志！
PROXY_ADDRESS = [
    "https://gh-proxy.com/",
    "https://ghfile.geekertao.top/",
    "https://github.dpik.top/",
    "https://gh.felicity.ac.cn/",
    "https://gh.geekertao.top/",
    "https://v6.gh-proxy.org/",
    "https://ghfast.top/",
    "",
]


class UpdateClass:
    def __init__(self, log, db):
        self.db = db
        self.log = log
        self.exec = ExecClass(log)
        self.bcd = BcdClass(log)

    def check_update(self):
        """检查云端最新版本。成功返回 release 字典，失败返回 False。"""
        try:
            self.db.state["update_status"] = "checking"
            channel = self.db.config.get("update_channel")
            if channel == "pre":
                url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"
                resp = requests.get(url)
                if resp.status_code != 200:
                    self.log.warn(f"检查更新失败，返回值是：{resp.status_code}")
                    self.db.state["update_status"] = "error"
                    return False
                data = resp.json()
                if not data:
                    self.log.warn("检查更新失败，Release 列表为空")
                    self.db.state["update_status"] = "error"
                    return False
                release = data[0]
            elif channel == "stable":
                url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
                resp = requests.get(url)
                if resp.status_code != 200:
                    self.log.warn(f"检查更新失败，返回值是：{resp.status_code}")
                    self.db.state["update_status"] = "error"
                    return False
                release = resp.json()
            else:
                self.log.warn(f"检查更新失败，错误是：更新通道 {channel} 无效。")
                self.db.state["update_status"] = "error"
                return False

            tag_name = release.get("tag_name")
            if not tag_name:
                self.db.state["update_status"] = "error"
                return False
            if self.is_newer(tag_name):
                self.db.state["update_status"] = "available"
            else:
                self.db.state["update_status"] = "latest"

            self.log.info(f"检查了更新，最新版本是：{tag_name}")
            self.db.state["latest_release"] = release

            return release

        except Exception as e:
            self.db.state["update_status"] = "error"
            self.log.warn(f"检查更新时出错，错误是：{e}")
            return False

    def update(self, release):
        "更新至指定 Release 对应的版本。传入 Release 。 成功返回 True ，失败返回 False。"
        temp_zip_path = os.path.join(self.exec.get_exe_path(), ".update.zip")

        assets = release.get("assets", [])
        if not assets:
            self.db.state["update_status"] = "error"
            self.log.warn("Release 中没有可下载的附件")
            return False

        asset = assets[0]
        url = asset["browser_download_url"]
        total = asset["size"]

        self.db.state["update_downloaded"] = 0
        self.db.state["update_total"] = total
        self.db.state["update_status"] = "downloading"

        for proxy in PROXY_ADDRESS:
            try:
                if os.path.exists(temp_zip_path):
                    os.remove(temp_zip_path)
                with requests.get(f"{proxy}{url}", stream=True, timeout=(10, 30)) as r:
                    r.raise_for_status()
                    downloaded = 0
                    with open(temp_zip_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if not chunk:
                                continue
                            f.write(chunk)
                            downloaded += len(chunk)
                            self.db.state["update_downloaded"] = downloaded
                self.db.state["update_status"] = "downloadsuccess"
                self.log.info(f"下载完成：{temp_zip_path}")
                break

            except Exception as e:
                self.log.error(f"从 {proxy} 下载时失败：{e}，回退至下一个镜像站")

        if self.db.state["update_status"] != "downloadsuccess":
            self.log.info("全部源下载失败。")
            self.db.state["update_status"] = "error"
            return False

        # 解压到GuardianRecovery
        self.db.state["update_status"] = "unziping"
        system_drive = os.environ.get("SystemDrive", "C:") + "\\"
        guardianrecovery_path = os.path.join(system_drive, "GuardianRecovery")
        update_path = os.path.join(guardianrecovery_path, "update")
        try:
            os.makedirs(update_path, exist_ok=True)
            with zipfile.ZipFile(temp_zip_path, "r") as zf:
                zf.extractall(update_path)
        except Exception as e:
            self.db.state["update_status"] = "error"
            self.log.error(f"解压失败: {e}")
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
            if os.path.exists(update_path):
                shutil.rmtree(update_path)
            return False

        # 创建标识符
        flag_file_path = os.path.join(guardianrecovery_path, ".update")
        with open(flag_file_path, "w") as f:
            f.write("")

        os.remove(temp_zip_path)

        # 修改启动菜单，下次启动时更新
        if not self.bcd.set_recovery_bcd_start():
            self.db.state["update_status"] = "error"
            return False

        self.db.state["update_status"] = "waitreboot"
        self.log.info(f"更新准备完成，重启后将更新至 {release.get('tag_name')}")
        return True

    @staticmethod
    def is_newer(version):
        """判断传入的版本号是否比当前版本更新。是返回 True，否返回 False。"""

        def _parse(v):
            return tuple(int(x) for x in v.lstrip("v").split("."))

        try:
            return _parse(version) > _parse(VERSION)
        except (ValueError, AttributeError):
            return False
