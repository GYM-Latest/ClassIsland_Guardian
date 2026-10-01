import QtQuick
import QtQuick.Layouts
import RinUI
import "../components"

FluentPage {
    id: dashboard
    title: backend.config.protect_state === "running" ? qsTr("保护运行中 ~")
     : backend.config.protect_state === "stop"    ? qsTr("保护已停止")
     : backend.config.protect_state === "tempstop" ? qsTr("保护暂停")
     : "未知状态"

    ColumnLayout {
        Layout.fillWidth: true
        Layout.topMargin: 20
        spacing: 10

        Text {
            text: qsTr("保护控制")
            typography: Typography.BodyLarge
        }

        ClickableCard {
            Layout.fillWidth: true
            visible: backend.config.protect_state === "running"
            iconName: "ic_fluent_pause_20_regular"
            title: qsTr("暂停保护")
            description: qsTr("暂时停止保护，重启后自动恢复")
            onClicked: confirmTempStop.open()
        }

        ClickableCard {
            Layout.fillWidth: true
            visible: backend.config.protect_state === "running"
            iconName: "ic_fluent_dismiss_20_regular"
            title: qsTr("停止保护")
            description: qsTr("停止保护，需要手动恢复")
            onClicked: confirmStop.open()
        }

        ClickableCard {
            Layout.fillWidth: true
            visible: backend.config.protect_state === "stop" || backend.config.protect_state === "tempstop"
            iconName: "ic_fluent_play_20_regular"
            title: qsTr("恢复保护")
            description: qsTr("重新启用守护")
            onClicked: backend.resume_protection()
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        Layout.topMargin: 24
        spacing: 10

        Text {
            text: qsTr("快捷操作")
            typography: Typography.BodyLarge
        }

        ClickableCard {
            Layout.fillWidth: true
            iconName: "ic_fluent_arrow_sync_20_regular"
            title: qsTr("重启 ClassIsland")
            description: qsTr("强制重启 ClassIsland 进程，可用于卡死恢复")
            onClicked: backend.restart_ci()
        }
    }

    Dialog {
        id: confirmStop
        title: qsTr("确认停止保护？")
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel

        Text {
            text: qsTr("停止保护后，ClassIsland 将不再受到任何守护。\n你确定要继续吗？")
            width: 320
            wrapMode: Text.WordWrap
        }

        onAccepted: backend.stop_protection()
    }

    Dialog {
        id: confirmTempStop
        title: qsTr("确认暂停保护？")
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel

        Text {
            text: qsTr("暂停保护后，ClassIsland 将不再受到任何守护，重启后守护将自动恢复。\n你确定要继续吗？")
            width: 320
            wrapMode: Text.WordWrap
        }

        onAccepted: backend.temp_stop_protection()
    }

    Connections {
        target: backend

        function onShowTransition() {
            waitingDialog.open()
        }

        function onHideTransition() {
            waitingDialog.close()
        }
    }

    Dialog {
        id: waitingDialog
        title: (
            backend.config.protect_state === "stop"    ? qsTr("正在停止保护")
        : backend.config.protect_state === "tempstop" ? qsTr("正在暂停保护")
        : qsTr("正在处理")
        )
        modal: true
        standardButtons: Dialog.NoButton 

        ColumnLayout {
            spacing: 16

            Text {
                text: "等待所有守护任务结束..."
                Layout.fillWidth: true
            }

            ProgressBar {
                id: progressBar
                Layout.fillWidth: true
                indeterminate: true 
            }
        }
}
}