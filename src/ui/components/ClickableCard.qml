import QtQuick
import RinUI

Item {
    id: root
    implicitHeight: card.implicitHeight

    property alias iconName: card.icon.name
    property alias title: card.title
    property alias description: card.description
    signal clicked()

    SettingCard {
        id: card
        width: root.width
        icon.name: root.iconName
        title: root.title
        description: root.description
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }

    Rectangle {
        anchors.fill: parent
        radius: Theme.currentTheme.appearance.windowRadius
        color: "black"
        opacity: mouseArea.pressed ? 0.08 : (mouseArea.containsMouse ? 0.04 : 0)
        enabled: false
        Behavior on opacity { NumberAnimation { duration: 100 } }
    }
}