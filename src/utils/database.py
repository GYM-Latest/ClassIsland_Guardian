# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import sqlite3

from .log import Log


# 封装数据库方法
class Database:
    def __init__(self, install_dir):
        self.install_dir = install_dir
        self.database_path = os.path.join(install_dir, "data", "guardian_config.db")

        self.path = {}
        self.config = {}

    # 读取数据库，成功返回True，失败返回False
    def read_database(self):
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

                cursor.execute("SELECT password FROM config WHERE id=1")
                row = cursor.fetchone()
                if row:
                    self.config["password"] = row[0]

                return True

        except Exception as e:
            Log.error(f"读取配置失败: {e}")
            return False

    # 创建数据库，成功返回数据库路径，失败返回False
    def new_database(self, config_data):
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
                        password TEXT
                                );
                            """)
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO paths (id, classisland_path, classisland_process_name, classisland_launcher_name)
                        VALUES (1, ?, ?, ?)
                """,
                    (
                        config_data.get("classisland_path", r"D:\ClassIsland"),
                        config_data.get(
                            "classisland_process_name", "ClassIsland.Desktop.exe"
                        ),
                        config_data.get("classisland_launcher_name", "ClassIsland.exe"),
                    ),
                )
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO config (id, password)
                        VALUES (1, ?)
                """,
                    (config_data.get("password", ""),),
                )
                conn.commit()
                return self.database_path

        except Exception as e:
            Log.error(f"创建数据库时出错，错误为: {e}")
            return False
