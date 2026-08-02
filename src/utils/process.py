# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import psutil
import os
import time

from utils.log import Log
from utils.exec import Exec

class Process:
    def __init__(self,db):
        self.db = db

    # 检查classisland进程数量并返回
    def check_classisland_status(self):
        '检查Classisland进程数量。 返回Classisland进程数量(int)'
        process_quantity = 0
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == self.db.path.get('classisland_process_name'):
                process_quantity += 1; 
        return process_quantity

    # 查找ClassIsland进程pid并返回
    def find_classisland_pid(self):
        '查找ClassIsland进程pid。 返回Classisland进程pid(string)，若未找到，返回False(bool)'
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] == self.db.path.get('classisland_process_name'):
                classisland_process_pid = proc.info['pid']
                return classisland_process_pid
        return False

    # 启动ClassIsland
    def start_classisland(self):
        '启动Classisland。 成功返回True，失败返回False'
        Exec.remove_ifeo(self.db.path.get('classisland_process_name'))
        return Exec.start(os.path.join(self.db.path.get('classisland_path'),self.db.path.get('classisland_launcher_name')))

    # 关闭ClassIsland
    def kill_classisland(self):
        '关闭Classisland。 成功返回True，失败返回False'
        if not Exec.kill_process(self.db.path.get('classisland_process_name')):
            Log.info('关闭失败')
            return False
        return True
    
    # 重启ClassIsland
    def reboot_classisland(self):
        '重启Classisland。 成功返回True，失败返回False'
        if not self.kill_classisland():
            Log.info('重启失败')
            return False
        time.sleep(3)
        if not self.start_classisland():
            Log.info('重启失败')
            return False
        Log.info('重启成功')
        return True