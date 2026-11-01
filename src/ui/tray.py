# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
from typing import Any

from lightpytray import LightPyTray

from utils.database import Database
from utils.log import LogClass

_tray_instance: LightPyTray | None = None


def start_tray(log: LogClass, db: Database, scheduler: Any) -> LightPyTray:
    global _tray_instance

    # 打包时得改
    ROOT_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    icon_path = os.path.join(ROOT_DIR, "icon", "icon.ico")

    def on_left_click() -> None:
        log.info("托盘图标被左键单击！")
        from core.tasks import main_window

        scheduler.add_job(
            main_window,
            "date",
            id="main_window",
            executor="main_window",
            max_instances=1,
        )

    _tray_instance = LightPyTray(
        icon_path=icon_path,
        tooltip="ClassIsland Guardian",
        menu_items=None,
        on_left_click=on_left_click,
        quit_button=(None, None),
    )

    _tray_instance._run()

    return _tray_instance
