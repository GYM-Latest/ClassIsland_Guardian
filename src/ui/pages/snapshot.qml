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

    ListView {
    spacing: 8
    width: parent.width
    height: contentHeight
    clip: true

        // 测试数据
        model: ListModel {
            ListElement { name: "snapshot_2026-11-14.zip"; time: "2026-11-14 10:00" }
            ListElement { name: "snapshot_2026-11-13.zip"; time: "2026-11-13 18:30" }
        }

            delegate: SettingCard {
            width: ListView.view.width
            
            icon.name: "ic_fluent_folder_20_regular" 
            
            title: model.name
            description: model.time

            RowLayout {
                spacing: 8
                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                
                Button {
                    icon.name: "ic_fluent_arrow_undo_20_regular"
                    flat: true
                    onClicked: console.log("恢复:", model.name)
                    
                    ToolTip.text: "恢复到此快照"
                    ToolTip.visible: hovered
                }
                
                Button {
                    icon.name: "ic_fluent_delete_20_regular"
                    flat: true
                    onClicked: console.log("删除:", model.name)
                    
                    ToolTip.text: "删除此快照"
                    ToolTip.visible: hovered
                }
            }
        }
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
        }
    }

    Dialog {
        id: waitingDialog
        title: "正在拍摄快照"
        modal: true
        standardButtons: Dialog.NoButton 
        closePolicy: Popup.NoAutoClose

        ColumnLayout {
            spacing: 16

            ProgressBar {
                Layout.fillWidth: true
                value: backend.state.snapshot_total > 0 ? (backend.state.snapshot_current / backend.state.snapshot_total) : 0
            }

            Text {
                    text: (backend.state.snapshot_total > 0) 
            ? `${backend.state.snapshot_current} / ${backend.state.snapshot_total}` 
            : "正在获取文件列表..."
                Layout.fillWidth: true
            }
        }
    }
}