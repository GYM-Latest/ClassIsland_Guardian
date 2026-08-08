# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 GYM_Latest

import os
import sys
from datetime import datetime


class Log:
    def __init__(self):
        self.logfile = os.path.join(
            os.path.dirname(sys.executable)
            if getattr(sys, "frozen", False)
            else os.path.dirname(__file__),
            "data",
            "guardian.log",
        )

    def _write(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line)
        try:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except:
            pass

    def log(self, msg):
        self._write(f"(annotation) {msg}")

    def info(self, msg):
        self._write(f"(info) {msg}")

    def warn(self, msg):
        self._write(f"(warn) {msg}")

    def error(self, msg):
        self._write(f"(error) {msg}")

    def _organize_log(self):
        pass


Log = Log()
