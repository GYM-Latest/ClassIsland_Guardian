import win32con
import win32gui
import win32service
from typing import Literal
from PySide6.QtWidgets import QWidget
from pywintypes import HANDLEType as PyHANDLE

class WindowClass:
    def __init__(self, log) -> None:
        self.log = log

    def set_window_topmost(self, window: QWidget) -> bool:
        """设置指定窗口置顶。"""
        try:
            hwnd = int(window.root_window.winId())
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                0,
                0,
                0,
                0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
            )
            self.log.info("成功设置了窗口置顶")
            return True
        except Exception as e:
            self.log.warn(f"设置窗口置顶失败，错误是：{e}")
            return False

    def get_new_desktop(self, name: str) -> PyHANDLE | Literal[False]:
        """创建一个新的桌面并返回其句柄。"""
        try:
            h_desk = win32service.CreateDesktop(
                name,
                0,
                win32con.GENERIC_ALL,
                None
            )
            
            self.log.info(f"成功创建新桌面: {name}")
            return h_desk
            
        except Exception as e:
            self.log.error(f"创建桌面失败 (WinError: {e.winerror})，错误信息: {e.strerror}")
            return False

    def get_recent_desktop(self) -> PyHANDLE | Literal[False]:
        """获取当前的桌面句柄。"""
        try:
            h_desk = win32service.OpenInputDesktop(
                0,
                False,
                win32con.MAXIMUM_ALLOWED
            )
            self.log.info("成功获取当前线程的桌面句柄")
            return h_desk
        except Exception as e:
            self.log.error(f"获取当前线程桌面失败，错误是：{e}")
            return False

    def bind_desktop_to_thread(self, h_desk: PyHANDLE) -> bool:
        """将指定桌面绑定到当前线程。"""
        try:
            h_desk.SetThreadDesktop()
            self.log.info("成功将桌面绑定到当前线程")
            return True
        except Exception as e:
            self.log.error(f"绑定桌面到线程失败，错误是：{e}")
            return False

    def goto_desktop(self, h_desk: PyHANDLE) -> bool:
        """切换到指定桌面。"""
        try:
            h_desk.SwitchDesktop()
            self.log.info("成功切换到指定桌面")
            return True
        except Exception as e:
            self.log.error(f"切换桌面失败，错误是：{e}")
            return False

    def close_desktop(self, h_desk: PyHANDLE) -> bool:
        """关闭指定桌面。"""
        try:
            h_desk.CloseDesktop()
            self.log.info("成功关闭指定桌面")
            return True
        except Exception as e:
            self.log.error(f"关闭桌面失败，错误是：{e}")
            return False
