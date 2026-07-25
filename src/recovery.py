import os
import shutil
import string
import sys
import subprocess
import time

from utils.log import Log
from utils.version import VERSION, CODENAME

def clear():
    subprocess.run('cls', shell=True)

def find_guardianrecovery_path():
    """返回 GuardianRecovery 目录的路径(String)。如果未找到，返回False。"""
    for drive in string.ascii_uppercase:
        root = f"{drive}:\\"
        backup_path = os.path.join(root, "GuardianRecovery")
        if os.path.isdir(backup_path):
            return backup_path
    return False

def fix_guardian():
    """在预启动修复环境中修复Guardian。"""
    print(f'正在进行系统修复。修复完成后会自动进入系统，请安心等待 ~\n')
    try:
        # 备份日志文件
        try:
            try:
                os.remove(os.path.join(guardianrecovery_path, 'guardian.log'))
            except:
                pass
            shutil.copy2(os.path.join(guardian_path, 'data', 'guardian.log'), os.path.join(guardianrecovery_path, 'guardian.log'))
            Log.info(f'备份日志文件成功 ~')
        except Exception as e:
            Log.warn(f'备份日志文件失败，错误为：{e}')

        # 修复程序文件
        try:
            shutil.rmtree(guardian_path)
            Log.info('清除旧程序文件成功 ~')
        except:
            pass
        def copy_and_log(src, dst):
            Log.info(f'正在修复：{dst}')
            shutil.copy2(src, dst)
        shutil.copytree(
            os.path.join(guardianrecovery_path, 'Guardian'), 
            guardian_path,
            copy_function=copy_and_log
        )
        Log.info(f'修复文件成功 ~')

        # 恢复日志文件
        try:
            shutil.copy2(os.path.join(guardianrecovery_path, 'guardian.log'), os.path.join(guardian_path, 'data', 'guardian.log'))
            os.remove(os.path.join(guardianrecovery_path, 'guardian.log'))
            Log.info(f'恢复日志文件成功 ~')
        except Exception as e:
            Log.warn(f'恢复日志文件失败，错误为：{e}')

        # 为check.exe添加开机自启项
        startup_dir = os.path.join(guardianrecovery_device, "ProgramData", "Microsoft", "Windows", "Start Menu", "Programs", "StartUp")
        os.makedirs(startup_dir, exist_ok=True)
        with open(os.path.join(startup_dir, "Guardian_Check.bat"), "w") as f:
            f.write("""@echo off
        start /b "" "%ProgramFiles%\\Guardian\\check.exe"
        """)
        Log.info('创建 check.exe 开机自启项成功 ~')

    except Exception as e:
        Log.error(f'修复失败，错误为：{e}')

def main():
    global guardian_path
    global guardianrecovery_path
    global guardianrecovery_device

    # 获取 GuardianRecovery 路径
    guardianrecovery_path = find_guardianrecovery_path()
    Log.logfile = os.path.join(guardianrecovery_path,'recovery.log')
    clear()
    Log.info('正在初始化预启动修复恢复环境...')
    if(not guardianrecovery_path):
        Log.error('未找到可用的恢复路径。程序将会退出。')
        sys.exit(0)
    Log.info(f'寻找到了可用的恢复目录：{guardianrecovery_path}')
    guardianrecovery_device, _ = os.path.splitdrive(guardianrecovery_path)
    guardian_path = os.path.join(guardianrecovery_device, "Program Files", "Guardian")
    Log.info('初始化成功 ~')

    # 打印欢迎画面
    time.sleep(2)
    clear()
    print(r'''
   ___ _            ___    _              _    ___                  _ _             ___                             
  / __| |__ _ _____|_ _|__| |__ _ _ _  __| |  / __|_  _ __ _ _ _ __| (_)__ _ _ _   | _ \___ __ _____ _____ _ _ _  _ 
 | (__| / _` (_-<_-<| |(_-< / _` | ' \/ _` | | (_ | || / _` | '_/ _` | / _` | ' \  |   / -_) _/ _ \ V / -_) '_| || |
  \___|_\__,_/__/__/___/__/_\__,_|_||_\__,_|  \___|\_,_\__,_|_| \__,_|_\__,_|_||_| |_|_\___\__\___/\_/\___|_|  \_, |
                                                                                                               |__/ 
''')
    print(f'''
ClassIsland Guardian Recovery
版本：{VERSION} | ({CODENAME})
''')

    # 依据状态标志符确定操作类型
    time.sleep(5)
    if(os.path.exists(os.path.join(guardianrecovery_path, '.rollback'))):
        # 回退逻辑-还没写
        pass
    elif(os.path.exists(os.path.join(guardianrecovery_path, '.update'))):
        # 更新逻辑-还没写
        pass
    else:
        fix_guardian()



if __name__ == "__main__":
    main()