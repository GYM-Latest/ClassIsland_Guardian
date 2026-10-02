# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import sqlite3
import time

from utils.version import VERSION


# 封装数据库方法
class Database:
    def __init__(self, database_path):
        self.database_path = database_path

        # 路径表
        self.path = {}
        # 设置表
        self.config = {}
        # 运行时状态表
        self.state = {}
        # 元数据表
        self.meta = {}

    # 数据库格式转换
    def _format_database(self):
        self.path["classisland_process_name"] = (
            self.path.get("classisland_process_name") or "ClassIsland.Desktop.exe"
        )
        self.path["classisland_launcher_name"] = (
            self.path.get("classisland_launcher_name") or "ClassIsland.exe"
        )

        self.config["protect_state"] = self.config.get("protect_state") or "running"
        self.config["kill_non_install_ci"] = (
            self.config.get("kill_non_install_ci") == "true"
        )
        self.config["kill_multi_ci"] = self.config.get("kill_multi_ci") == "true"
        self.config["launch_ci_as_system"] = (
            self.config.get("launch_ci_as_system") == "true"
        )
        self.config["launch_ci_as_uiaccess"] = (
            self.config.get("launch_ci_as_uiaccess") == "true"
        )
        self.config["auto_restart_frozen_ci"] = (
            self.config.get("auto_restart_frozen_ci") != "false"
        )
        self.config["escape_launch_ci"] = self.config.get("escape_launch_ci") != "false"
        self.config["rollback_before_launch"] = (
            self.config.get("rollback_before_launch") == "true"
        )
        self.config["rollback_on_fail"] = self.config.get("rollback_on_fail") != "false"
        self.config["rollback_on_crash"] = (
            self.config.get("rollback_on_crash") != "false"
        )
        self.config["auto_cleanup_snapshot"] = (
            self.config.get("auto_cleanup_snapshot") != "false"
        )
        self.config["max_snapshot_count"] = int(
            self.config.get("max_snapshot_count") or 5
        )
        self.config["auto_install_dotnet"] = (
            self.config.get("auto_install_dotnet") == "true"
        )
        self.config["cig_professional"] = self.config.get("cig_professional") == "true"
        self.config["critical_process"] = self.config.get("critical_process") != "false"
        self.config["window_top_mode"] = (
            self.config.get("window_top_mode") or "uiaccess"
        )
        self.config["auto_download_update"] = (
            self.config.get("auto_download_update") != "false"
        )
        self.config["update_channel"] = self.config.get("update_channel") or "stable"
        self.config["tray_icon"] = self.config.get("tray_icon") != "false"
        self.config["notification"] = self.config.get("notification") != "false"
        self.config["task_error_mode"] = (
            self.config.get("task_error_mode") or "silent_disable"
        )
        self.config["service_error_mode"] = (
            self.config.get("service_error_mode") or "silent_restart"
        )

        self.meta["version"] = VERSION
        self.meta["create_time"] = self.meta.get("create_time") or time.asctime(
            time.localtime()
        )
        self.meta["run_hours"] = float(self.meta.get("run_hours") or 0)
        self.meta["device_id"] = self.meta.get("device_id") or ""

    # 读取数据库，成功返回True，失败返回False
    def read_database(self, log):
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                # 读取
                for table, target in [
                    ("paths", self.path),
                    ("config", self.config),
                    ("meta", self.meta),
                ]:
                    cursor.execute(f"SELECT key, value FROM {table}")
                    for key, value in cursor.fetchall():
                        target[key] = value

                # 修正与格式转换
                self._format_database()

                return True

        except Exception as e:
            log.error(f"读取配置失败: {e}")
            return False

    # 创建数据库，成功返回数据库路径，失败返回False
    def new_database(self, log):
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS paths (
                        key   TEXT PRIMARY KEY,
                        value TEXT
                    );
                    CREATE TABLE IF NOT EXISTS config (
                        key   TEXT PRIMARY KEY,
                        value TEXT
                    );
                    CREATE TABLE IF NOT EXISTS meta (
                        key   TEXT PRIMARY KEY,
                        value TEXT
                    );
                            """)
                for table, data in [
                    ("paths", self.path),
                    ("config", self.config),
                    ("meta", self.meta),
                ]:
                    for key, value in data.items():
                        cursor.execute(
                            f"INSERT OR REPLACE INTO {table} (key, value) VALUES (?, ?)",
                            (key, str(value)),
                        )
                conn.commit()
            return self.database_path

        except Exception as e:
            log.error(f"创建数据库时出错，错误为: {e}")
            return False

    # 保存数据库
    def save_database(self, log):
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                for table, data in [
                    ("paths", self.path),
                    ("config", self.config),
                    ("meta", self.meta),
                ]:
                    for key, value in data.items():
                        # 不保存 classisland_process_name 防止逃逸启动脏名称污染配置
                        if key == "classisland_process_name":
                            continue
                        cursor.execute(
                            f"INSERT OR REPLACE INTO {table} (key, value) VALUES (?, ?)",
                            (key, str(value)),
                        )
                conn.commit()
                return True
        except Exception as e:
            log.error(f"保存数据库失败，错误是：{e}")
            return False

    # 读取v0.4.x及以下的数据库，成功返回True，失败返回False
    def read_v0_4_x_database(self, log):
        """读取 v0.4.x 及以下的数据库，成功返回 True，失败返回 False。"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT classisland_path, classisland_process_name, "
                    "classisland_launcher_name FROM paths WHERE id=1"
                )
                row = cursor.fetchone()
                if row:
                    self.path["classisland_path"] = row[0] or ""
                    self.path["classisland_process_name"] = (
                        row[1] or "ClassIsland.Desktop.exe"
                    )
                    self.path["classisland_launcher_name"] = row[2] or "ClassIsland.exe"

                cursor.execute("SELECT password FROM config WHERE id=1")
                row = cursor.fetchone()
                if row:
                    self.config["password"] = row[0] or ""

                # 补齐字段
                self._format_database()

                return True

        except Exception as e:
            log.error(f"读取 v0.4.x 数据库失败: {e}")
            return False
