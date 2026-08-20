# ClassIsland Guardian
> ⌜念念不忘，必有回响⌟

`ClassIsland Guardian` 是一款适用于 `Windows` 平台的，功能强大的 `ClassIsland` 守护工具。

有关 `ClassIsland` 的信息，敬请参阅 [
ClassIsland Github](https://github.com/ClassIsland/ClassIsland)。

> [!CAUTION] 
> **项目正处于早期测试阶段，稳定性欠佳。**
>
> 目前已实现绝大多数功能，但该项目 **缺少完整详细测试，大量操作尚未文档化**。
>
> 请谨慎部署，如有必要，建议在**虚拟机**中部署。
>
> **请勿在生产环境部署！** 如果在使用过程中遇到Bug，欢迎提交Issue。

## 功能

### 应用层守护
- 监控 `ClassIsland.Desktop.exe` 进程状态，异常退出时自动拉起。
- 支持手动创建、列出和恢复 `ClassIsland` 目录的历史快照，检测到目录异常时自动回滚。
- 映像劫持对抗：启动前自动检测并清理针对 `ClassIsland` 进程的恶意 Debugger 劫持项，确保程序不被劫持或禁用。
- 逃逸式启动：监测安全软件或者权限软件对 'ClassIsland' 的拦截，并尝试绕过。
- 完整的操作日志记录，便于排查问题。

### 驱动级守护

> [!WARNING]
> 驱动级守护不支持在开启了 `Secure Boot` 的设备上使用。且需开启 `测试模式` 。

- 保护 `ClassIsland Guardian` 程序本体与预启动修复文件不受破坏。
- 阻止攻击者结束 `ClassIsland` 与 `ClassIsland Guardian` 进程。

### 预启动修复

> [!WARNING]
> 预启动修复不支持在系统磁盘分区上开启了 `Bitlocker` 的设备上使用。

- 独立于 Windows 系统的预启动环境，不依赖任何驱动。
- 在 Windows 启动之前抢先运行。
- 自动检测  `ClassIsland Guardian` 是否损坏，发现损坏时自动从快照完成检查和修复。

### 其他
- 通过完善的命令行菜单配置保护策略。
- 支持密码锁定，保护保护策略不受篡改。
- 还支持更多功能……

## 软件截图/短宣传片
![config.exe的配置页面](https://cdn.luogu.com.cn/upload/image_hosting/0wmadd6q.png)

[观看短宣传片 ->](https://www.bilibili.com/video/BV1DcgV6LEF7/)

## 使用

> [!IMPORTANT]  
> **详细安装与配置说明请参阅 [ClassIsland Guardian 文档](docs/guides/first_install.md)。**

### 系统要求：

- Windows 10/11 x64。
- 管理员权限。
- 建议在虚拟机或测试环境中先行验证。

### 下载与安装

- [GitHub Releases](https://github.com/SXSJGYM/ClassIsland_Guardian/releases)

## 开发/编译
> [!IMPORTANT]  
> **详细的开发环境配置与编译指南请参阅 [ClassIsland Guardian 开发文档](_)。**

### 项目结构

- `src/`：Ring3 用户态 Python 源码。
- `drivers/`：Ring0 内核驱动源码。
- `launcher/`: Ring3 用户态启动器源码。


## 社区衍生项目

> [!NOTE]
> 以下项目为社区爱好者独立维护，与 `GYM-Latest/ClassIsland_Guardian` 无官方关联。  
> 如有 Bug 或使用问题，请直接前往对应仓库反馈，谢谢。

- **[HickoryTrail/ClassIsland_Guardian_Sharp](https://github.com/HickoryTrail/ClassIsland_Guardian_Sharp)**: 
   社区使用 `C#` 重写的版本，采用 `.NET 10 NativeAOT 技术栈` 。  
  > 该项目由社区开发者 100% 使用 `VibeCoding` 完成重构，尚未经过详细测试，仅供学习参考。
  

## 许可证

本项目采用 [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html) 许可证。有关详细信息，敬请参见 [LICENCE.txt](LICENCE.txt) 。


## 致谢

1. 感谢 [ClassIsland](https://github.com/ClassIsland/ClassIsland) 本体——这个项目因你而生，也因你而不断进化。
2. 感谢我的班主任张老师——对我和多媒体的“严加调教”促生了这个项目，并推动它不断完善。
3. 感谢所有贡献者——每一行代码、每一个 Issue、每一次讨论，都在让 CIG 变得更好。
4. 感谢 [DeepSeek](https://deepseek.com)——在无数个卡壳的深夜提供思路与陪伴。
5. 感谢 [SignPath Foundation](https://signpath.org)——为开源项目提供免费的代码签名服务，让驱动能够被信任。
6. 感谢 [热铁盒网页托管](https://host-intro.retiehe.com/)——提供高速且价格友好的网站托管服务。
7. 感谢 [洛谷云图床](https://www.luogu.com.cn/image)——稳定的图床支持，让文档和 README 得以清晰呈现。
8. 感谢你——让这个项目有了存在的意义。
9. 磅十五便士。