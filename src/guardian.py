# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import subprocess
import os
import time
import sys
from datetime import datetime
import utils.win_graceful_shutdown
import atexit

from utils.log import Log
from utils.database import Database
from utils.process import Process
from utils.exec import Exec
from utils.snapshot import Snapshot
from utils.version import VERSION, CODENAME

# 设置计划任务
def register_self():
    task_name = "ClassIslandGuardian"
    exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__

    try:
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            Log.info('自启动项存在 ~')
            return True
        
        Log.info('自启动项不存在，尝试创建自启动项 ~')
        subprocess.run([
            "schtasks", "/Create",
            "/TN", task_name,
            "/TR", f'"{exe_path}"',
            "/SC", "ONLOGON",
            "/DELAY", "0001:00",
            "/RL", "HIGHEST",
            "/F"
        ], capture_output=True)
        Log.info('创建成功 ~')
        return True
    except Exception:
        Log.info('')
        return False

# 进程退出后处理函数
def in_shutdown():
    pass

# 进程丢失后处理函数
def process_missing():
    if Process.start_classisland():
        Log.warn('尝试拉起ClassIsland。')
        time.sleep(30)
        status = Process.check_classisland_status()
        if status == 1:
            Log.info('拉起成功，ClassIsland进程正常 ~')
            return
    
    Log.warn('拉起失败，ClassIsland进程仍未在运行，尝试修复')
    if Snapshot.restore_snapshot(Snapshot.list_snapshot()[0]):
        Log.info('修复成功，尝试拉起ClassIsland ~')
        if Process.start_classisland():
            Log.info('拉起成功，ClassIsland进程正常 ~')
            return

    Log.error('修复失败。')

def main():
    try: 
        global db
        global Process
        global Snapshot

        db = Database(Exec.get_exe_path())
        if(not db.read_database()):
            sys.exit(0)
        Process = Process(db)
        Snapshot = Snapshot(db)
        Log.info(f'ClassIsland Guardian 已启动 ~ | 版本：{VERSION} ({CODENAME})')

        register_self()

        while(True):
            time.sleep(120)
            status = Process.check_classisland_status()
            if status == 1:
                Log.info('检查ClassIsland，进程正常 ~')
            elif status == 0:
                process_missing()
            elif status >= 2:
                Log.info(f'(Warning) 检测到 {status} 个ClassIsland进程，确认卡死，正在重启')
                Process.reboot_classisland()
    except Exception as e:
            try:
                Log.error(f'发生无法处理的错误：{e}')
            except:
                logfile = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__), 'guardian.log')
                with open(logfile, 'a') as f:
                    f.write(f'{datetime.now()}: {e}\n')
            time.sleep(5)
            subprocess.Popen(
                [sys.executable],
                cwd=os.path.dirname(sys.executable),
                close_fds=True
            )
            sys.exit(0)

atexit.register(in_shutdown)

if __name__ == "__main__":
    main()