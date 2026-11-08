from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler

import os
from core import tasks
from utils.database import Database
from utils.log import LogClass

# 守护任务列表，停止守护时会停止这里的任务
PROTECT_JOB_LIST = {"monitor_classisland_process", "check_classisland_issue"}
scheduler: BackgroundScheduler
db: Database


# 调度器错误处理函数
def task_error_handler(event: JobExecutionEvent) -> None:
    log = LogClass("Service.task_error_handler")
    try:
        log.error(
            f"任务 {event.job_id} 发生未被捕获的异常，错误是： {event.exception}, 堆栈是：{event.traceback}"
        )
        scheduler.remove_job(event.job_id)
        log.info(
            f"成功禁用发生异常的任务：{event.job_id}，当前任务列表：{scheduler.get_jobs()}"
        )
    except Exception as e:
        log.error(
            f"禁用异常任务失败，错误是：{e}，当前任务列表：{scheduler.get_jobs()}"
        )


def init_tasks(_scheduler: BackgroundScheduler, _db: Database) -> None:
    global scheduler, db
    scheduler = _scheduler
    db = _db

    tasks.task_dependency_init(scheduler, db)

    # 注册调度器错误监听
    scheduler.add_listener(task_error_handler, EVENT_JOB_ERROR)

    # 添加保护任务
    add_protect_job()

    # 添加检查更新任务
    scheduler.add_job(
        tasks.check_update,
        "date",
        id="check_update",
        max_instances=1,
    )
    
    # 添加更新后处理任务
    scheduler.add_job(
        tasks.after_update,
        "date",
        id="after_update",
        max_instances=1,
    )

    # UI图标任务
    scheduler.add_job(
        tasks.tray,
        "date",
        id="ui_tray",
        max_instances=1,
    )


def is_guardian_jobs_running() -> bool:
    """检查是否有守护任务正在执行"""
    for executor in scheduler._executors.values():
        for job_id in executor._instances:
            if job_id in PROTECT_JOB_LIST:
                return True
    return False


def is_job_running(job_id: str) -> bool:
    """检查指定任务是否正在执行"""
    if scheduler.get_job(job_id):
        return True
    for executor in scheduler._executors.values():
        for this_job_id in executor._instances:
            if this_job_id == job_id:
                return True
    return False


def add_protect_job() -> None:
    """添加守护任务进调度器。"""
    scheduler.add_job(
        tasks.monitor_classisland_process,
        "interval",
        seconds=1,
        id="monitor_classisland_process",
        max_instances=1,
    )
    scheduler.add_job(
        tasks.check_classisland_issue,
        "interval",
        seconds=5,
        id="check_classisland_issue",
        max_instances=1,
    )


def remove_protect_job() -> None:
    """移除守护任务出调度器。"""
    for job_id in PROTECT_JOB_LIST:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
