import QtQuick
import QtQuick.Layouts
import RinUI

FluentPage {
    id: about
    title: qsTr("关于 ClassIsland Guardian")

    ColumnLayout {
        Layout.fillWidth: true
        Layout.topMargin: 20
        spacing: 10

        SettingCard {
            Layout.fillWidth: true
            title: qsTr("ClassIsland Guardian")
            description: qsTr("一款功能强大的 ClassIsland 守护工具。")
            icon.name: "ic_fluent_shield_20_regular"

            Text {
                text: backend.meta.version
                typography: Typography.BodyStrong
                color: Theme.currentTheme.colors.textSecondaryColor
            }
        }

        SettingExpander {
            Layout.fillWidth: true
            title: qsTr("常用链接")
            description: qsTr("相关资源与反馈渠道")
            icon.name: "ic_fluent_link_20_regular"

            SettingItem {
                title: qsTr("GitHub 仓库")
                description: qsTr("源代码、Issue、Release")
                actionIcon.name: "ic_fluent_open_20_regular"
                clickable: true
                onClicked: Qt.openUrlExternally("https://github.com/GYM-Latest/ClassIsland_Guardian")
            }

            SettingItem {
                title: qsTr("文档")
                description: qsTr("安装、配置与开发指南")
                actionIcon.name: "ic_fluent_open_20_regular"
                clickable: true
                onClicked: Qt.openUrlExternally("https://github.com/GYM-Latest/ClassIsland_Guardian/tree/main/docs")
            }

            SettingItem {
                title: qsTr("提交反馈")
                description: qsTr("报告 Bug 或建议新功能")
                actionIcon.name: "ic_fluent_open_20_regular"
                clickable: true
                onClicked: Qt.openUrlExternally("https://github.com/GYM-Latest/ClassIsland_Guardian/issues/new")
            }
        }

        SettingCard {
            Layout.fillWidth: true
            title: qsTr("开源许可证")
            description: qsTr("本项目基于 GPL-3.0 License 获得许可")
            icon.name: "ic_fluent_document_20_regular"

            Hyperlink {
                text: qsTr("查看许可证")
                openUrl: "https://www.gnu.org/licenses/gpl-3.0.html"
            }
        }

    SettingExpander {
        Layout.fillWidth: true
        title: qsTr("致谢")
        description: qsTr("感谢所有让这个项目存在的人")
        icon.name: "ic_fluent_heart_20_regular"

        SettingItem {
            ColumnLayout {
                spacing: 6

                Hyperlink {
                    text: qsTr("ClassIsland")
                    openUrl: "https://github.com/ClassIsland/ClassIsland"
                }
                Hyperlink {
                    text: qsTr("RinUI")
                    openUrl: "https://github.com/RinLit-233-shiroko/Rin-UI"
                }
            }
        }

        SettingItem {
            ColumnLayout {
                spacing: 6

                Hyperlink {
                    text: qsTr("智教联盟论坛")
                    openUrl: "https://forum.smart-teach.cn/"
                }
            }
        }

        SettingItem {
            ColumnLayout {
                spacing: 6

                Hyperlink {
                    text: qsTr("DeepSeek")
                    openUrl: "https://deepseek.com"
                }
                Hyperlink {
                    text: qsTr("洛谷云图床")
                    openUrl: "https://www.luogu.com.cn/image"
                }
                Hyperlink {
                    text: qsTr("热铁盒网页托管")
                    openUrl: "https://host-intro.retiehe.com/"
                }
            }
        }

        SettingItem {
            title: qsTr("所有贡献者与用户")
            description: qsTr("每一行代码、每一个 Issue、每一次讨论，都在让 CIG 变得更好")
        }

        SettingItem {
            title: qsTr("以及你")
            description: qsTr("让这个项目有了存在的意义")
        }
    }

        Text {
            Layout.fillWidth: true
            Layout.topMargin: 12
            Layout.bottomMargin: 24
            horizontalAlignment: Text.AlignHCenter
            typography: Typography.Caption
            color: Theme.currentTheme.colors.textSecondaryColor
            text: qsTr("CopyRight © 2026 GYM_Latest. 保留所有权利。")
        }
    }
}