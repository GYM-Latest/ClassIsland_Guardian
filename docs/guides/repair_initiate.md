# 修复启动 ClassIsland Guardian

> 欢迎！该文档将指引您在误关闭 `Windows 测试模式` 导致系统无法正常启动时，完成修复。

## 发生了什么

`ClassIsland Guardian` 的驱动级守护，会在系统最底层安装几个内核驱动来保护 `ClassIsland`。这些驱动没有微软官方签名，而 `Windows` 出于安全考虑，默认只允许加载“有签名”的驱动。

`测试模式`（`testsigning`）就是专门用来放行这类无签名驱动的开关。安装驱动级守护时，安装程序会自动打开这个开关。

如果你误把它关闭了，`Windows` 开机加载驱动时就会把这些无签名驱动 **全部拒载**。

而其中，`ClassIsland Guardian` 为了确保守护力度、防止保护被静默绕过，特意将自己注册成了 **系统关键驱动**——它在系统最早的启动阶段（引导阶段）就被加载，一旦缺失或加载失败，`Windows` 会判定系统关键组件损坏，直接拒绝启动。

于是便出现“无法加载操作系统”或“自动修复 无法修复你的电脑”的界面，系统再也进不去了。

> [!TIP]
> 别担心，你的系统并没有丝毫损坏，按照接下来的步骤即可完成修复。

## 修复前确认

当启动系统时，弹出类似以下界面而不是正常启动系统：

![无法加载操作系统，因为无法验证文件或者或其某个依赖项的签名](https://cdn.luogu.com.cn/upload/image_hosting/u7fu72yh.png)

![“自动修复” 无法修复你的电脑](https://cdn.luogu.com.cn/upload/image_hosting/fkrij4kv.png)

出现上述界面即说明驱动签名校验失败，请按以下步骤修复。

## 暂时修复并进入系统

两种界面对应两种进入方式：

**方式一：** 出现“无法加载操作系统”界面时，直接按 `F8` 进入 **启动设置** 界面。

**方式二：** 出现“自动修复 无法修复你的电脑”界面时，点击 **高级选项**，进入 **选择一个选项** 界面，再依次进入 **疑难解答 → 高级选项**：

![选择一个选项 界面](https://cdn.luogu.com.cn/upload/image_hosting/it0xkile.png)

![疑难解答 界面](https://cdn.luogu.com.cn/upload/image_hosting/tjs4279z.png)

![高级选项 页面](https://cdn.luogu.com.cn/upload/image_hosting/ypfll55b.png)

在 **高级选项** 中选择 **启动设置** 并点击 **重启**，进入启动设置界面：

![启动设置 界面](https://cdn.luogu.com.cn/upload/image_hosting/xpak09i3.png)

两种方式最终都会进入 **启动设置** 界面，按 **7**（或 **F7**）以 **禁用驱动程序强制签名** 模式启动（该模式仅本次生效）。

## 修复步骤

1. 以"禁用驱动程序强制签名"模式进入系统后，**以管理员身份** 打开 `powershell/cmd`。
2. 重新开启测试模式：

    ```powershell
    bcdedit /set testsigning on
    ```

3. 重启电脑。

## 彻底完成修复

重启后系统即可正常启动，`ClassIsland Guardian` 驱动级守护重新生效。

## 注意事项

- "禁用驱动程序强制签名"模式仅本次启动有效，重启后失效，因此必须执行步骤 2 重新开启测试模式。

## 预防

**绝对禁止** 关闭 `Windows 测试模式`（执行 `bcdedit /set testsigning off`）——驱动级守护依赖测试模式加载未签名驱动，关闭后系统将无法启动。
