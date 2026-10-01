# src/ui/main_window.py
import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from RinUI import RinUIWindow
from ui.backend import UiBackend

backend = None


def start_main_window(log, db, scheduler):
    """启动 QML 主窗口（阻塞直到窗口关闭）"""
    global backend
    app = QApplication.instance() or QApplication(sys.argv)

    window = RinUIWindow()

    if not backend:
        backend = UiBackend(scheduler, db, log)

    window.engine.rootContext().setContextProperty("backend", backend)

    qml_path = os.path.join(os.path.dirname(__file__), "main_window.qml")
    window.load(qml_path)

    log.info("启动主窗口")
    app.exec()
    log.info("主窗口已关闭")
