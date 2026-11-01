# src/ui/main_window.py
import gc
import os
import sys
from typing import Any

from ui.backend import UiBackend
from utils.database import Database
from utils.exec import ExecClass
from utils.log import LogClass
from utils.window import WindowClass

backend: UiBackend | None = None

secure_desktop_handle = None

def start_main_window(log: LogClass, db: Database, scheduler: Any) -> None:
    """启动 QML 主窗口（阻塞直到窗口关闭）"""
    global secure_desktop_handle
    exec = ExecClass(log)
    window_manager = WindowClass(log)
    recent_desktop_handle = None

    # 根据配置切换安全桌面
    if db.config.get("window_top_mode") == "secure_desktop" or secure_desktop_handle is not None:
        try:
            if secure_desktop_handle is None:
                secure_desktop_handle = window_manager.get_new_desktop("ClassIslandGuardianSecureDesktop")
                if secure_desktop_handle is False:
                    raise RuntimeError("创建安全桌面失败。")
                if not window_manager.bind_desktop_to_thread(secure_desktop_handle):
                    raise RuntimeError("绑定安全桌面失败。")
            recent_desktop_handle = window_manager.get_recent_desktop()
            if recent_desktop_handle is False:
                raise RuntimeError("获取当前线程桌面失败。")
            if not window_manager.goto_desktop(secure_desktop_handle):
                window_manager.goto_desktop(recent_desktop_handle)
                raise RuntimeError("切换到安全桌面失败。")
        except RuntimeError as e:
            try:
                if secure_desktop_handle is not None:
                    secure_desktop_handle.CloseDesktop()
            except:
                pass
                    
    try:
        from PySide6.QtCore import QCoreApplication, QEvent
        from PySide6.QtWidgets import QApplication
        from RinUI import RinUIWindow
        
        app = QApplication.instance() or QApplication(sys.argv)
        window = RinUIWindow(shared_engine=False)
        backend = UiBackend(scheduler, db, log)
        window.engine.rootContext().setContextProperty("backend", backend)
        qml_path = os.path.join(exec.get_exe_path(), "ui", "main_window.qml")
        window.load(qml_path)

        # 根据配置决定是否置顶
        if db.config.get("window_top_mode") != "none":
            window_manager.set_window_topmost(window)

        log.info("启动主窗口")
        app.exec()
        log.info("主窗口已关闭，开始垃圾清理")
    except Exception as e:
        log.error(f"启动主窗口失败，错误是：{e}")
    finally:
        # 尝试切回原来的桌面
        if recent_desktop_handle is not None:
            window_manager.goto_desktop(recent_desktop_handle)
        try:
            engine = window.engine
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            backend = None
            del window
            gc.collect()
        except Exception as e:
            log.warn(f"清理 QML 引擎失败：{e}")
        log.info("清理完毕")
