from typing import Any

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from utils.database import Database
from utils.log import LogClass
from utils.process import ProcessClass


class UiBackend(QObject):
    dataChanged = Signal()
    showTransition = Signal()
    hideTransition = Signal()

    def __init__(self, scheduler: Any, db: Database, log: LogClass) -> None:
        super().__init__()
        self.scheduler = scheduler
        self.db = db
        self.log = log

        # 定时重新抓取数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.dataChanged.emit)
        self.timer.start(500)

    @Property("QVariantMap", notify=dataChanged)
    def path(self) -> dict[str, Any]:
        return dict(self.db.path.copy())

    @Property("QVariantMap", notify=dataChanged)
    def state(self) -> dict[str, Any]:
        return dict(self.db.state.copy())

    @Property("QVariantMap", notify=dataChanged)
    def config(self) -> dict[str, Any]:
        return dict(self.db.config.copy())

    @Property("QVariantMap", notify=dataChanged)
    def meta(self) -> dict[str, Any]:
        return dict(self.db.meta.copy())

    @Slot(str, str, "QVariant")
    def set_value(self, target: str, key: str, value: Any) -> None:
        match target:
            case "path":
                self.db.path[key] = value
            case "state":
                self.db.state[key] = value
            case "config":
                self.db.config[key] = value
            case "meta":
                self.db.meta[key] = value

    @Slot()
    def temp_stop_protection(self) -> None:
        from core.scheduler_manager import PROTECT_JOB_LIST

        self.log.info("用户UI请求临时停止保护。")
        self.set_value("config", "protect_state", "tempstop")
        self.showTransition.emit()
        for job_id in PROTECT_JOB_LIST:
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

        self._wait_guardian_jobs_end()

    @Slot()
    def stop_protection(self) -> None:
        from core.scheduler_manager import remove_protect_job

        self.log.info("用户UI请求停止保护。")
        self.set_value("config", "protect_state", "stop")
        remove_protect_job()

        self._wait_guardian_jobs_end()

    @Slot()
    def resume_protection(self) -> None:
        from core.scheduler_manager import add_protect_job

        self.log.info("用户UI请求恢复保护。")
        self.set_value("config", "protect_state", "running")
        add_protect_job()

    @Slot()
    def restart_classisland(self) -> None:
        from core.tasks import reboot_classisland

        self.log.info("用户UI请求重启 ClassIsland 进程。")
        process = ProcessClass(self.db, self.log)
        self.scheduler.add_job(
            reboot_classisland,
            "date",
            args=[process],
            id="fixing_classisland",
            max_instances=1,
        )

    @Slot()
    def check_update(self) -> None:
        from core.tasks import check_update

        self.log.info("用户UI请求检查更新。")
        self.scheduler.add_job(
            check_update,
            "date",
            id="check_update",
            max_instances=1,
        )

    @Slot()
    def update(self) -> None:
        from core.tasks import update

        self.log.info("用户UI请求更新。")
        self.scheduler.add_job(
            update,
            "date",
            id="update",
            max_instances=1,
        )

    def _wait_guardian_jobs_end(self) -> None:
        from core.scheduler_manager import is_guardian_jobs_running

        if is_guardian_jobs_running():
            QTimer.singleShot(100, self._wait_guardian_jobs_end)
        else:
            self.hideTransition.emit()
