# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import sys
import threading
import time
from datetime import datetime

import psutil
from apscheduler.schedulers.background import BackgroundScheduler

import utils.win_graceful_shutdown  # noqa: F401  （副作用导入：import 即注册关机钩子）
from utils.bcd import Bcd
from utils.database import Database
from utils.exec import Exec
from utils.log import Log
from utils.process import Process
from utils.snapshot import Snapshot
from utils.version import CODENAME, VERSION


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
    if Process.start_classisland():
        Log.warn("尝试拉起ClassIsland。")
        time.sleep(5)
        status = Process.check_classisland_status()
        if status == 1:
            Log.info("拉起成功，ClassIsland进程正常 ~")
            return

    Log.warn("拉起失败，ClassIsland进程仍未在运行，尝试修复")
    snapshots = Snapshot.list_snapshot()
    if snapshots and Snapshot.restore_snapshot(snapshots[0]):
        Log.info("修复成功，尝试拉起ClassIsland ~")
        if Process.start_classisland():
            Log.info("拉起成功，ClassIsland进程正常 ~")
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
            psutil.Process(result).wait(1)
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


# 守护主循环
def main():
    try:
        global db
        global Process
        global Snapshot
        global scheduler

        global is_reboot
        global is_config_running
        scheduler = BackgroundScheduler()
        # 热重启竞态检测标识
        is_reboot = False
        # config 运行状态标识
        is_config_running = False

        db = Database(Exec.get_exe_path())
        if not db.read_database():
            Bcd.set_recovery_bcd_start()
        Process = Process(db)
        Snapshot = Snapshot(db)
        Exec.make_process_critical()
        Log.info(f"ClassIsland Guardian 已启动 ~ | 版本：{VERSION} ({CODENAME})")

        if os.path.exists(os.path.join(Exec.get_exe_path(), ".tempstopprotect")):
            os.remove(os.path.join(Exec.get_exe_path(), ".tempstopprotect"))

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
