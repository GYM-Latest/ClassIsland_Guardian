# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import ctypes
import sys
import subprocess
import getpass
import time
import hashlib
import os
import shutil
import readchar

from utils.database import Database
from utils.log import Log
from utils.exec import Exec
from utils.version import VERSION, CODENAME
from utils.snapshot import Snapshot

def check_password():

    while(True):
        Exec.clear_terminal()
        print(f'请输入管理员密码 ~\n')
        print(f'(为安全考虑，输入将不可见)')
        password = getpass.getpass('>')
        if(hashlib.sha256(password.encode('utf-8')).hexdigest() == db.config.get('password')):
            return True
        else:
            print("唔... 密码不对呢，再试试吧")
            time.sleep(1)

def main():
    # 确保以管理员权限运行
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas",
                                            sys.executable,
                                            " ".join(sys.argv), None, 1)

    global db
    global Snapshot
    db = Database(Exec.get_exe_path())
    if(not db.read_database()):
        sys.exit()
    Snapshot = Snapshot(db)

    # 身份验证
    if(db.config.get('password')):
        check_password()

    # 显示主菜单
    while True:
        Exec.clear_terminal()
        print(f'''ClassIsland Guardian Config
版本：{VERSION} | ({CODENAME})
    ''')
        print(f'身份验证通过，欢迎回来 ~\n')
        print('''[1] 保护控制
[2] ClassIsland 快照管理
[3] 查看日志
[4] 系统设置
[5] 关于
[0] 退出管理程序
''')
        result = readchar.readchar()
        if(result == '1'):
            pass
        elif(result == '2'):
            while True:
                Exec.clear_terminal()
                print('''请选择要进行的操作 ~
[1] 查看与管理 ClassIsland 当前已有快照
[2] 拍摄新 ClassIsland 快照
[0] 返回
    ''')        
                result = readchar.readchar()
                try:
                    if(result == '1'):
                        while True:
                            Exec.clear_terminal()
                            snapshot_list = Snapshot.list_snapshot()
                            if(snapshot_list):
                                num = 0
                                for this_snapshot in snapshot_list:
                                    num += 1
                                    print(f'[{num}] {this_snapshot}')
                                print('请输入要操作的快照序号 ~ (输入 0 以返回)')
                                result = input('>')
                                if(result == '0'):
                                    break
                                else:
                                    select_snapshot = result
                                    while True:
                                        Exec.clear_terminal()
                                        print('''请选择要进行的操作 ~
[1] 恢复到所选快照
[2] 删除所选快照
[0] 返回
''')
                                        result = readchar.readchar()
                                        if(result == '1'):
                                            print('正在恢复快照，稍安勿躁 ~')
                                            Snapshot.restore_snapshot(snapshot_list[int(select_snapshot) - 1])
                                            break
                                        elif(result == '2'):
                                            print('正在删除快照，稍安勿躁')
                                            Snapshot.remove_snapshot(snapshot_list[int(select_snapshot) - 1])
                                            break
                                        elif(result == '0'):
                                            break

                    if(result == '2'):
                        print('正在创建快照，稍安勿躁 ~~~')
                        result = Snapshot.create_snapshot()
                        if(result):
                            print(f'成功创建了新快照 ~ ：{result}')
                        time.sleep(1)
                        break
                    if(result == '0'):
                        break
                except Exception as e:
                    Log.error(f'快照操作失败，错误为：{e}')
                    time.sleep(1)
        elif(result == '3'):
            while True:
                Exec.clear_terminal()
                print('''请选择要查看的日志类型 ~
[1] Guardian 主程序日志
[2] Recovery 预启动修复日志
[0] 返回
''')
                result = readchar.readchar()
                try:
                    if(result == '1'):
                        os.startfile(os.path.join(Exec.get_exe_path(), 'data', 'guardian.log'))
                        break
                    if(result == '2'):
                        shutil.copy2(
                            os.path.join(os.path.splitdrive(Exec.get_exe_path())[0] + "\\", "GuardianRecovery", "recovery.log"),
                            os.path.join(os.environ.get("TEMP"), "recovery.log")
                        )
                        os.startfile(os.path.join(os.environ.get("TEMP"), "recovery.log"))
                        break
                    if(result == '0'):
                        break
                except Exception as e:
                    Log.error(f'打开日志文件失败，错误为：{e}')
                    time.sleep(1)
        elif(result == '4'):
            pass
        elif(result == '5'):
            pass
        elif(result == '0'):
            sys.exit(0)
        else:
            pass

if __name__ == "__main__":
    main()