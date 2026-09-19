import os
import time

import psutil

from utils.log import LogClass
from utils.process import ProcessClass
from utils.snapshot import SnapshotClass
from utils.update import UpdateClass
from utils.version import VERSION


# 依赖保存函数
def task_dependency_init(_scheduler, _db):
    global scheduler, db
    scheduler = _scheduler
    db = _db


# 进程丢失后处理任务
def process_missing(log, process, snapshot):
    # 在拉起前，先检查 ClassIsland 是否有后备进程
    # 如果有，说明在重启，直接返回
    if process.check_classisland_status() != 0:
        log.info("识别到 ClassIsland 正在重启，忽略......")
        return

    # 进程消失后短暂观察，等待可能的主动重启
    for _ in range(4):
        time.sleep(0.5)
        if process.check_classisland_status() != 0:
            log.info("识别到 ClassIsland 正在重启，忽略......")
            return

    # 先尝试直接拉起
    log.warn("检测到ClassIsland进程丢失，尝试拉起ClassIsland。")
    if process.start_classisland():
        return
    log.warn("拉起失败，ClassIsland进程仍未在运行。")

    # 拉起失败后先恢复快照
    log.warn("尝试恢复最新快照。")
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
    log.error("尝试逃逸式启动。")
    if process.escape_start_classisland():
        log.info(
            f"逃逸式启动成功！当前 ClassIsland 目录：{db.path.get('classisland_path')} ，当前可执行文件名称：{db.path.get('classisland_process_name')}"
        )
        return
    log.error("拉起失败。")


# 重启 ClassIsland 任务
def reboot_classisland(process):
    process.reboot_classisland()


# 30s轮询卡死检测任务
def detect_classisland_pending():
    log = LogClass("Task.detect_classisland_pending")
    process = ProcessClass(db, log)
    if not process.check_classisland_frozen() and not scheduler.get_job(
        "fixing_classisland"
    ):
        log.info("日志文件超过 70s 无更新，认定卡死，开始重启。")
        scheduler.add_job(
            reboot_classisland,
            "date",
            id="fixing_classisland",
            max_instances=1,
            args=[process],
        )


# 监控任务
def monitor_classisland():
    log = LogClass("Task.monitor_classisland")
    process = ProcessClass(db, log)
    snapshot = SnapshotClass(db, log)

    result = process.find_classisland_pid()
    if result:
        try:
            psutil.Process(result).wait(4)
            if not scheduler.get_job("fixing_classisland"):
                scheduler.add_job(
                    process_missing,
                    "date",
                    id="fixing_classisland",
                    max_instances=1,
                    args=[log, process, snapshot],
                )
        except psutil.TimeoutExpired:
            return
    else:
        if not scheduler.get_job("fixing_classisland"):
            scheduler.add_job(
                process_missing,
                "date",
                id="fixing_classisland",
                max_instances=1,
                args=[log, process, snapshot],
            )


# 更新任务
def update():
    log = LogClass("Task.update")
    update = UpdateClass(log)
    try:
        latest_tag = update.check_update("pre")
        if not latest_tag:
            return False
        system_drive = os.environ.get("SystemDrive", "C:") + "\\"
        guardianrecovery_path = os.path.join(system_drive, "GuardianRecovery")
        if latest_tag != VERSION and (
            not os.path.exists(os.path.join(guardianrecovery_path, ".update"))
        ):
            update.update()
    except Exception as e:
        log.warn(f"更新失败，错误是：{e}")
