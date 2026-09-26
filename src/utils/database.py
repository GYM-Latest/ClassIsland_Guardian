# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import sqlite3
import time
from utils.version import CODENAME, VERSION


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

    # 读取数据库，成功返回True，失败返回False
    def read_database(self, log):
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT classisland_path, classisland_process_name, classisland_launcher_name FROM paths WHERE id=1"
                )
                row = cursor.fetchone()
                if row:
                    self.path["classisland_path"] = row[0]
                    self.path["classisland_process_name"] = (
                        row[1] or "ClassIsland.Desktop.exe"
                    )
                    self.path["classisland_launcher_name"] = row[2] or "ClassIsland.exe"

                cursor.execute("SELECT password, protect_state FROM config WHERE id=1")
                row = cursor.fetchone()
                if row:
                    self.config["password"] = row[0]
                    self.config["protect_state"] = row[1]

                cursor.execute(
                    "SELECT version, create_time, run_hours, device_id FROM meta WHERE id=1"
                )
                row = cursor.fetchone()
                if row:
                    self.meta["version"] = row[0]
                    self.meta["create_time"] = row[1]
                    self.meta["run_hours"] = float(row[2] or 0)
                    self.meta["device_id"] = row[3]

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
                    CREATE TABLE IF NOT EXISTS paths(
                        id INTEGER PRIMARY KEY,
                        classisland_path TEXT,
                        classisland_process_name TEXT DEFAULT 'ClassIsland.Desktop.exe',
                        classisland_launcher_name TEXT DEFAULT 'ClassIsland.exe'      
                                );
                    CREATE TABLE IF NOT EXISTS config(
                        id INTEGER PRIMARY KEY,
                        password TEXT,
                        protect_state TEXT DEFAULT 'running'
                                );
                    CREATE TABLE IF NOT EXISTS meta(
                        id INTEGER PRIMARY KEY,
                        version TEXT,
                        create_time TEXT,
                        run_hours TEXT,
                        device_id TEXT
                                );
                            """)
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO paths (id, classisland_path, classisland_process_name, classisland_launcher_name)
                        VALUES (1, ?, ?, ?)
                """,
                    (
                        self.path.get("classisland_path", r"D:\ClassIsland"),
                        self.path.get(
                            "classisland_process_name", "ClassIsland.Desktop.exe"
                        ),
                        self.path.get("classisland_launcher_name", "ClassIsland.exe"),
                    ),
                )
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO config (id, password, protect_state)
                        VALUES (1, ?, ?)
                """,
                    (
                        self.config.get("password", ""),
                        self.config.get("protect_state", "running"),
                    ),
                )
                cursor.execute(
                    """
                        INSERT OR REPLACE INTO meta (id, version, create_time, run_hours, device_id)
                            VALUES (1, ?, ?, ?, ?)
                    """,
                    (
                        VERSION,
                        time.asctime(time.localtime()),
                        "0",
                        "",
                    ),
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

                # 不保存 classisland_process_name 防止逃逸启动脏名称污染配置
                cursor.execute(
                    """
                        UPDATE paths SET classisland_path=?, classisland_launcher_name=? WHERE id = 1
                    """,
                    (
                        self.path.get("classisland_path", r"D:\ClassIsland"),
                        self.path.get("classisland_launcher_name", "ClassIsland.exe"),
                    ),
                )
                cursor.execute(
                    """
                        UPDATE config SET password = ?, protect_state = ? WHERE id = 1
                    """,
                    (
                        self.config.get("password", ""),
                        self.config.get("protect_state", "running"),
                    ),
                )
                cursor.execute(
                    """
                            UPDATE meta SET version = ?, run_hours = ?, device_id = ? WHERE id = 1
                        """,
                    (
                        self.meta.get("version"),
                        self.meta.get("run_hours"),
                        self.meta.get("device_id"),
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            log.error(f"保存数据库失败，错误是：{e}")
            return False
