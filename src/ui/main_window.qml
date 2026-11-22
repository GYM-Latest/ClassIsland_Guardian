import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentWindow {
    id: mainwindow
    visible: true
    title: backend.config.debug_mode === true ? qsTr("ClassIsland Guardian " + "("+ backend.meta.version + ") " + "(DebugMode)")
     : backend.config.debug_mode === false ? qsTr("ClassIsland Guardian " + "("+ backend.meta.version + ")")
     : "ClassIsland Guardian"

    width: 1400
    height: 800
    minimumWidth: 550
    minimumHeight: 400

    navigationItems: [
        {
            title: "保护控制",
            page: Qt.resolvedUrl("pages/dashboard.qml"),
            icon: "ic_fluent_home_20_regular",
            position: Position.Top
        },
        {
            title: "快照管理",
            page: Qt.resolvedUrl("pages/snapshot.qml"),
            icon: "ic_fluent_save_20_regular"
        },
        {
            title: "保护设置",
            page: Qt.resolvedUrl("pages/protect_settings.qml"),
            icon: "ic_fluent_shield_20_regular"
        },   
        {
            title: "应用设置",
            page: Qt.resolvedUrl("pages/app_settings.qml"),
            icon: "ic_fluent_settings_20_regular"
        },
        {
            title: "更新",
            page: Qt.resolvedUrl("pages/update.qml"),
            icon: "ic_fluent_arrow_circle_up_20_regular"
        },
        {
            title: "关于",
            page: Qt.resolvedUrl("pages/about.qml"),
            icon: "ic_fluent_info_20_regular",
            position: Position.Bottom
        }
    ]

    Component.onCompleted: {
        if (backend.config.debug_mode) {
            floatLayer.createInfoBar({
                severity: Severity.Warning,
                position: Position.BottomRight,
                timeout: 20000,
                closable: true,
                title: qsTr("调试模式已启用"),
                text: qsTr("正在以调试模式运行，某些功能可能无法正常使用。")
            })
        }
    }
}