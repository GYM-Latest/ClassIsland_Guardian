import time
from typing import Any

import os

from ui.main_window import start_main_window
from ui.tray import start_tray
from utils.database import Database
from utils.log import LogClass
from utils.process import ProcessClass
from utils.snapshot import SnapshotClass
from utils.update import UpdateClass
from utils.exec import ExecClass


scheduler: Any
db: Database


# 依赖保存函数
def task_dependency_init(_scheduler: Any, _db: Database) -> None:
    global scheduler, db
    scheduler = _scheduler
    db = _db


# 进程丢失后处理任务
def process_missing(
    log: LogClass, process: ProcessClass, snapshot: SnapshotClass
) -> None:
    if process.start_classisland():
        return
    log.info("拉起失败，ClassIsland进程仍未在运行。")

    # 拉起失败后先恢复快照
    log.info("尝试恢复最新快照。")
    # 先备份当前状态
    snapshot.create_snapshot("自动回滚前生成的快照")
    # 忽略自动回滚备份，只恢复真正的历史快照
    snapshots = snapshot.list_snapshot()
    if snapshots:
        snapshots = [s for s in snapshots if "自动回滚前生成的快照" not in s]
        if snapshots and snapshot.restore_snapshot(snapshots[0]):
            if process.start_classisland():
                return
        else:
            log.error("恢复快照时出错，错误是：没有可用快照")

    # 尝试逃逸式启动
    log.info("尝试逃逸式启动。")
    if process.escape_start_classisland():
        log.info(
            f"逃逸式启动成功！当前 ClassIsland 目录：{db.path.get('classisland_path')} ，当前可执行文件名称：{db.path.get('classisland_process_name')}"
        )
        return
    log.error("拉起失败。")


# 重启 ClassIsland 任务
def reboot_classisland(process: ProcessClass) -> None:
    process.reboot_classisland()


# 回滚 ClassIsland 任务
def rollback_classisland(
    log: LogClass, process: ProcessClass, snapshot: SnapshotClass
) -> None:
    snapshot.restore_snapshot()


# 30s轮询检查classisland状态
def check_classisland_issue() -> None:
    from core.scheduler_manager import is_job_running

    log = LogClass("Task.check_classisland_issue")
    process = ProcessClass(db, log)
    if (
        db.config.get("auto_restart_frozen_ci")
        and process.is_classisland_frozen()
        and not scheduler.get_job("fixing_classisland")
    ):
        log.info("日志文件超过 70s 无更新，认定卡死，开始重启。")
        if not is_job_running("fixing_classisland"):
            scheduler.add_job(
                reboot_classisland,
                "date",
                id="fixing_classisland",
                max_instances=1,
                args=[process],
            )

    if db.config.get("rollback_on_crash"):
        pass


# 监控classisland进程任务
def monitor_classisland_process() -> None:
    from core.scheduler_manager import is_job_running

    log = LogClass("Task.monitor_classisland_process")
    process = ProcessClass(db, log)
    snapshot = SnapshotClass(db, log)

    # 根据配置查杀非目录进程
    if db.config.get("kill_non_install_ci"):
        process.kill_non_install_classisland()

    # 根据配置查杀多开进程
    if db.config.get("kill_multi_ci"):
        process.kill_multi_ci()

    # 检查进程状态
    if not process.get_classisland_status() and not is_job_running(
        "fixing_classisland"
    ):
        log.info("检测到ClassIsland进程丢失，尝试拉起ClassIsland。")
        scheduler.add_job(
            process_missing,
            "date",
            id="fixing_classisland",
            max_instances=1,
            args=[log, process, snapshot],
        )


# 检查更新任务
def check_update() -> None:
    log = LogClass("Task.update")
    update = UpdateClass(log, db)
    update.check_update()


# 更新任务
def update() -> None:
    log = LogClass("Task.update")
    update = UpdateClass(log, db)
    update.update(db.state["latest_release"])

# 更新后处理任务
def after_update() -> None:
    log = LogClass("Task.after_update")
    exec = ExecClass(log)
    if os.path.exists(os.path.join(exec.get_exe_path(),".afterupdate")):
        os.remove(os.path.join(exec.get_exe_path(),".afterupdate"))
        update = UpdateClass(log, db)
        update.after_update()

# UI主窗口任务
def main_window() -> None:
    log = LogClass("Task.ui_main_window")

    start_main_window(log, db, scheduler)


# 托盘图标任务
def tray() -> None:
    log = LogClass("Task.ui_tray")

    start_tray(log, db, scheduler)
