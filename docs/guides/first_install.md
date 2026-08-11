# 安装 ClassIsland Guardian

> 欢迎！该文档将指引您在计算机上安装 `ClassIsland Guardian`。

## 准备工作

> [!CAUTION]
> 当前 `ClassIsland Guardian` 仍处在 **早期测试阶段** 。强烈建议在 **虚拟机** 里进行测试与安装。如果遇到 `Bug` ，欢迎创建 `Issue` 反馈。

> [!TIP]
> `ClassIsland Guardian` 是 `ClassIsland` 的配套应用程序，如您未安装 `ClassIsland` ,可以访问 [https://www.classisland.tech/](https://www.classisland.tech/) 下载 `ClassIsland`

### 环境准备

1. `ClassIsland Guardian` 需要 `Windows 10 x64` 及以上系统。
2. 在开始安装前，请确保开启了 `测试模式` 。

    ```powershell
    # 在管理员 Cmd/Powershell 中执行（需重启后生效）
    bcdedit /set testsigning on
    ```

3. 部分杀软可能会对 `ClassIsland Guardian` 误报，建议在安装前 **关闭所有杀软**

### 安装

1. 前往 [Github-release 页面](https://github.com/SXSJGYM/ClassIsland_Guardian/releases) 下载最新发行版。
2. 解压下载到的 `.zip` 包到一个 **独立目录**。
3. **以管理员权限** 运行 `powershell/cmd`。并在 `powershell/cmd` 中启动 `setup.exe`。这样做是为了在 setup 报错退出时方便捕获到其堆栈。
4. 开始安装：

    ```text
    ClassIsland Guardian Installer
    版本 0.20260726.1 | Mahiro
    欢迎，该配置向导会帮你完成 ClassIsland Guardian 的安装与配置 ~

    要开始，请输入 y 再按 ENTER
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

7. 确认安装：

    ```text
    所有配置都填好啦 ~

    输入 install 再按 ENTER 就可以开始安装了
    安装过程中 ClassIsland 会稍微歇一下下 ~
    如果安装过程中杀软的大手发力了，麻烦关一下，非常感谢！ ~
    >
    ```

    输入 `install` 并回车以开始安装。

    安装过程时需 2~3 分钟，请耐心等待。

8. 完成安装

    当看到
    ``` text
    安装完成，重启后生效 ~
    ```
    时，说明安装完成。
    
    此时，重新启动电脑 `ClassIsland Guardian` 方可生效