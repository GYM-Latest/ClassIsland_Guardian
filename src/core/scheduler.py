from apscheduler.events import EVENT_JOB_ERROR

from core import tasks
from utils.log import LogClass

# 守护任务列表，停止守护时会停止这里的任务
PROTECT_JOB_LIST = {"monitor_classisland", "detect_classisland_pending"}


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

    # 添加任务
    add_protect_job()

    # scheduler.add_job(
    #     tasks.check_update,
    #     "date",
    #     id="check_update",
    #     max_instances=1,
    # )
    # 测试用的UI任务
    scheduler.add_job(
        tasks.tray,
        "date",
        id="test_ui",
        max_instances=1,
    )


def is_guardian_jobs_running():
    """检查是否有守护任务正在执行"""
    for executor in scheduler._executors.values():
        for job_id in executor._instances:
            if job_id in PROTECT_JOB_LIST:
                return True
    return False


def add_protect_job():
    """添加守护任务进调度器。"""
    scheduler.add_job(
        tasks.monitor_classisland,
        "interval",
        seconds=5,
        id="monitor_classisland",
        max_instances=1,
    )
    if db.config["kill_multi_ci"]:
        scheduler.add_job(
            tasks.check_classisland_multi,
            "interval",
            seconds=30,
            id="check_classisland_multi",
            max_instances=1,
        )


def remove_protect_job():
    """移除守护任务出调度器。"""
    for job_id in PROTECT_JOB_LIST:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
