# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latestimport os

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
        rollback_path = os.path.join(root, "GuardianRecovery")
        if os.path.isdir(rollback_path):
            return rollback_path
    return False

def rollback_guardian_log():
    '''备份Guardian主程序日志到GuardianRecovery目录。'''
    try:
        try:
            os.remove(os.path.join(guardianrecovery_path, 'guardian.log'))
        except:
            pass
        shutil.copy2(os.path.join(guardian_path, 'data', 'guardian.log'), os.path.join(guardianrecovery_path, 'guardian.log'))
        Log.info(f'备份日志文件成功 ~')
    except Exception as e:
        Log.warn(f'备份日志文件失败，错误为：{e}')

def restore_guardian_log():
    '''从GuardianRecovery目录恢复Guardian主程序日志。'''
    try:
        shutil.copy2(os.path.join(guardianrecovery_path, 'guardian.log'), os.path.join(guardian_path, 'data', 'guardian.log'))
        os.remove(os.path.join(guardianrecovery_path, 'guardian.log'))
        Log.info(f'恢复日志文件成功 ~')
    except Exception as e:
        Log.warn(f'恢复日志文件失败，错误为：{e}')

def fix_guardian():
    """在预启动修复环境中修复Guardian。"""
    print(f'正在进行系统修复。修复完成后会自动进入系统，请安心等待 ~\n')
    try:
        # 备份日志文件
        rollback_guardian_log()

        # 修复程序文件与配置文件
        try:
            shutil.rmtree(guardian_path)
            Log.info('清除旧程序文件成功 ~')
        except:
            pass
        def copy_and_log(src, dst):
            Log.info(f'正在修复：{dst}')
            shutil.copy2(src, dst)
        shutil.copytree(
            os.path.join(guardianrecovery_path, 'stable'), 
            guardian_path,
            copy_function=copy_and_log
        )
        shutil.copytree(
                    os.path.join(guardianrecovery_path, 'data'), 
                    os.path.join(guardian_path, 'data'),
                    copy_function=copy_and_log
        )
        Log.info(f'修复文件成功 ~')

        # 恢复日志文件
        restore_guardian_log()

        # 为check.exe添加开机自启项
        try:
            startup_dir = os.path.join(guardianrecovery_device, "Programdata", "Microsoft", "Windows", "Start Menu", "Programs", "StartUp")
            os.makedirs(startup_dir, exist_ok=True)
            with open(os.path.join(startup_dir, "Guardian_Check.bat"), "w") as f:
                f.write("""@echo off
            start /b "" "%ProgramFiles%\\Guardian\\check.exe"
            """)
            Log.info('创建 check.exe 开机自启项成功 ~')
        except Exception as e:
            Log.ware(f'修复失败，错误为：{e}')

    except Exception as e:
        Log.error(f'修复失败，错误为：{e}')

def update_guardian():
    '''在预启动修复环境下升级Guardian主程序'''
    try:
        # 备份Guardian日志
        rollback_guardian_log()

        # 备份更新前的目录到 rollback
        try:
            shutil.rmtree(os.path.join(guardianrecovery_path, 'rollback'))
            Log.info('成功清除了旧 rollback 目录 ~')
        except:
            pass
        try:
            shutil.rmtree(os.path.join(guardian_path, 'data'))
            Log.info('成功清除了旧 data 目录 ~')
        except:
            pass
        def copy_and_log(src, dst):
            Log.info(f'正在备份：{dst}')
            shutil.copy2(src, dst)
        shutil.copytree(
            guardian_path,
            os.path.join(guardianrecovery_path, 'rollback'), 
            copy_function=copy_and_log
        )
        Log.info(f'备份文件成功 ~')

        # 从 update 目录更新文件
        shutil.rmtree(guardian_path)
        def copy_and_log(src, dst):
            Log.info(f'正在更新：{dst}')
            shutil.copy2(src, dst)
        shutil.copytree(
            os.path.join(guardianrecovery_path, 'update'), 
            guardian_path,
            copy_function=copy_and_log
        )
        Log.info(f'更新文件成功 ~')

        # 恢复 data 目录
        def copy_and_log(src, dst):
            Log.info(f'正在恢复数据：{dst}')
            shutil.copy2(src, dst)
        shutil.copytree(
            os.path.join(guardianrecovery_path, 'data'), 
            os.path.join(guardian_path, 'data'),
            copy_function=copy_and_log
        )
        Log.info(f'恢复数据成功 ~')

        # 恢复日志
        restore_guardian_log()

        # 删除 update 目录
        shutil.rmtree(os.path.join(guardianrecovery_path, 'update'))
        Log.info('删除更新包成功 ~')

        # 更新状态标识符
        os.remove(os.path.join(guardianrecovery_path,'.update'))
        with open(os.path.join(guardianrecovery_path,'.rollback'), 'w') as f:
            f.write('')
        Log.info('更新状态标识符成功 ~')

    except Exception as e:
        Log.error(f'升级失败，错误为：{e}')

def rollback_guardian():
    '''在预启动修复环境下回退Guardian主程序 (需要至少更新过一次)'''
    try:
        # 备份Guardian日志
        rollback_guardian_log()

        # 从 rollback 目录回退文件
        shutil.rmtree(guardian_path)
        def copy_and_log(src, dst):
            Log.info(f'正在回退：{dst}')
            shutil.copy2(src, dst)
        shutil.copytree(
            os.path.join(guardianrecovery_path, 'rollback'), 
            guardian_path,
            copy_function=copy_and_log
        )
        Log.info(f'回退文件成功 ~')

        # 恢复 data 目录
        def copy_and_log(src, dst):
            Log.info(f'正在恢复数据：{dst}')
            shutil.copy2(src, dst)
        shutil.copytree(
            os.path.join(guardianrecovery_path, 'data'), 
            os.path.join(guardian_path, 'data'),
            copy_function=copy_and_log
        )
        Log.info(f'恢复数据成功 ~')

        # 恢复日志
        restore_guardian_log()

        # 更新状态标识符
        os.remove(os.path.join(guardianrecovery_path,'.rollback'))
        Log.info('更新状态标识符成功 ~')

    except Exception as e:
        Log.error(f'回退失败，错误为：{e}')

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
        Log.error('未找到可用的恢复环境。程序将会退出。')
        sys.exit(0)
    Log.info(f'寻找到了可用的恢复环境：{guardianrecovery_path}')
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
    if(os.path.exists(os.path.join(guardianrecovery_path, '.rollback'))):
        Log.info('准备回退至更新前的版本... 稍安勿躁 ~')
        time.sleep(2)
        rollback_guardian()
    elif(os.path.exists(os.path.join(guardianrecovery_path, '.update'))):
        Log.info('准备更新至最新版本... 稍安勿躁 ~')
        time.sleep(2)
        update_guardian()
    else:
        Log.info('准备修复至稳定版本... 稍安勿躁 ~')
        time.sleep(2)
        fix_guardian()



if __name__ == "__main__":
    main()