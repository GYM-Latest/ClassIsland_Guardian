# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import sys
import threading
from datetime import datetime

import psutil
import win32api
import win32event
from apscheduler.schedulers.background import BackgroundScheduler
from winerror import ERROR_ALREADY_EXISTS

import utils.win_graceful_shutdown
from utils.bcd import Bcd
from utils.database import Database
from utils.exec import Exec
from utils.log import Log
from utils.process import Process
from utils.snapshot import Snapshot
from utils.update import Update
from utils.version import CODENAME, VERSION

# 互斥锁句柄
_instance_mutex = None


# 检查并创建互斥锁
def prevent_multiple_instances():
    """防止多实例启动，若已有实例则退出程序"""
    try:
        global _instance_mutex
        mutex_name = "Global\\ClassIslandGuardian_Instance"
        _instance_mutex = win32event.CreateMutex(None, False, mutex_name)
        if win32api.GetLastError() == ERROR_ALREADY_EXISTS:
            sys.exit(0)
    except:
        sys.exit(0)


# 热重启函数
def hot_reboot():
    try:
        global is_reboot
        if not is_reboot:
            is_reboot = True
            scheduler.shutdown(True)
            main()
    except:
        Exec.unmake_process_critical()
        sys.exit()


# 调度器错误处理函数
def error_handler(event):
    Log.error(f"任务 {event.job_id} 发生未被捕获的异常，错误是： {event.exception}")
    Log.error("触发热重启 ~")
    threading.Thread(target=hot_reboot, daemon=True).start()


# 进程丢失后处理函数
def process_missing():
    if is_config_running:
        return

    # 先尝试直接拉起
    Log.warn("尝试拉起ClassIsland。")
    if Process.start_classisland():
        return
    Log.warn("拉起失败，ClassIsland进程仍未在运行，尝试恢复最新快照")

    # 拉起失败后先恢复快照
    # 先备份当前状态
    Snapshot.create_snapshot("自动回滚前生成的快照")
    # 忽略自动回滚备份，只恢复真正的历史快照
    snapshots = Snapshot.list_snapshot()
    if snapshots:
        snapshots = [s for s in snapshots if "自动回滚前生成的快照" not in s]
        if snapshots and Snapshot.restore_snapshot(snapshots[0]):
            Log.info("修复成功，尝试拉起ClassIsland ~")
            if Process.start_classisland():
                return

    # 尝试逃逸式启动
    if Process.escape_start_classisland():
        Log.info("逃逸式启动成功！")
        return
    Log.error("修复失败。")


# 重启 ClassIsland
def reboot_classisland():
    if is_config_running:
        return
    Process.reboot_classisland()


# 120s轮询线程
def poll_classisland():
    if is_config_running:
        return
    status = Process.check_classisland_status()
    if status == 1:
        Log.info("检查ClassIsland，进程正常 ~")
    elif status == 0:
        if not scheduler.get_job("process_missing"):
            scheduler.add_job(
                process_missing,
                "date",
                id="process_missing",
                max_instances=1,
            )
    elif status >= 2:
        Log.info(f"(Warning) 检测到 {status} 个ClassIsland进程，确认卡死，正在重启")
        if not scheduler.get_job("reboot_classisland"):
            scheduler.add_job(
                reboot_classisland,
                "date",
                id="reboot_classisland",
                max_instances=1,
            )


# 监控线程
def monitor_classisland():
    result = Process.find_classisland_pid()
    if result:
        try:
            psutil.Process(result).wait(4)
            if not scheduler.get_job("process_missing"):
                scheduler.add_job(
                    process_missing,
                    "date",
                    id="process_missing",
                    max_instances=1,
                )
        except psutil.TimeoutExpired:
            return
    else:
        if not scheduler.get_job("process_missing"):
            scheduler.add_job(
                process_missing,
                "date",
                id="process_missing",
                max_instances=1,
            )


# 标识符识别线程
def identifier_monitor():
    global is_config_running
    if os.path.exists(
        os.path.join(Exec.get_exe_path(), ".stopprotect")
    ) or os.path.exists(os.path.join(Exec.get_exe_path(), ".tempstopprotect")):
        scheduler.pause_job("poll_classisland")
        scheduler.pause_job("monitor_classisland")
    else:
        scheduler.resume_job("poll_classisland")
        scheduler.resume_job("monitor_classisland")
    is_config_running = False
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] == "config.exe":
                if os.path.normcase(os.path.dirname(proc.exe())) == os.path.normcase(
                    Exec.get_exe_path()
                ):
                    is_config_running = True
                    scheduler.pause_job("poll_classisland")
                    scheduler.pause_job("monitor_classisland")
                else:
                    Log.warn(
                        f"识别到存在可能伪造的config进程！详细信息：{proc.as_dict()}"
                    )
        except Exception as e:
            Log.error(f"检查config进程时出错，错误是：{e}")


# 更新线程
def update():
    try:
        latest_tag = Update.check_update("pre")
        if not latest_tag:
            return False
        system_drive = os.environ.get("SystemDrive", "C:") + "\\"
        guardianrecovery_path = os.path.join(system_drive, "GuardianRecovery")
        if latest_tag != VERSION and (
            not os.path.exists(os.path.join(guardianrecovery_path, ".update"))
        ):
            Update.update()
    except Exception as e:
        # 更新失败是小事，不应触发热重启
        Log.warn(f"更新失败，错误是：{e}")


# 守护主循环
def main():
    try:
        prevent_multiple_instances()

        global db
        global Process
        global Snapshot
        global scheduler
        global Log

        global is_reboot
        global is_config_running
        scheduler = BackgroundScheduler()
        # 注入关机钩子模块，并给其调度器赋值
        utils.win_graceful_shutdown.scheduler = scheduler
        # 热重启竞态检测标识
        is_reboot = False
        # config 运行状态标识
        is_config_running = False

        db = Database(Exec.get_exe_path())
        if not db.read_database():
            Bcd.set_recovery_bcd_start()
        Process = Process(db)
        Snapshot = Snapshot(db)
        Log = Log("guardian")
        Exec.make_process_critical()
        Log.info(f"ClassIsland Guardian 已启动 ~ | 版本：{VERSION} ({CODENAME})")

        # 删除可能存在的标识符
        # 删除暂时停止保护标识符
        if os.path.exists(os.path.join(Exec.get_exe_path(), ".tempstopprotect")):
            os.remove(os.path.join(Exec.get_exe_path(), ".tempstopprotect"))
        # 删除更新标识符并调整启动顺序
        if os.path.exists(os.path.join(Exec.get_exe_path(), ".afterupdate")):
            os.remove(os.path.join(Exec.get_exe_path(), ".afterupdate"))
            os.remove(
                os.path.join(
                    os.environ.get("SystemDrive", "C:") + "\\",
                    "GuardianRecovery",
                    ".rollback",
                )
            )
            Bcd.set_windows_bcd_start()

        # 守护主循环
        scheduler.add_job(
            poll_classisland,
            "interval",
            seconds=120,
            id="poll_classisland",
            max_instances=1,
        )
        scheduler.add_job(
            monitor_classisland,
            "interval",
            seconds=5,
            id="monitor_classisland",
            max_instances=1,
        )
        scheduler.add_job(
            identifier_monitor,
            "interval",
            seconds=3,
            id="identifier_monitor",
            max_instances=1,
        )
        scheduler.add_job(
            update,
            "interval",
            seconds=7200,
            id="update",
            max_instances=1,
        )
        if not scheduler.get_job("update_boot"):
            scheduler.add_job(
                update,
                "date",
                id="update_boot",
                max_instances=1,
            )
        scheduler.start()
        return

    except Exception as e:
        try:
            Log.error(f"发生无法处理的错误：{e}")
        except:
            logfile = os.path.join(
                os.path.dirname(sys.executable)
                if getattr(sys, "frozen", False)
                else os.path.dirname(__file__),
                "guardian.log",
            )
            with open(logfile, "a") as f:
                f.write(f"{datetime.now()}: {e}\n")
        # 延时尝试热重启，避免程序崩溃
        threading.Thread(target=hot_reboot, daemon=True).start()


if __name__ == "__main__":
    main()
    threading.Event().wait()
