from apscheduler.events import EVENT_JOB_ERROR

from core import tasks
from utils.log import LogClass


# 调度器错误处理函数
def task_error_handler(event):
    log = LogClass("Service.task_error_handler")
    try:
        log.error(f"任务 {event.job_id} 发生未被捕获的异常，错误是： {event.exception}")
        scheduler.remove_job(event.job_id)
        log.info(
            f"成功禁用发生异常的任务：{event.job_id}，当前任务列表：{scheduler.get_jobs()}"
        )
    except Exception as e:
        log.error(
            f"禁用异常任务失败，错误是：{e}，当前任务列表：{scheduler.get_jobs()}"
        )


def register_tasks(_scheduler, _db):
    global scheduler, db
    scheduler = _scheduler
    db = _db

    tasks.task_dependency_init(scheduler, db)

    # 注册调度器错误监听
    scheduler.add_listener(task_error_handler, EVENT_JOB_ERROR)

    # 守护主循环
    scheduler.add_job(
        tasks.detect_classisland_pending,
        "interval",
        seconds=30,
        id="detect_classisland_pending",
        max_instances=1,
    )
    scheduler.add_job(
        tasks.monitor_classisland,
        "interval",
        seconds=5,
        id="monitor_classisland",
        max_instances=1,
    )
    scheduler.add_job(
        tasks.update,
        "interval",
        seconds=7200,
        id="update",
        max_instances=1,
    )
    if not scheduler.get_job("update_boot"):
        scheduler.add_job(
            tasks.update,
            "date",
            id="update_boot",
            max_instances=1,
        )
