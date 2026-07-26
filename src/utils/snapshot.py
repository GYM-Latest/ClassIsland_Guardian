# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

from datetime import datetime
import os
import zipfile
import shutil

from utils.exec import Exec
from utils.log import Log
from utils.process import Process

class Snapshot:
    def __init__(self,db):
        self.db = db
        self.snapshot_dir = os.path.join(Exec.get_exe_path(),'data','snapshot')
        self.Process = Process(db)
        self.classisland_path = db.path.get('classisland_path')
        
    def list_snapshot(self):
        '列出所有可用的快照。 成功返回列表，失败返回False'
        try:
            filelist = os.listdir(self.snapshot_dir)
            filelist.sort(reverse=True)
            return filelist
        except Exception as e:
            Log.error(f'列出快照时出错，错误为：{e}')
            return False
        
    def restore_snapshot(self,name):
        '恢复到指定的快照。 传入要恢复快照的文件名(string) 成功返回True，失败返回False'
        Exec.kill_process(self.db.path.get('classisland_process_name'))
        if os.path.exists(os.path.join(self.snapshot_dir,name)):
            try:
                try:
                    shutil.rmtree(self.classisland_path)
                except:
                    pass
                os.mkdir(self.classisland_path)
                with zipfile.ZipFile(os.path.join(self.snapshot_dir,name), 'r') as zf:
                    zf.extractall(path=self.classisland_path)
                    Log.info(f'成功恢复到指定快照：{name}')
                    return True
            except Exception as e:
                Log.error(f'恢复时出错，错误为：{e}')
                return False
        else:
            Log.error(f'恢复时出错，指定的快照文件不存在')
            return False
    
    def create_snapshot(self):
        '创建一个快照。 成功返回快照名称，失败返回False。'
        if not self.Process.kill_classisland():
            return False
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        zip_name = f'snapshot_{timestamp}.zip'

        try:
            if os.path.exists(self.classisland_path):
                os.makedirs(self.snapshot_dir, exist_ok=True)
                with zipfile.ZipFile(os.path.join(self.snapshot_dir,zip_name), 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, _, files in os.walk(self.classisland_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.classisland_path)
                            zf.write(file_path, arcname)
                return zip_name
            else:
                Log.error(f'压缩文件时出错，错误是：ClassIsland目录不存在')
                return False
        except Exception as e:
            Log.error(f'压缩文件时出错，错误是：{e}')
            return False

    def remove_snapshot(self,name):
        '移除指定的快照。 传入要删除的快照名称(String) 成功返回True，失败返回False'
        try:
            os.remove(os.path.join(self.snapshot_dir, name))
            return True
        except Exception as e:
            Log.error(f'移除快照时出错，错误为：{e}')
            return False