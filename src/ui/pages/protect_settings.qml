import QtQuick
import QtQuick.Layouts
import RinUI

FluentPage {
    id: protectSettings
    title: "保护设置"

    Text {
        text: "基本设置"
        typography: Typography.BodyStrong
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_folder_20_regular"
        title: "ClassIsland 安装路径"
        description: backend.path.classisland_path || "未设置"

        TextField {
            placeholderText: "请输入路径"
            text: backend.path.classisland_path || ""
            onEditingFinished: backend.set_value("path", "classisland_path", text)
        }
    }

    Text {
        text: "进程保护"
        typography: Typography.BodyStrong
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_shield_error_20_regular"
        title: "自动查杀非安装目录下的 ClassIsland"
        description: "自动查杀路径不在安装路径下的 ClassIsland 进程"

        Switch {
            checked: backend.config.kill_non_install_ci
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "kill_non_install_ci", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_shield_task_20_regular"
        title: "自动查杀多余的 ClassIsland 实例"
        description: "自动查杀掉多开实例"

        Switch {
            checked: backend.config.kill_multi_ci
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "kill_multi_ci", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_shield_lock_20_regular"
        title: "以 SYSTEM 权限启动 ClassIsland"
        description: "请三思而后行，可能带来安全风险"

        Switch {
            checked: backend.config.launch_ci_as_system
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "launch_ci_as_system", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_window_shield_20_regular"
        title: "以 UIAccess 权限启动 ClassIsland"
        description: "请三思而后行，可能有兼容性问题（如任务栏图标异常）"

        Switch {
            checked: backend.config.launch_ci_as_uiaccess
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "launch_ci_as_uiaccess", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_arrow_sync_20_regular"
        title: "检测到 ClassIsland 卡死时自动重启"
        description: "ClassIsland 卡死后自动结束并重新拉起"

        Switch {
            checked: backend.config.auto_restart_frozen_ci
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "auto_restart_frozen_ci", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_arrow_exit_20_regular"
        title: "拉起失败后尝试逃逸式启动"
        description: "正常拉起失败时，尝试绕过可能存在的拦截"

        Switch {
            checked: backend.config.escape_launch_ci
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "escape_launch_ci", checked
            )
        }
    }

    Text {
        text: "快照系统"
        typography: Typography.BodyStrong
        Layout.topMargin: 16
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_history_20_regular"
        title: "拉起 ClassIsland 前先回滚快照"
        description: "会显著降低进程丢失时的响应速度，但能防止 ClassIsland 资源文件损坏"

        Switch {
            checked: backend.config.rollback_before_launch
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "rollback_before_launch", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_arrow_undo_20_regular"
        title: "拉起 ClassIsland 失败后回滚快照"
        description: "拉起失败时，从最新快照恢复 ClassIsland 目录"

        Switch {
            checked: backend.config.rollback_on_fail
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "rollback_on_fail", checked
            )
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon.name: "ic_fluent_bug_20_regular"
        title: "检测到 ClassIsland 崩溃时回滚快照"
        description: "ClassIsland 崩溃后自动从快照恢复"

        Switch {
            checked: backend.config.rollback_on_crash
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "rollback_on_crash", checked
            )
        }
    }

    SettingExpander {
        Layout.fillWidth: true
        icon.name: "ic_fluent_delete_20_regular"
        title: "自动清理快照"
        description: "定期清理旧快照，只保留最新的几个"

        action: Switch {
            checked: backend.config.auto_cleanup_snapshot
            text: ""
            checkedText: ""
            uncheckedText: ""
            onCheckedChanged: backend.set_value(
                "config", "auto_cleanup_snapshot", checked
            )
        }

        SettingItem {
            title: "最大保留自动生成快照数"
            description: "超过这个数量的旧自动生成快照会被自动删除，手动创建的快照不会被删除"

            SpinBox {
                from: 1
                to: 20
                value: backend.config.max_snapshot_count
                onValueChanged: backend.set_value(
                    "config", "max_snapshot_count", value
                )
            }
        }
    }

//    Text {
//        text: "其它"
//        typography: Typography.BodyStrong
//    }
//
//
//    SettingCard {
//        Layout.fillWidth: true
//        icon.name: "ic_fluent_puzzle_piece_20_regular"
//        title: "ClGProfessional 插件支持"
//        description: "需要先在 ClassIsland 中安装 CIGProfessional 插件（目前还是大饼）"
//
//        Switch {
//            checked: backend.config.cig_professional
//            onCheckedChanged: backend.set_value(
//                "config", "cig_professional", checked
//            )
//        }
//    }
}