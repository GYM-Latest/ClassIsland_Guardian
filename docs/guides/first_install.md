# 安装 ClassIsland Guardian

> 欢迎！该文档将指引您在计算机上安装 `ClassIsland Guardian`。

## 准备工作

> [!CAUTION]
> 当前 `ClassIsland Guardian` 仍处在 **早期测试阶段** 。强烈建议在 **虚拟机** 里进行测试与安装。如果遇到 `Bug` ，欢迎创建 `Issue` 反馈。

> [!TIP]
> `ClassIsland Guardian` 是 `ClassIsland` 的配套应用程序，如您未安装 `ClassIsland` ,可以访问 [https://www.classisland.tech/](https://www.classisland.tech/) 下载 `ClassIsland`

> [!CAUTION]
> `ClassIsland_Guardian` 与 `ClassIsland` 的部分插件 **不兼容**，贸然使用会造成不可预见的风险，请在安装前检查 [不兼容插件名单](incompatible_plugin.md) 并删除相关插件。

> [!NOTE]
> 需要在多台计算机上安装？或者需要在班级多媒体上隐蔽安装？
> 该项目支持 [无人值守安装](unattended_install.md) 。

### 环境准备

1. `ClassIsland Guardian` 需要 `Windows 10 x64` 及以上系统。
2. 安装程序会按需自动开启 `测试模式`：安装驱动级守护时自动开启并重启，仅应用层守护则无需测试模式。**无需手动执行 `bcdedit /set testsigning on`。**
3. 部分杀软可能会对 `ClassIsland Guardian` 误报，建议在安装前 **关闭所有杀软**。

## 安装 

1. 前往 [Github-release 页面](https://github.com/GYM-Latest/ClassIsland_Guardian/releases) 下载最新发行版。
2. 解压下载到的 `.zip` 包到一个 **独立目录**。
3. **以管理员权限** 运行 `powershell/cmd`，并在其中启动 `setup.exe`。这样做是为了在 setup 报错退出时方便捕获到其堆栈。
4. 开始安装：

    ```text
    ClassIsland Guardian Installer
    版本 v0.3.0 | Mahiro
    欢迎，该配置向导会帮你完成 ClassIsland Guardian 的安装与配置 ~

    要开始安装，请输入 y 再按 ENTER
    要生成无人值守安装配置文件，请输入 c 再按 ENTER
    要退出向导，请输入 n 再按 ENTER
    >
    ```

    按 `y` 并回车，进入下一步。

5. 输入 `ClassIsland` 的路径：

    ```text
    请输入 ClassIsland 的路径 ~
    输好后按 ENTER 就好 ~
    >D:\classisland
    ```

    安装程序会尝试自动识别 `ClassIsland` 的安装路径，如果识别失败，请手动填写 **正确的** 目录。

    回车，进入下一步。

6. 设置管理密码：

    ```text
    请设置管理密码 ~（留空则不启用）

    为安全起见，输入不会显示出来哦
    >
    ```

    建议输入一个密码以提升保护力度。为了安全考虑，输入密码时不会有任何回显反馈。**务必牢记密码，没有找回渠道。**

    输入密码后将会要求确认密码，将刚刚输入的密码照原样重新输入即可：

    ```text
    确认密码
    >
    ```

    回车，进入下一步。

7. 选择守护方式：

    ```text
    是否安装驱动级守护？

    驱动级守护可以阻止攻击者结束 ClassIsland 与守护进程，
    将会自动开启 Windows 测试模式并重启以加载未签名驱动。
    输入 y 安装驱动级守护，输入 n 仅使用应用层守护
    >
    ```

    - 输入 `n`：仅应用层守护，无需测试模式，**不会自动重启**。
    - 输入 `y`：驱动级守护，安装程序会 **自动开启测试模式** 并在安装开始后重启电脑，重启后自动继续安装。

8. 确认安装：

    ```text
    所有配置都填好啦 ~

    输入 install 再按 ENTER 就可以开始安装了
    安装过程中 ClassIsland 会稍微歇一下下 ~
    如果安装过程中杀软的大手发力了，麻烦关一下，非常感谢！ ~
    >
    ```

    输入 `install` 并回车以开始安装。

    - **应用层守护**（步骤 7 输入 `n`）：安装过程需 2~3 分钟，请耐心等待。
    - **驱动级守护**（步骤 7 输入 `y`）：安装程序自动开启 `Windows 测试模式` 并创建自启动任务，随后提示重启：

      ```text
      安装程序需要重启才能继续，将在倒计时结束后重启 ~
      ```

      电脑重启后，安装程序会 **自动继续** 完成安装，无需任何操作。

9. 完成安装

    看到

    ```text
    安装完成，重启后生效 ~
    ```

    时，说明安装完成。此时，重新启动电脑 `ClassIsland Guardian` 方可生效。

> [!CAUTION]
> 若安装了驱动级守护，安装完成后系统将保持在 `Windows 测试模式`（`testsigning on`）以加载未签名驱动；
> 
> **绝对禁止** 关闭 `Windows 测试模式`，这会导致 `Windows` 无法正常启动。
>
> 如果你已经失误关闭了 `Windows 测试模式` 并且 `Windows` 已经无法正常启动，请参见 [此文档](/docs/guides/repair_initiate.md)
