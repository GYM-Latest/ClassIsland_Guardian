# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest
# 基于 grintor/win_graceful_shutdown (GPL-3.0) 修改
# https://github.com/grintor/win_graceful_shutdown

import atexit
import ctypes
import os
import signal
import sys
import threading
import time

import win32api
import win32con
import win32gui

from utils.exec import Exec

# you can override these variables in the main script if you want the windows shutdown screen to say something else
APPNAME = os.path.basename(__file__)
SHUTDOWN_MESSAGE = f"{APPNAME} is shutting down..."

# you can override these variables in the main script if you want a different return code than 0xc000013a for any shutdown request
RETURN_CODE_CTRL_C_EVENT = -1073741510
RETURN_CODE_CTRL_BREAK_EVENT = -1073741510
RETURN_CTRL_CLOSE_EVENT = -1073741510
RETURN_CODE_WM_CLOSE = -1073741510
RETURN_CODE_WM_ENDSESSION = -1073741510

# 由主脚本在创建调度器后注入：utils.win_graceful_shutdown.scheduler = scheduler
scheduler = None


# you can manually send test signals from another python process like this:
# import win32con, win32gui
# win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

EXIT_HANDLERS_RUNNING = False
EXIT_REASON = None

ucrtbase = ctypes.CDLL("ucrtbase")
c_raise = ucrtbase["raise"]


def window_thread():
    hinst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "WindowClass"

    def wndproc(hwnd, message, event_id, session_id):
        global EXIT_REASON
        if message == win32con.WM_CLOSE:
            print("进程结束请求已被拦截。")
            return 0

        if message == win32con.WM_DESTROY:
            print("进程结束请求已被拦截。")
            return 0

        if (
            message == win32con.WM_ENDSESSION
        ):  # WM_ENDSESSION gets called by windows once WM_QUERYENDSESSION returns True
            EXIT_REASON = win32con.WM_ENDSESSION
            Exec.unmake_process_critical()
            if scheduler is not None:
                scheduler.shutdown(True)
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


def first_exit():
    # if is possible for two instances of the exit handlers to run. For example,
    # if someone hits ctrl-c and then closes the window (SIGINT then RETURN_CTRL_CLOSE_EVENT) then atexit will be called twice.
    # we are using the EXIT_HANDLERS_RUNNING variable as a kind of lock to prevent that from happening
    global EXIT_HANDLERS_RUNNING
    EXIT_HANDLERS_RUNNING = True


# if we don't put a signal handler in to handle SIGINT and SIGBREAK,
# they will cause a keyboard interrupt somewhere random before atexit handlers can run (or even inside them)
def signal_handler(sig, frame):
    global EXIT_REASON
    if not EXIT_HANDLERS_RUNNING:
        RETURN_CODE = 0
        atexit.register(
            first_exit
        )  # will cause EXIT_HANDLERS_RUNNING to be true as soon as sys.exit() is called.

        if sig == signal.SIGINT:
            EXIT_REASON = win32con.CTRL_C_EVENT
            RETURN_CODE = RETURN_CODE_CTRL_C_EVENT

        if sig == signal.SIGBREAK:
            EXIT_REASON = win32con.CTRL_BREAK_EVENT
            RETURN_CODE = RETURN_CODE_CTRL_BREAK_EVENT

        if sig == signal.SIGTERM:
            if EXIT_REASON == win32con.WM_CLOSE:
                RETURN_CODE = RETURN_CODE_WM_CLOSE

            if EXIT_REASON == win32con.WM_ENDSESSION:
                RETURN_CODE = RETURN_CODE_WM_ENDSESSION

        sys.exit(RETURN_CODE)


def ConsoleCtrlHandler(sig):
    global EXIT_REASON
    if sig == win32con.CTRL_CLOSE_EVENT:
        if not EXIT_HANDLERS_RUNNING:
            atexit.register(first_exit)
            EXIT_REASON = win32con.CTRL_CLOSE_EVENT

            # we are already past the point where the exit handlers would normally be able to run,
            # so we have to use our monkey-patched atexit module to run each exit handler manually
            # note that this cannot take longer than 5 seconds or the OS kills the process
            for registered_function in reversed(atexit.registered_functions):
                func = registered_function["func"]
                args = registered_function["args"]
                kwargs = registered_function["kwargs"]
                if args and kwargs:
                    func(*args, **kwargs)
                if args and not kwargs:
                    func(*args)
                if kwargs and not args:
                    func(*kwargs)
                if not kwargs and not args:
                    func()
            os._exit(RETURN_CTRL_CLOSE_EVENT)
        else:
            while True:  # same logic as WM_ENDSESSION, need to wait for the exit handlers to finish
                time.sleep(1)
    if sig == win32con.CTRL_C_EVENT:
        # if you put a sys.exit() here, python will print "ConsoleCtrlHandler function failed" before exiting
        pass

    if sig == win32con.CTRL_BREAK_EVENT:
        # if you put a sys.exit() here, python will print "ConsoleCtrlHandler function failed" before exiting
        pass


def init():
    patch_atexit()  # we monkey-patch atexit so that we can manually run the exit handlers later if we have to
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGBREAK, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    win32api.SetConsoleCtrlHandler(ConsoleCtrlHandler, True)
    threading.Thread(target=window_thread, daemon=True).start()


def patch_atexit():
    atexit.origional_register = atexit.register
    atexit.origional_unregister = atexit.unregister
    atexit.registered_functions = []

    def atexit_register_new(func, *args, **kwargs):
        atexit.origional_register(func, *args, **kwargs)
        atexit.registered_functions.append(
            {"args": args, "kwargs": kwargs, "func": func}
        )

    def atexit_unregister_new(func):
        atexit.origional_unregister(func)
        # remove all items from the registered_functions list in which the func is the same
        atexit.registered_functions[:] = [
            item for item in atexit.registered_functions if item["func"] != func
        ]

    atexit.register = atexit_register_new
    atexit.unregister = atexit_unregister_new


init()
