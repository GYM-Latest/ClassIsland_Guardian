# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import ctypes
from typing import Literal

import win32api
import win32con
import win32security
import win32ts
from pywintypes import HANDLEType as PyHANDLE

from .log import LogClass


class TokenClass:
    def __init__(self, log: LogClass) -> None:
        self.log = log

    # 获取当前活动会话的纯净用户令牌
    def get_new_token(self) -> PyHANDLE | Literal[False]:
        "获取当前活动会话的纯净用户令牌。 成功返回令牌(PyHANDLE)，失败返回False(bool)。"
        try:
            session_id = win32ts.WTSGetActiveConsoleSessionId()
            if session_id == 0xFFFFFFFF:
                self.log.warn("没有活动控制台会话，无法获取用户令牌。")
                return False
            impersonation_token = win32ts.WTSQueryUserToken(session_id)
            return impersonation_token
        except Exception as e:
            self.log.error(f"获取用户令牌时失败，错误是：{e}")
            return False

    # 复制指定令牌
    def get_copyed_token(
        self, token: PyHANDLE | Literal[False]
    ) -> PyHANDLE | Literal[False]:
        "复制指定令牌，返回一个新的 Primary Token。 成功返回令牌(PyHANDLE)，失败返回False(bool)。"
        if not token:
            self.log.warn("未提供待复制的令牌。")
            return False
        try:
            new_token = win32security.DuplicateTokenEx(
                ExistingToken=token,
                ImpersonationLevel=win32security.SecurityImpersonation,
                DesiredAccess=win32security.TOKEN_ALL_ACCESS,
                TokenType=win32security.TokenPrimary,
            )
            return new_token
        except Exception as e:
            self.log.error(f"复制令牌失败，错误是：{e}")
            return False

    # 为指定令牌设置 UIAccess 标志
    def add_uiaccess_to_token(self, token: PyHANDLE | Literal[False]) -> bool:
        """为指定令牌设置 UIAccess 标志。成功返回 True，失败返回 False。"""
        # 启用 SeDebugPrivilege 权限
        hproc = win32api.GetCurrentProcess()
        proc_handle = win32security.OpenProcessToken(
            hproc, win32con.TOKEN_ADJUST_PRIVILEGES | win32con.TOKEN_QUERY
        )
        win32security.AdjustTokenPrivileges(
            proc_handle,
            False,
            [
                (
                    win32security.LookupPrivilegeValue(None, "SeDebugPrivilege"),
                    win32con.SE_PRIVILEGE_ENABLED,
                )
            ],
        )
        self.log.info("已启用 SeDebugPrivilege 权限。")
        if not token:
            self.log.warn("令牌为空，无法设置 UIAccess。")
            return False
        try:
            ui_access_value = ctypes.c_int(1)
            result = ctypes.windll.advapi32.SetTokenInformation(
                ctypes.c_void_p(int(token)),
                26,  # TokenUIAccess
                ctypes.byref(ui_access_value),
                ctypes.sizeof(ui_access_value),
            )
            if not result:
                raise ctypes.WinError(ctypes.get_last_error())
            self.log.info("已为令牌设置 UIAccess 标志。")
            return True
        except Exception as e:
            self.log.error(f"设置 UIAccess 失败，错误是：{e}")
            return False

    # 获取当前进程的访问令牌（Primary Token）
    def get_recent_token(self) -> PyHANDLE | Literal[False]:
        "获取当前进程的访问令牌（Primary Token）。成功返回令牌(PyHANDLE)，失败返回False(bool)。"
        try:
            process_handle = win32api.GetCurrentProcess()
            token = win32security.OpenProcessToken(
                process_handle,
                win32security.TOKEN_ALL_ACCESS,
            )
            return token
        except Exception as e:
            self.log.error(f"获取当前进程令牌失败，错误是：{e}")
            return False

    def get_reduced_token(self, token: PyHANDLE | Literal[False]) -> bool:
        "禁用令牌中最危险的特权。成功返回 True，失败返回 False。"
        DANGEROUS_PRIVILEGES = [
            "SeTcbPrivilege",
            "SeDebugPrivilege",
            "SeImpersonatePrivilege",
            "SeAssignPrimaryTokenPrivilege",
            "SeCreateTokenPrivilege",
            "SeBackupPrivilege",
            "SeRestorePrivilege",
            "SeTakeOwnershipPrivilege",
            "SeLoadDriverPrivilege",
        ]
        if not token:
            return False
        try:
            to_disable = []
            for name in DANGEROUS_PRIVILEGES:
                try:
                    luid = win32security.LookupPrivilegeValue(None, name)
                    to_disable.append((luid, 0))
                except Exception:
                    continue

            if to_disable:
                win32security.AdjustTokenPrivileges(token, False, to_disable)
                self.log.info(f"已禁用 {len(to_disable)} 个危险特权。")
            return True
        except Exception as e:
            self.log.error(f"禁用危险特权失败：{e}")
            return False
