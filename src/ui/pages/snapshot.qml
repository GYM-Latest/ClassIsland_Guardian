import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

FluentPage {
    id: snapshotPage
    title: "快照管理"

    function formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    ListModel {
        id: snapshotModel
    }

    function refreshSnapshots() {
        snapshotModel.clear()
        const snapshots = backend.get_snapshot_list()
        for (let i = 0; i < snapshots.length; i++) {
            snapshotModel.append(snapshots[i])
        }
    }

    Component.onCompleted: refreshSnapshots()

    onVisibleChanged: {
        if (visible)
            refreshSnapshots()
    }

    RowLayout {
        Layout.fillWidth: true

        Text{
            text: "快照列表"
            typography: Typography.Subtitle
            Layout.fillWidth: true
        }

        Button {
            text: "拍摄新快照"
            icon.name: "ic_fluent_camera_20_regular"
            highlighted: true
            onClicked: {
                createDialog.open()
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8

        Repeater {
            model: snapshotModel

            delegate: SettingCard {
                Layout.fillWidth: true

                icon.name: "ic_fluent_folder_20_regular"

                title: model.name
                description: model.time + "  ·  " + formatSize(model.size)

                RowLayout {
                    spacing: 8
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight

                    Button {
                        icon.name: "ic_fluent_arrow_undo_20_regular"
                        flat: true
                        onClicked: backend.restore_snapshot(model.name)

                        ToolTip.text: "恢复到此快照"
                        ToolTip.visible: hovered
                    }

                    Button {
                        icon.name: "ic_fluent_delete_20_regular"
                        flat: true
                        onClicked: backend.remove_snapshot(model.name)

                        ToolTip.text: "删除此快照"
                        ToolTip.visible: hovered
                    }
                }
            }
        }
    }

    Text {
        Layout.fillWidth: true
        visible: snapshotModel.count === 0
        text: "暂无快照，点击右上角「拍摄新快照」创建一个。"
        typography: Typography.Body
    }

    Dialog {
        id: createDialog
        title: "拍摄新快照"
        modal: true
        anchors.centerIn: Overlay.overlay
        standardButtons: Dialog.Ok | Dialog.Cancel

        ColumnLayout {
            spacing: 16
            Text {
                text: "请输入备注信息（可以为空）："
            }
            TextField {
                id: remarkInput
                Layout.preferredWidth: 300
                placeholderText: "例如：安装新插件前"
            }
        }

        onAccepted: {
            let remark = remarkInput.text.trim()
            remarkInput.text = ""
            backend.create_snapshot(remark)
        }
    }

    Dialog {
        id: deleteDialog
        title: "删除快照"
        modal: true
        anchors.centerIn: Overlay.overlay
        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            remarkInput.text = ""
            backend.delete_snapshot(remark)
        }
    }

    Connections {
        target: backend

        function onShowTransition() {
            waitingDialog.open()
        }

        function onHideTransition() {
            waitingDialog.close()
            refreshSnapshots()
        }
    }

    Dialog {
        id: waitingDialog
        title: (
            backend.state.snapshot_state === "create" ? qsTr("正在拍摄快照")
        : backend.state.snapshot_state === "remove" ? qsTr("正在删除快照")
        : backend.state.snapshot_state === "restore" ? qsTr("正在恢复快照")
        : qsTr("正在处理")
        )
        modal: true
        standardButtons: Dialog.NoButton
        footer: Item { height: 0 }
        closePolicy: Popup.NoAutoClose

        ColumnLayout {
            spacing: 16

            ProgressBar {
                Layout.fillWidth: true
                value: backend.state.snapshot_create_total > 0
                    ? (backend.state.snapshot_create_current / backend.state.snapshot_create_total)
                    : 0
                indeterminate: (
                    backend.state.snapshot_state === "create" ? false
                : true
                )
            }

            Text {
                text: (backend.state.snapshot_create_total > 0)
                    ? `${backend.state.snapshot_create_current} / ${backend.state.snapshot_create_total}`
                    : "正在获取文件列表..."
                Layout.fillWidth: true
                visible: backend.state.snapshot_state === "create"
            }
        }
    }
}