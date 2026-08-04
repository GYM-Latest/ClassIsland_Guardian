import subprocess
import re
import os

from utils.log import Log

class Bcd:
    @staticmethod
    def _find_recovery_guid():
        '''查找 ClassIsland Guardian Recovery BCD启动项对应的 GUID。 成功返回GUID(String)，失败返回False'''
        try:
            result = subprocess.run(
                ['bcdedit', '/enum'],
                check=True,
                capture_output=True,
                text=True
            )
            current_guid = None
            for line in result.stdout.splitlines():
                id_match = re.match(r'identifier\s+(\{[^\}]+\})', line.strip())
                if id_match:
                    current_guid = id_match.group(1)
                if 'ClassIsland Guardian Recovery' in line and current_guid:
                    return current_guid
            Log.error(f'未能找到启动项GUID。')
            return False
        except Exception as e:
            Log.error(f'未能找到启动项GUID，错误是：{e}')
            return False

    @staticmethod
    def _find_windows_guid():
        '''查找 Windows BCD启动项对应的 GUID。 成功返回GUID(String)，失败返回False'''
        try:
            result = subprocess.run(
                ['bcdedit', '/enum'],
                check=True,
                capture_output=True,
                text=True
            )
            current_guid = None
            for line in result.stdout.splitlines():
                stripped = line.strip()
                id_match = re.match(r'identifier\s+(\{[^\}]+\})', stripped)
                if id_match:
                    current_guid = id_match.group(1)
                if (stripped.startswith('description')
                        and 'Windows' in stripped
                        and 'Recovery' not in stripped
                        and 'To Go' not in stripped
                        and current_guid):
                    return current_guid
            Log.error('未能找到 Windows 启动项 GUID。')
            return False
        except Exception as e:
            Log.error(f'未能找到 Windows 启动项 GUID，错误是：{e}')
            return False

    @staticmethod
    def create_recovery_bcd():
        '''为 GuardianRecovery\\recovery.wim 创建 BCD 启动项。 成功返回对应启动项的GUID(String)，失败返回 False '''
        try:
            system_device = os.environ.get('SystemDrive', 'C:')
            # 复制现有启动项
            result = subprocess.run(
                ['bcdedit', '/copy', '{current}', '/d', '"ClassIsland Guardian Recovery"'],
                check = True,
                capture_output = True
            )
            recovery_guid = re.search(r'\{[^\}]+\}', result.stdout).group()
            # 设置设备路径
            subprocess.run(
                ['bcdedit', '/set', recovery_guid, 'device', 
                f'ramdisk=[{system_device}]\\GuardianRecovery\\recovery.wim,{{ramdiskoptions}}'],
                check = True
            )
            subprocess.run(
                ['bcdedit', '/set', recovery_guid, 'osdevice', 
                f'ramdisk=[{system_device}]\\GuardianRecovery\\recovery.wim,{{ramdiskoptions}}'],
                check=True
            )
            # 添加启动参数
            subprocess.run(['bcdedit', '/set', recovery_guid, 'winpe', 'yes'], check=True)
            subprocess.run(['bcdedit', '/set', recovery_guid, 'systemroot', '\\Windows'], check=True)
            subprocess.run(['bcdedit', '/set', recovery_guid, 'detecthal', 'yes'], check=True)
            # 添加到启动菜单
            subprocess.run(['bcdedit', '/displayorder', recovery_guid, '-addlast'], check=True)
            # 隐藏启动菜单
            subprocess.run(['bcdedit', '/timeout', '0'], check=True)
            return recovery_guid
        except Exception:
            return False

    @staticmethod
    def set_recovery_bcd_startonce():
        '''设置下次启动从 Recovery 环境启动。 成功返回 True ，失败返回 False'''
        try:
            recovery_guid = Bcd._find_recovery_guid()
            if(not recovery_guid):
                return False
            subprocess.run(['bcdedit', '/bootsequence', recovery_guid], check=True)
            return True
        except Exception as e:
            Log.error(f'设置单次启动项时失败，错误是：{e}')
            return False

    @staticmethod
    def set_recovery_bcd_start():
        '''设置默认启动项为 Recovery 环境。 成功返回 True ，失败返回 False'''
        try:
            recovery_guid = Bcd._find_recovery_guid()
            if(not recovery_guid):
                return False
            subprocess.run(['bcdedit', '/default', recovery_guid], check=True)
            return True
        except Exception as e:
            Log.error(f'设置默认启动项时失败，错误是：{e}')
            return False

    @staticmethod
    def set_windows_bcd_startonce():
        '''设置下次启动从 Windows 环境启动。 成功返回 True ，失败返回 False'''
        try:
            windows_guid = Bcd._find_windows_guid()
            if(not windows_guid):
                return False
            subprocess.run(['bcdedit', '/bootsequence', windows_guid], check=True)
            return True
        except Exception as e:
            Log.error(f'设置单次启动项时失败，错误是：{e}')
            return False

    @staticmethod
    def set_windows_bcd_start():
        '''设置默认启动项为 Windows 环境。 成功返回 True ，失败返回 False'''
        try:
            windows_guid = Bcd._find_windows_guid()
            if(not windows_guid):
                return False
            subprocess.run(['bcdedit', '/default', windows_guid], check=True)
            return True
        except Exception as e:
            Log.error(f'设置默认启动项时失败，错误是：{e}')
            return False