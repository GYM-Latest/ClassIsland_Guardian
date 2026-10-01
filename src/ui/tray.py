# src/ui/tray.py
import os

from lightpytray import LightPyTray

_tray_instance = None


def start_tray(log, db, scheduler):
    global _tray_instance

    # 打包时得改
    ROOT_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    icon_path = os.path.join(ROOT_DIR, "icon", "icon.ico")

    def on_left_click():
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
