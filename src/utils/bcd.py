import os
import re
import shutil
import subprocess

from utils.log import Log


class Bcd:
    @staticmethod
    def _find_recovery_guid():
        """查找 ClassIsland Guardian Recovery BCD启动项对应的 GUID。 成功返回GUID(String)，失败返回False"""
        try:
            result = subprocess.run(
                ["bcdedit", "/enum"], check=True, capture_output=True, text=True
            )
            current_guid = None
            for line in result.stdout.splitlines():
                id_match = re.match(
                    r"(?:identifier|标识符)\s+(\{[^\}]+\})", line.strip()
                )
                if id_match:
                    current_guid = id_match.group(1)
                if "ClassIsland Guardian Recovery" in line and current_guid:
                    return current_guid
            Log.error("未能找到启动项GUID。")
            return False
        except Exception as e:
            Log.error(f"未能找到启动项GUID，错误是：{e}")
            return False

    @staticmethod
    def _find_windows_guid():
        """查找 Windows BCD启动项对应的 GUID。 成功返回GUID(String)，失败返回False"""
        try:
            result = subprocess.run(
                ["bcdedit", "/enum"], check=True, capture_output=True, text=True
            )
            current_guid = None
            for line in result.stdout.splitlines():
                stripped = line.strip()
                id_match = re.match(r"(?:identifier|标识符)\s+(\{[^\}]+\})", stripped)
                if id_match:
                    current_guid = id_match.group(1)
                if (
                    stripped.startswith(("description", "描述"))
                    and "Windows" in stripped
                    and "Boot Manager" not in stripped
                    and "Recovery" not in stripped
                    and "To Go" not in stripped
                    and current_guid
                ):
                    return current_guid
            Log.error("未能找到 Windows 启动项 GUID。")
            return False
        except Exception as e:
            Log.error(f"未能找到 Windows 启动项 GUID，错误是：{e}")
            return False

    @staticmethod
    def create_recovery_bcd():
        """为 GuardianRecovery\\recovery.wim 创建 BCD 启动项。 成功返回对应启动项的GUID(String)，失败返回 False"""
        try:
            if Bcd._find_recovery_guid():
                Log.error("创建 BCD启动项 失败，错误是：已经有同名启动项")
                return False
            system_device = os.environ.get("SystemDrive", "C:")
            # 复制现有启动项
            result = subprocess.run(
                [
                    "bcdedit",
                    "/copy",
                    "{current}",
                    "/d",
                    "ClassIsland Guardian Recovery",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            recovery_guid = re.search(r"\{[^\}]+\}", result.stdout).group()
            # 设置设备路径
            subprocess.run(
                [
                    "bcdedit",
                    "/set",
                    recovery_guid,
                    "device",
                    f"ramdisk=[{system_device}]\\GuardianRecovery\\recovery.wim,{{ramdiskoptions}}",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "bcdedit",
                    "/set",
                    recovery_guid,
                    "osdevice",
                    f"ramdisk=[{system_device}]\\GuardianRecovery\\recovery.wim,{{ramdiskoptions}}",
                ],
                check=True,
            )
            # 添加启动参数
            subprocess.run(
                ["bcdedit", "/set", recovery_guid, "winpe", "yes"], check=True
            )
            subprocess.run(
                ["bcdedit", "/set", recovery_guid, "systemroot", "\\Windows"],
                check=True,
            )
            subprocess.run(
                ["bcdedit", "/set", recovery_guid, "detecthal", "yes"], check=True
            )
            # 确保 {ramdiskoptions} 存在且配置了 SDI 路径
            check = subprocess.run(
                ["bcdedit", "/enum", "{ramdiskoptions}"],
                capture_output=True,
                text=True,
                check=False,  # 非零返回是预期（对象不存在），stdout/stderr 已被解析使用
            )
            out = (check.stdout or "") + (check.stderr or "")
            if "ramdisksdidevice" not in out or "ramdisksdipath" not in out:
                exists = re.search(r"标识符\s+(\{[^\}]+\})", out) is not None
                if not exists:
                    subprocess.run(
                        [
                            "bcdedit",
                            "/create",
                            "{ramdiskoptions}",
                            "/d",
                            "Ramdisk options",
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    Log.info("已创建 {ramdiskoptions} ~")
                subprocess.run(
                    [
                        "bcdedit",
                        "/set",
                        "{ramdiskoptions}",
                        "ramdisksdidevice",
                        f"partition={system_device}",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                subprocess.run(
                    [
                        "bcdedit",
                        "/set",
                        "{ramdiskoptions}",
                        "ramdisksdipath",
                        "\\GuardianRecovery\\boot.sdi",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                # 复制 boot.sdi 文件
                boot_sdi_source_path = (
                    f"{system_device}\\Windows\\Boot\\DVD\\PCAT\\boot.sdi"
                )
                if not os.path.exists(boot_sdi_source_path):
                    boot_sdi_source_path = (
                        f"{system_device}\\Windows\\Boot\\PCAT\\boot.sdi"
                    )
                if not os.path.exists(boot_sdi_source_path):
                    Log.error(
                        "未找到系统内置 boot.sdi 文件，无法配置 {ramdiskoptions} ~"
                    )
                    return False
                boot_sdi_target_path = f"{system_device}\\GuardianRecovery\\boot.sdi"
                os.makedirs(f"{system_device}\\GuardianRecovery", exist_ok=True)
                shutil.copy2(boot_sdi_source_path, boot_sdi_target_path)
                Log.info("已复制 boot.sdi 文件 ~")
                Log.info("已配置 {ramdiskoptions} SDI 路径 ~")
            # 添加到启动菜单
            subprocess.run(
                ["bcdedit", "/displayorder", recovery_guid, "-addlast"], check=True
            )
            # 隐藏启动菜单
            subprocess.run(["bcdedit", "/timeout", "0"], check=True)
            return recovery_guid
        except Exception as e:
            Log.error(f"创建 BCD启动项 失败，错误是：{e}")
            return False

    @staticmethod
    def set_recovery_bcd_startonce():
        """设置下次启动从 Recovery 环境启动。 成功返回 True ，失败返回 False"""
        try:
            recovery_guid = Bcd._find_recovery_guid()
            if not recovery_guid:
                return False
            subprocess.run(["bcdedit", "/bootsequence", recovery_guid], check=True)
            return True
        except Exception as e:
            Log.error(f"设置单次启动项时失败，错误是：{e}")
            return False

    @staticmethod
    def set_recovery_bcd_start():
        """设置默认启动项为 Recovery 环境。 成功返回 True ，失败返回 False"""
        try:
            recovery_guid = Bcd._find_recovery_guid()
            if not recovery_guid:
                return False
            subprocess.run(["bcdedit", "/default", recovery_guid], check=True)
            return True
        except Exception as e:
            Log.error(f"设置默认启动项时失败，错误是：{e}")
            return False

    @staticmethod
    def set_windows_bcd_startonce():
        """设置下次启动从 Windows 环境启动。 成功返回 True ，失败返回 False"""
        try:
            windows_guid = Bcd._find_windows_guid()
            if not windows_guid:
                return False
            subprocess.run(["bcdedit", "/bootsequence", windows_guid], check=True)
            return True
        except Exception as e:
            Log.error(f"设置单次启动项时失败，错误是：{e}")
            return False

    @staticmethod
    def set_windows_bcd_start():
        """设置默认启动项为 Windows 环境。 成功返回 True ，失败返回 False"""
        try:
            windows_guid = Bcd._find_windows_guid()
            if not windows_guid:
                return False
            subprocess.run(["bcdedit", "/default", windows_guid], check=True)
            return True
        except Exception as e:
            Log.error(f"设置默认启动项时失败，错误是：{e}")
            return False

    @staticmethod
    def remove_recovery_bcd():
        """为 GuardianRecovery\recovery.wim 移除 BCD 启动项。 成功返回 True ，失败返回 False"""
        try:
            recovery_guid = Bcd._find_recovery_guid()
            if not recovery_guid:
                Log.error("移除BCD启动项时出错，错误是：未能找到启动项GUID")
                return False
            subprocess.run(
                ["bcdedit", "/delete", recovery_guid],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except Exception as e:
            Log.error(f"移除BCD启动项时出错，错误是：{e}")
            return False
