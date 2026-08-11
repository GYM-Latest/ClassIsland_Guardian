## 不兼容插件名单

为确保 `ClassIsland_Guardian` 正常工作，以下插件/工具请勿同时启用：

### 1. ClassIslandHide

- **原因**  
  该插件通过“自复制启动”方式将 ClassIsland 进程名修改为随机字符串，导致 `ClassIsland Guardian` 基于固定进程名的监控逻辑无法识别目标进程。

- **影响**  
  `ClassIsland Guardian` 的进程守护功能 **完全失效**，且会引发更多严重问题，如：`ClassIsland` 将被不断启动，无法正常工作。

- **建议操作**  
  **二选一**：
  - `ClassIsland Guardian` 已内置 **随机进程名逃逸启动**，可以直接使用此功能，无需配置。
  - 如需保留 `ClassIslandHide` 的窗口标题伪装功能，请 **禁用 Guardian 的进程守护功能**，避免两者冲突。

---

> **注意**：此名单会持续更新。如发现其他不兼容插件，欢迎提交 [Issue](../../issues) 补充。