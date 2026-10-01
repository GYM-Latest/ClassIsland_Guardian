# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

try:
    import os
    import sys
    import threading
    from datetime import datetime

    import win32api
    import win32event
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.executors.pool import ThreadPoolExecutor
    from apscheduler.schedulers.base import STATE_STOPPED
    from winerror import ERROR_ALREADY_EXISTS

    import core.exit_app
    import core.scheduler
    from utils.bcd import BcdClass
    from utils.database import Database
    from utils.exec import ExecClass
    from utils.log import LogClass
    from utils.version import CODENAME, VERSION

    import_error = None

except Exception as e:
    import_error = e

# 互斥锁句柄
_instance_mutex = None

# 热重启次数记录
hot_reboot_time = 0
# 热重启竞态检测标识
is_reboot = False


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
    log = LogClass("Service.hot_reboot")
    exec = ExecClass(log)
    try:
        global is_reboot
        global hot_reboot_time
        if not is_reboot:
            is_reboot = True
            if scheduler.state != STATE_STOPPED:
                scheduler.shutdown(True)
            if hot_reboot_time >= 5:
                log.info("热重启次数达到上限，不再重启并关闭进程。")
                exec.unmake_process_critical()
                os._exit(0)
            hot_reboot_time += 1
            log.info(f"这是第 {hot_reboot_time} 次热重启。")
            main()
    except:
        exec.unmake_process_critical()
        os._exit(0)


# 守护进程主入口
def main():
    try:
        global scheduler, is_reboot

        # 导入失败直接退出，这里后续可以弹窗
        if import_error:
            sys.exit(1)

        # 初始化日志和 BCD
        log = LogClass("Service.start_app")
        bcd = BcdClass(log)
        exec = ExecClass(log)

        # 初始化调度器与热重启标志
        executors = {
            "default": ThreadPoolExecutor(10),
            "main_window": ThreadPoolExecutor(1),
        }
        scheduler = BackgroundScheduler(executors=executors)
        is_reboot = False

        # 初始化数据库
        db = Database(os.path.join(exec.get_exe_path(), "data", "config.db"))
        if not db.read_database(log) and os.path.exists(
            os.path.join(exec.get_exe_path(), "data", "guardian_config.db")
        ):
            log.info("检测到数据库需要迁移，正在迁移...")
            db.database_path = os.path.join(
                exec.get_exe_path(), "data", "guardian_config.db"
            )
            if db.read_v0_4_x_database(log):
                db.database_path = os.path.join(
                    exec.get_exe_path(), "data", "config.db"
                )
                if db.new_database(log):
                    log.info("数据库迁移成功。")
        db.save_database(log)

        # 标记关键进程
        exec.make_process_critical()

        log.info(f"ClassIsland Guardian 已启动 ~ | 版本：{VERSION} ({CODENAME})")

        # 删除可能存在的标识符
        # 删除更新标识符并调整启动顺序
        if os.path.exists(os.path.join(exec.get_exe_path(), ".afterupdate")):
            os.remove(os.path.join(exec.get_exe_path(), ".afterupdate"))
            os.remove(
                os.path.join(
                    os.environ.get("SystemDrive", "C:") + "\\",
                    "GuardianRecovery",
                    ".rollback",
                )
            )
            bcd.set_windows_bcd_start()

        # 这里调用 core/scheduler.py
        core.scheduler.register_tasks(scheduler, db)
        scheduler.start()
        # 运行 Service.app_exit()
        core.exit_app.init(scheduler)

    except Exception as e:
        log = LogClass("Service.hot_reboot")
        try:
            log.error(f"发生无法处理的错误：{e}")
            log.error("触发热重启 ~")
        except:
            logfile = os.path.join(
                os.path.dirname(sys.executable)
                if getattr(sys, "frozen", False)
                else os.path.dirname(__file__),
                "guardian.log",
            )
            with open(logfile, "a") as f:
                f.write(f"{datetime.now()}: {e}\n")
        # 尝试热重启，避免程序崩溃
        threading.Thread(target=hot_reboot, daemon=True).start()


if __name__ == "__main__":
    prevent_multiple_instances()
    main()
