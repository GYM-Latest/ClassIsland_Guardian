# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import shutil
import zipfile

import requests

from utils.bcd import Bcd
from utils.exec import Exec
from utils.log import Log

Log = Log("update")

OWNER = "GYM-Latest"
REPO = "ClassIsland_Guardian"


class Update:
    @staticmethod
    # v0.x.x 阶段，默认传入 pre，否则无法更新
    def check_update(channel="pre"):
        "检查云端最新版本。 传入更新通道 pre/stable(string) 成功返回最新版本号，失败返回 False。"
        try:
            if channel == "pre":
                url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"
                resp = requests.get(url)

                if resp.status_code != 200:
                    Log.warn(f"检查更新失败，返回值是：{resp.status_code}")
                    return False

                data = resp.json()
                if not data:
                    Log.warn("检查更新失败，Release 列表为空")
                    return False
                tag_name = data[0].get("tag_name")

                if tag_name:
                    pass
                else:
                    return False
            elif channel == "stable":
                url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
                resp = requests.get(url)

                if resp.status_code != 200:
                    Log.warn(f"检查更新失败，返回值是：{resp.status_code}")
                    return False

                data = resp.json()
                tag_name = data.get("tag_name")

                if tag_name:
                    pass
                else:
                    return False
            else:
                Log.warn("检查更新失败，错误是：给定的更新通道无效。")
                return False
            Log.info(f"检查了更新，最新版本是：{tag_name}")
            return tag_name

        except Exception as e:
            Log.warn(f"检查更新时出错，错误是：{e}")
            return False

    @staticmethod
    def update():
        "更新至最新版本（重启后生效）。 成功返回 True ，失败返回 False。"
        try:
            latest_tag = Update.check_update()
            if not latest_tag:
                return False

            api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{latest_tag}"
            try:
                resp = requests.get(api_url)
                resp.raise_for_status()
            except Exception as e:
                Log.error(f"获取 Release 信息失败: {e}")
                return False
            release_data = resp.json()

            assets = release_data.get("assets", [])
            if not assets:
                Log.warn("Release 中未找到可下载的 asset")
                return False
            asset = assets[0]
            download_url = asset["browser_download_url"]

            temp_zip_path = os.path.join(Exec.get_exe_path(), ".update.zip")
            Log.info(f"正在下载更新: {latest_tag}")

            try:
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    with open(temp_zip_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
            except Exception as e:
                Log.error(f"下载失败: {e}")
                if os.path.exists(temp_zip_path):
                    os.remove(temp_zip_path)
                return False

            # 解压到GuardianRecovery
            system_drive = os.environ.get("SystemDrive", "C:") + "\\"
            guardianrecovery_path = os.path.join(system_drive, "GuardianRecovery")
            update_path = os.path.join(guardianrecovery_path, "update")
            try:
                os.makedirs(update_path, exist_ok=True)
                with zipfile.ZipFile(temp_zip_path, "r") as zf:
                    zf.extractall(update_path)
            except Exception as e:
                Log.error(f"解压失败: {e}")
                if os.path.exists(temp_zip_path):
                    os.remove(temp_zip_path)
                if os.path.exists(update_path):
                    shutil.rmtree(update_path)
                return False

            # 创建标识符
            flag_file_path = os.path.join(guardianrecovery_path, ".update")
            with open(flag_file_path, "w") as f:
                f.write(latest_tag)

            os.remove(temp_zip_path)

            # 修改启动菜单，下次启动时更新
            if not Bcd.set_recovery_bcd_start():
                return False

            Log.info(f"更新准备完成，重启后将更新至 {latest_tag}")
            return True

        except Exception as e:
            Log.warn(f"检查更新时出错，错误是：{e}")
            return False
