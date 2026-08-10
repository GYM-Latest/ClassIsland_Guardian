import os
import shutil
import subprocess

import readchar

from utils.bcd import Bcd
from utils.exec import Exec


def main():
    if not os.path.exists(os.path.join(Exec.get_exe_path(), ".uninstall")):
        print("请在 config.exe 中触发卸载流程，而不是直接运行 uninstall.exe")
        print("按任意键退出...")
        readchar.readchar()
        return

    recovery_path = os.path.join(
        os.environ.get("SystemDrive", "C:") + "\\", "GuardianRecovery"
    )
    guardian_path = os.path.join(
        os.environ.get("ProgramFiles", r"C:\Program Files"), "Guardian"
    )
    drivers_path = os.path.join(
        os.environ.get("SystemRoot", r"C:\Windows"), "System32", "drivers"
    )

    print("正在进行卸载...")
    # 先删除 BCD 启动项
    if not Bcd.remove_recovery_bcd():
        print("删除 BCD 启动项失败，请尝试手动删除。")
        print("按任意键继续卸载...")
        readchar.readchar()
    # 删除 GuardianRecovery 目录
    if os.path.exists(recovery_path):
        shutil.rmtree(recovery_path)
    # 删除驱动文件
    for driver in ["file.sys", "process.sys", "registry.sys"]:
        driver_file = os.path.join(drivers_path, driver)
        if os.path.exists(driver_file):
            os.remove(driver_file)
    # 删除 config.py 创建的计划任务
    subprocess.run(
        ["schtasks", "/Delete", "/TN", "ClassIslandGuardianUninstall", "/F"],
        capture_output=True,
        check=False,
    )
    # 延迟删除 Guardian 安装目录（uninstall.exe 自身在其中运行，需等进程退出）
    subprocess.Popen(
        f'ping 127.0.0.1 -n 3 > nul & rmdir /s /q "{guardian_path}"',
        shell=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    print("卸载完成 ~")
    return


if __name__ == "__main__":
    main()
