from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot


class UiBackend(QObject):
    dataChanged = Signal()
    showTransition = Signal()
    hideTransition = Signal()

    def __init__(self, scheduler, db, log):
        super().__init__()
        self.scheduler = scheduler
        self.db = db
        self.log = log

        # 定时重新抓取数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.dataChanged.emit)
        self.timer.start(500)

    @Property("QVariantMap", notify=dataChanged)
    def path(self):
        return dict(self.db.path)

    @Property("QVariantMap", notify=dataChanged)
    def state(self):
        return dict(self.db.state)

    @Property("QVariantMap", notify=dataChanged)
    def config(self):
        return dict(self.db.config)

    @Property("QVariantMap", notify=dataChanged)
    def meta(self):
        return dict(self.db.meta)

    @Slot(str, str, "QVariant")
    def set_value(self, target, key, value):
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
    def temp_stop_protection(self):
        from core.scheduler import PROTECT_JOB_LIST

        self.set_value("config", "protect_state", "tempstop")
        self.showTransition.emit()
        for job_id in PROTECT_JOB_LIST:
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

        self._wait_guardian_jobs_end()

    @Slot()
    def stop_protection(self):
        from core.scheduler import remove_protect_job

        self.set_value("config", "protect_state", "stop")
        remove_protect_job()

        self._wait_guardian_jobs_end()

    @Slot()
    def resume_protection(self):
        from core.scheduler import add_protect_job

        self.set_value("config", "protect_state", "running")
        add_protect_job()

    @Slot()
    def check_update(self):
        from core.tasks import check_update

        self.scheduler.add_job(
            check_update,
            "date",
            id="check_update",
            max_instances=1,
        )

    @Slot()
    def update(self):
        from core.tasks import update

        self.scheduler.add_job(
            update,
            "date",
            id="check_update",
            max_instances=1,
        )

    def _wait_guardian_jobs_end(self):
        from core.scheduler import is_guardian_jobs_running

        if is_guardian_jobs_running():
            QTimer.singleShot(100, self._wait_guardian_jobs_end)
        else:
            self.hideTransition.emit()
