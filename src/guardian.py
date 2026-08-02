# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import time
import sys
from datetime import datetime
import psutil
import threading
import utils.win_graceful_shutdown

from utils.log import Log
from utils.database import Database
from utils.process import Process
from utils.exec import Exec
from utils.snapshot import Snapshot
from utils.version import VERSION, CODENAME

# 进程丢失后处理函数
def process_missing():
    if Process.start_classisland():
        Log.warn('尝试拉起ClassIsland。')
        time.sleep(5)
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

# 120s轮询线程
def poll_thread():
    try:
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
        # 延时尝试热重启，避免程序崩溃
        time.sleep(5)
        main()
        return

# 监控线程
def monitor_thread():
    try:
        while True:
            time.sleep(10)
            result = Process.find_classisland_pid()
            if(result):
                psutil.Process(result).wait()
                process_missing()
            else:
                process_missing()

    except Exception as e:
        try:
            Log.error(f'发生无法处理的错误：{e}')
        except:
            logfile = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__), 'guardian.log')
            with open(logfile, 'a') as f:
                f.write(f'{datetime.now()}: {e}\n')
        # 延时尝试热重启，避免程序崩溃
        time.sleep(5)
        main()
        return

# 守护主循环
def main():
    while True:
        try: 
            global db
            global Process
            global Snapshot

            db = Database(Exec.get_exe_path())
            if(not db.read_database()):
                sys.exit(0)
            Process = Process(db)
            Snapshot = Snapshot(db)
            Exec.make_process_critical()
            Log.info(f'ClassIsland Guardian 已启动 ~ | 版本：{VERSION} ({CODENAME})')

            # 守护主循环
            threading.Thread(target=poll_thread, daemon=False).start()
            threading.Thread(target=monitor_thread, daemon=False).start()
            return
        
        except Exception as e:
                try:
                    Log.error(f'发生无法处理的错误：{e}')
                except:
                    logfile = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__), 'guardian.log')
                    with open(logfile, 'a') as f:
                        f.write(f'{datetime.now()}: {e}\n')
                # 延时尝试热重启，避免程序崩溃
                time.sleep(5)

if __name__ == "__main__":
    main()