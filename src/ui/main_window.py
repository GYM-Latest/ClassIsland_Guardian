# src/ui/main_window.py
import os
import sys
import win32gui
import win32con

from PySide6.QtWidgets import QApplication
from RinUI import RinUIWindow

from utils.exec import ExecClass
from ui.backend import UiBackend

backend = None


def start_main_window(log, db, scheduler):
    """启动 QML 主窗口（阻塞直到窗口关闭）"""
    global backend
    exec = ExecClass(log)
    app = QApplication.instance() or QApplication(sys.argv)
    window = RinUIWindow()
    if not backend:
        backend = UiBackend(scheduler, db, log)
    window.engine.rootContext().setContextProperty("backend", backend)
    # 发行时修改：exec.get_exe_path()
    qml_path = os.path.join(os.path.dirname(__file__), "main_window.qml")
    window.load(qml_path)

    # 根据配置决定是否置顶
    if db.config.get("window_top_mode") != "none":
        try:
            hwnd = int(window.root_window.winId())
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
            )
            log.info("成功设置了窗口置顶")
        except Exception as e:
            log.warn(f"设置窗口置顶失败，错误是：{e}")

    log.info("启动主窗口")
    app.exec()
    log.info("主窗口已关闭")
