# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import ctypes
import os
import time
from typing import Any

from lightpytray import LightPyTray

from utils.database import Database
from utils.log import LogClass


class TrayClass:
    """托盘图标与通知气泡。"""

    # Shell_NotifyIcon 常量
    NIM_MODIFY = 1
    NIF_INFO = 0x10

    def __init__(self, log: LogClass, db: Database, scheduler: Any) -> None:
        self.log = log
        self.db = db
        self.scheduler = scheduler
        self.tray: LightPyTray | None = None

    def start_tray(self) -> LightPyTray:
        """创建并运行托盘图标，成功返回托盘对象（阻塞直到托盘退出）。"""
        # 打包时得改
        ROOT_DIR = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        icon_path = os.path.join(ROOT_DIR, "icon", "icon.ico")

        def on_left_click() -> None:
            self.log.info("托盘图标被左键单击！")
            from core.tasks import main_window

            self.scheduler.add_job(
                main_window,
                "date",
                id="main_window",
                executor="main_window",
                max_instances=1,
            )

        self.tray = LightPyTray(
            icon_path=icon_path,
            tooltip="ClassIsland Guardian",
            menu_items=None,
            on_left_click=on_left_click,
            quit_button=(None, None),
        )
        
        # 启动通知队列轮询
        self.scheduler.add_job(
            self.notify_notification,
            "date",
            id="notification_worker",
            max_instances=1,
        )

        self.tray._run()

        return self.tray

    @staticmethod
    def notify(db: Database, title: str, message: str) -> None:
        """把一条通知放进 state 队列。"""
        if not db.config.get("notification"):
            return

        queue = db.state.get("notification_queue") or []
        db.state["notification_queue"] = queue + [
            {"title": title, "message": message}
        ]

    def notify_notification(self) -> None:
        """取出队列中的通知并弹出托盘气泡。不断阻塞。"""
        while True:
            time.sleep(1)

            queue = self.db.state.get("notification_queue") or []
            if not queue:
                continue

            # 托盘还没就绪留着
            if self.tray is None or self.tray._nid is None:
                continue

            # 托盘已就绪，取走队列
            self.db.state["notification_queue"] = []

            shell32 = ctypes.windll.shell32
            for item in queue:
                nid = self.tray._nid
                nid.uFlags |= self.NIF_INFO
                nid.szInfo = str(item["message"])[:255]
                nid.szInfoTitle = str(item["title"])[:63]
                nid.dwInfoFlags = 0  # 不显示信息图标（否则气泡前会多一个蓝点）
                shell32.Shell_NotifyIconW(self.NIM_MODIFY, ctypes.byref(nid))
