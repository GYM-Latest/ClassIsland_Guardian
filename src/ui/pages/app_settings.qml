import QtQuick
import QtQuick.Layouts
import RinUI

FluentPage {
    id: appSettings
    title: "应用设置"

    Text {
        text: "自保护"
        typography: Typography.BodyStrong
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_shield_lock_20_regular"
        title: "标记为系统关键进程"
        description: "Guardian 自身被结束时会触发蓝屏，防止恶意结束"

        Switch {
            checked: backend.config.critical_process
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "critical_process", checked
            )
        }
    }

    Text {
        text: "安全"
        typography: Typography.BodyStrong
        Layout.topMargin: 16
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_window_shield_20_regular"
        title: "窗口置顶模式"
        description: "选择 Guardian 窗口的置顶策略"

        ComboBox {
            model: [
                { text: "不置顶", value: "none" },
                { text: "UIAccess", value: "uiaccess" },
                { text: "安全桌面", value: "secure_desktop" },
            ]
            textRole: "text"
            valueRole: "value"
            Component.onCompleted: {
                for (var i = 0; i < model.length; i++) {
                    if (model[i].value === backend.config.window_top_mode) {
                        currentIndex = i
                        break
                    }
                }
            }
            onActivated: backend.set_value(
                "config", "window_top_mode", model[currentIndex].value
            )
        }
    }

    Text {
        text: "更新"
        typography: Typography.BodyStrong
        Layout.topMargin: 16
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_arrow_download_20_regular"
        title: "自动检查更新"
        description: "检查到新版本时弹出提示"

        Switch {
            checked: backend.config.auto_download_update
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "auto_download_update", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_channel_20_regular"
        title: "更新通道"
        description: "测试通道：接收所有版本更新，包括预发行版。可能包含 Bug 或未完工的功能\n稳定通道：接收稳定版更新，稳定性较高"

        ComboBox {
            model: [
                { text: "稳定通道", value: "stable" },
                { text: "测试通道", value: "pre" },
            ]
            textRole: "text"
            valueRole: "value"
            Component.onCompleted: {
                for (var i = 0; i < model.length; i++) {
                    if (model[i].value === backend.config.update_channel) {
                        currentIndex = i
                        break
                    }
                }
            }
            onActivated: backend.set_value(
                "config", "update_channel", model[currentIndex].value
            )
        }
    }

    Text {
        text: "通知与托盘"
        typography: Typography.BodyStrong
        Layout.topMargin: 16
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_apps_20_regular"
        title: "启用托盘图标"
        description: "在系统托盘中显示 Guardian 图标，点击可打开主窗口"

        Switch {
            checked: backend.config.tray_icon
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "tray_icon", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_alert_20_regular"
        title: "启用通知"
        description: "任务异常或更新可用时弹出通知"

        Switch {
            checked: backend.config.notification
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "notification", checked
            )
        }
    }

    Text {
        text: "高级"
        typography: Typography.BodyStrong
        Layout.topMargin: 16
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_bug_20_regular"
        title: "任务级异常处理方式"
        description: "非核心组件抛出未捕获异常时的处理策略"

        ComboBox {
            model: [
                { text: "静默记录日志并禁用任务", value: "silent_disable" },
                { text: "弹出通知并禁用任务", value: "popup" },
            ]
            textRole: "text"
            valueRole: "value"
            Component.onCompleted: {
                for (var i = 0; i < model.length; i++) {
                    if (model[i].value === backend.config.task_error_mode) {
                        currentIndex = i
                        break
                    }
                }
            }
            onActivated: backend.set_value(
                "config", "task_error_mode", model[currentIndex].value
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_bug_20_regular"
        title: "服务级异常处理方式"
        description: "核心组件崩溃时的处理策略（连续重启失败 5 次将静默退出）"

        ComboBox {
            model: [
                { text: "静默记录日志并重启", value: "silent_restart" },
                { text: "弹出通知并重启", value: "popup" },
            ]
            textRole: "text"
            valueRole: "value"
            Component.onCompleted: {
                for (var i = 0; i < model.length; i++) {
                    if (model[i].value === backend.config.service_error_mode) {
                        currentIndex = i
                        break
                    }
                }
            }
            onActivated: backend.set_value(
                "config", "service_error_mode", model[currentIndex].value
            )
        }
    }

    Text {
        text: "卸载"
        typography: Typography.BodyStrong
        Layout.topMargin: 16
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_delete_20_regular"
        title: "卸载 ClassIsland Guardian"
        description: "移除 Guardian 的所有文件和启动项（真的吗...?）"

        Button {
            text: "卸载"
            onClicked: confirmUninstall.open()
        }
    }

    // 卸载确认弹窗
    Dialog {
        id: confirmUninstall
        title: "确认卸载？"
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel

        Text {
            text: "卸载后将移除 Guardian 的所有文件、驱动和启动项。\n真的要继续吗...?"
            width: 320
            wrapMode: Text.WordWrap
        }

        onAccepted: backend.uninstall()
    }
}