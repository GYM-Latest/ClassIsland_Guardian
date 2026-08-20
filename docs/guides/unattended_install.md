# 无人值守安装 ClassIsland Guardian

> 当在教室多媒体等管理严格的环境中安装 `ClassIsland Guardian` 时，使用无人值守安装能够有效降低被班主任发现的几率，最大程度降低被班主任一肘肘飞的概率。下面将指导你使用此功能。

## 适用场景

- **多台机器批量部署**：机房、实验室、班级多媒体等需要同时安装多台电脑的场景。
- **管理严格的电脑**：班级多媒体、公用电脑等不便人工操作安装向导的场景，可以提前生成配置，将安装包与配置一并拷入（U 盘、教师端下发均可），运行一次 `setup.exe` 即自动装好，全程无需交互，实现隐蔽安装。

## 工作原理

1. 提前生成（或手写）一份配置文件 `install_config.json`，放在 `setup.exe` 同目录下。
2. 目标机器上以管理员身份运行 `setup.exe`，安装程序检测到配置文件后自动开始安装。
3. 若配置了驱动级守护（`driver_protection: true`），安装程序会 **自动开启测试模式并重启**，重启后自动继续完成安装。
4. 配置文件 **永远不会被安装程序修改或删除**，可反复用于多台机器部署。

## 准备工作

> [!CAUTION]
> 当前 `ClassIsland Guardian` 仍处在 **早期测试阶段** 。强烈建议在 **虚拟机** 里进行测试与安装。如果遇到 `Bug` ，欢迎创建 `Issue` 反馈。

> [!TIP]
> 无人值守安装要求目标机器已安装 `ClassIsland`，安装程序本身不会帮你安装它。可以访问 [https://www.classisland.tech/](https://www.classisland.tech/) 下载 `ClassIsland`。

> [!CAUTION]
> `ClassIsland_Guardian` 与 `ClassIsland` 的部分插件 **不兼容**，贸然使用会造成不可预见的风险，请在安装前检查 [不兼容插件名单](incompatible_plugin.md) 并删除相关插件。

### 环境准备

1. `ClassIsland Guardian` 需要 `Windows 10 x64` 及以上系统。
2. 无人值守安装 **无需手动开启测试模式**：若配置了驱动级守护，安装程序会自动开启并重启；仅应用层守护则完全不需要测试模式。
3. 部分杀软可能会对 `ClassIsland Guardian` 误报，建议在安装前 **关闭所有杀软**。

### 获取配置文件

#### 方式一：在任意机器上使用向导生成

在任意一台机器上（甚至可以是部署目标机器本身）运行 `setup.exe`，在起始页面输入 `c`：

```text
ClassIsland Guardian Installer
版本 v0.3.0 | Mahiro
欢迎，该配置向导会帮你完成 ClassIsland Guardian 的安装与配置 ~

要开始安装，请输入 y 再按 ENTER
要生成无人值守安装配置文件，请输入 c 再按 ENTER
要退出向导，请输入 n 再按 ENTER
>c
```

随后按向导提示依次填写 `ClassIsland` 路径、管理密码与守护方式（应用层 / 驱动级）。填写完成后，向导会在 `setup.exe` 同目录生成 `install_config.json`：

```text
已经生成无人值守安装配置文件（JSON）~

配置文件包含 ClassIsland 路径、管理密码与驱动级守护选项，
其中密码为明文，请妥善保管，不要泄露给他人哦 ~

按回车关闭安装向导......
```

#### 方式二：手动编写

配置文件为 `JSON` 格式，编码为 `UTF-8`，示例：

```json
{
    "version": "v0.3.0",
    "classisland_path": "D:\\classisland",
    "password": "***",
    "driver_protection": false
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `version` | string | 生成配置时使用的安装程序版本，手动编写时可省略 |
| `classisland_path` | string | `ClassIsland` 的安装目录（必填） |
| `password` | string | 管理密码，**明文存储**；留空 `""` 则不启用密码保护 |
| `driver_protection` | bool | `false` 仅应用层守护；`true` 安装驱动级守护（会自动开启测试模式并重启） |

> [!WARNING]
> 配置文件中的密码为 **明文** 存储，请妥善保管，切勿泄露给他人或提交到公开仓库。

## 安装

1. 将 **整个安装包目录** 复制到目标机器（推荐直接拷贝 `.zip` 压缩包到目标机器后再解压），确保以下文件/目录位于 **同一目录**：

    ```text
    setup.exe            # 安装程序
    appdata\             # 运行时资源（依赖）
    drivers\             # 内核驱动（依赖）
    recovery\            # 预启动修复环境（依赖）
    install_config.json  # 无人值守配置文件
    ```

    > [!WARNING]
    > 安装程序依赖同目录的 `appdata/`、`drivers/`、`recovery/` 资源，**只复制 `setup.exe` 和配置文件会导致安装失败**。

2. 以管理员身份运行 `setup.exe`（或在管理员 `powershell/cmd` 中启动，便于捕获报错堆栈）。
3. 等待安装自动完成，无需任何操作。若配置了驱动级守护（`driver_protection: true`），安装过程中会自动开启测试模式并重启，重启后自动续装完成。

## 注意事项

- 安装完成后 `install_config.json` **会被保留**，可在其他机器上重复使用；再次运行 `setup.exe` 会重新执行安装。
- 驱动级守护安装中途失败（如测试模式开启失败）时，程序会退出且不会破坏配置，可再次运行重试。
- 驱动级守护安装过程中程序会创建一个临时状态文件 `install_temp.json`（同样位于 `setup.exe` 同目录），由安装程序自行管理，安装完成后自动删除，请勿手动修改或删除。
- 若配置了驱动级守护，安装完成后目标机器将处于 Windows 测试模式（`testsigning on`）以加载未签名驱动。
