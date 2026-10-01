import QtQuick
import QtQuick.Layouts
import RinUI

FluentPage {
    id: update
    title: {
        var s = backend.state.update_status
        var r = backend.state.latest_release
        var v = r ? r.tag_name : ""
        if (s === "checking")    return qsTr("正在检查更新")
        if (s === "available")   return qsTr("发现新版本：") + v
        if (s === "latest")      return qsTr("已是最新版本")
        if (s === "downloading") return qsTr("正在下载更新")
        if (s === "unziping")    return qsTr("正在解压")
        if (s === "waitreboot")  return qsTr("重启以完成更新")
        if (s === "error")       return qsTr("更新失败")
        return qsTr("更新")
    }


    ProgressBar {
        Layout.fillWidth: true
        visible: backend.state.update_status === "checking"
                    || backend.state.update_status === "downloading"
                    || backend.state.update_status === "unziping"
        indeterminate: backend.state.update_status !== "downloading"
        value: backend.state.update_total > 0
                ? backend.state.update_downloaded / backend.state.update_total
                : 0
    }

    Text {
        Layout.fillWidth: true
        visible: backend.state.update_status === "downloading"
        text: backend.state.update_downloaded + " / " + backend.state.update_total
        typography: Typography.Caption
        color: Theme.currentTheme.colors.textSecondaryColor
        horizontalAlignment: Text.AlignRight
    }

    Button {
        highlighted: backend.state.update_status === "available"
                    || backend.state.update_status === "waitreboot"
        visible: backend.state.update_status !== "checking"
                && backend.state.update_status !== "downloading"
                && backend.state.update_status !== "unziping"
                && backend.state.update_status !== "waitreboot"
        text: backend.state.update_status === "available" ? "更新到此版本" : "检查更新"
        onClicked: {
            var s = backend.state.update_status
            if (s === "available") backend.update()
            else                   backend.check_update()
        }
    }

    // 更新日志
    Text {
    Layout.fillWidth: true
    Layout.topMargin: 10
    text: {
        var r = backend.state.latest_release
        if (!r) return ""
        return r.body || "暂无更新说明"
    }
    wrapMode: Text.Wrap
    textFormat: Text.MarkdownText
    typography: Typography.Body
    color: Theme.currentTheme.colors.textColor
    }
}