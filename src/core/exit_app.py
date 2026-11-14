# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest
# 基于 grintor/win_graceful_shutdown (GPL-3.0) 修改
# https://github.com/grintor/win_graceful_shutdown

import ctypes
import os
from typing import Any

import win32api
import win32con
import win32gui
from apscheduler.schedulers.base import STATE_STOPPED

from utils.exec import ExecClass
from utils.log import LogClass
from utils.database import Database

log = LogClass("Service.exit_app")
exec = ExecClass(log)

# you can override these variables in the main script if you want the windows shutdown screen to say something else
APPNAME = os.path.basename(__file__)
SHUTDOWN_MESSAGE = "ClassIsland Guardian 正在退出，请稍等..."

# you can override these variables in the main script if you want a different return code than 0xc000013a for any shutdown request
RETURN_CODE_CTRL_C_EVENT = -1073741510
RETURN_CODE_CTRL_BREAK_EVENT = -1073741510
RETURN_CTRL_CLOSE_EVENT = -1073741510
RETURN_CODE_WM_CLOSE = -1073741510
RETURN_CODE_WM_ENDSESSION = -1073741510

scheduler: Any = None
db: Database | None = None

EXIT_HANDLERS_RUNNING = False
EXIT_REASON: int | None = None


def window_thread() -> None:
    hinst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "WindowClass"

    def wndproc(
        hwnd: int, message: int, event_id: int, session_id: int
    ) -> int | bool | None:
        global EXIT_REASON
        if message == win32con.WM_CLOSE:
            log.info("WM_CLOSE 结束请求已被拦截。")
            return 0

        if message == win32con.WM_DESTROY:
            log.info("收到 WM_DESTROY 通知。")
            return 0

        if (
            message == win32con.WM_ENDSESSION
        ):
            if not event_id:
                log.info("系统关机/注销已被取消，Guardian 继续运行。")
                return 0
            exec.unmake_process_critical()
            log.info("系统正在关闭，Guardian正在退出...")
            if scheduler is not None and scheduler.state != STATE_STOPPED:
                scheduler.shutdown(False)
            
            exec.remove_ifeo("guardian.exe")
            exec.remove_ifeo("launcher.exe")

            if db is not None:
                db.save_database(log)
                
            os._exit(0)

        if message == win32con.WM_QUERYENDSESSION:
            # Windows will kill a process after 5 seconds unless it calls ShutdownBlockReasonCreate
            # the SHUTDOWN_MESSAGE here will be displayed on the shutdown screen to the user along with the APPNAME
            # unless the atexit handlers finish in less than 5 seconds
            ctypes.windll.user32.ShutdownBlockReasonCreate(
                hwnd, ctypes.c_wchar_p(SHUTDOWN_MESSAGE)
            )
            return True  # must return True for WM_ENDSESSION will be called

    messageMap = {
        win32con.WM_QUERYENDSESSION: wndproc,
        win32con.WM_ENDSESSION: wndproc,
        win32con.WM_DESTROY: wndproc,
        win32con.WM_CLOSE: wndproc,
    }

    wndclass.lpfnWndProc = messageMap
    hwnd = win32gui.CreateWindowEx(  # noqa: F841
        win32con.WS_EX_LEFT,
        win32gui.RegisterClass(wndclass),
        APPNAME,
        0,
        0,
        0,
        win32con.CW_USEDEFAULT,
        win32con.CW_USEDEFAULT,
        0,
        0,
        hinst,
        None,
    )
    # print(hwnd)
    win32gui.PumpMessages()  # blocks until PostQuitMessage() is called

def init(_scheduler: Any, _db: Database | None) -> None:
    global scheduler, db
    scheduler = _scheduler
    db = _db
    window_thread()

