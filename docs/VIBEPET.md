# VibeCoding Pet v0.1.0｜架构、隐私与验收

## 目标与能力边界

VibeCoding Pet 是一个可运行的 Rust 虚拟宠物 MVP。用户可通过网页查看 Agent 生命周期相关表情变化、活力值、快乐值、等级与最近事件；CodeArts CLI/OpenCode Hook 为**需要用户主动安装的可选适配器**。未安装时，可以通过明确标注的 `demo` 模式试玩。

**它不是自动代码修复器，不读取代码、提示词、密钥或工具输出，不默认调用云模型**。宠物经验是娱乐指标，不代表开发者生产力或代码质量。

## 技术架构

```text
  CodeArts CLI Hooks      OpenCode Plugin      用户 demo/手动事件
          │                    │                    │
          └────────────────────┴────────────────────┘
                               ▼
        127.0.0.1:7878  POST /api/event（source、kind）
                               │
                 严格的事件白名单与跨站校验
                               ▼
                      Rust PetState 内存态
                     /                   \
             GET /api/state            GET / (HTML/CSS/JS)
                     \                   /
                         网页交互动画
```

- `src/pet.rs`：无第三方依赖、确定性 Rust 状态机，记录最近最多 16 条事件，不保留自由文本。
- `src/bin/vibepet.rs`：零依赖 Rust HTTP/CLI 服务，只监听 IPv4 127.0.0.1。
- `skills/vibecoding-pet/web/`：响应式前端，使用内嵌资源，不依赖 CDN。
- `skills/vibecoding-pet/adapters/`：仅在用户复制安装后订阅工具事件。
- `tools/vibepet_dist.py`：可重复构建普通 ZIP 与 CodeArts 结构 ZIP，含 SHA-256 清单及大小限制。

## 官方 Hook 接口依据

- [CodeArts CLI Hooks 文档](https://support.huaweicloud.com/usermanual-cli/codeartsagent_cli_0018.html)：项目级 `.codeartsdoer/plugin(s)`，事件包括 `chat.message`、`tool.execute.before/after`、`chat.error`、`chat.finished`、`user.approval`。
- [OpenCode 官方 Plugins 文档](https://docs.opencode.ai/docs/plugins/)：项目级 `.opencode/plugins/`，事件包括 `session.created`、`session.status`、`session.error`、`tool.execute.before/after`。

适配器依照官方接口编写并有 Node Mock 测试，**但真实 CodeArts/OpenCode 进程中的 Hook 投递还需要额外联调**。 `chat.finished`、`session.idle` 映射为休息状态，不自动宣称任务成功。

## 数据与安全

- 严格白名单：来源 `codearts|opencode|demo|manual`、类型 `session_start|thinking|tool_start|tool_done|approval_wait|task_success|task_failure|session_idle|feed|cheer`。
- 仅在本地进程内存保留心情、活力、快乐、经验、等级与 16 条事件类型；没有长期记录或数据库；退出即清零。
- HTTP 限制 Host、Origin、跨站浏览器请求、最大 8 KiB 请求和 1 KiB POST 内容，拒绝额外的 prompt/code 字段。
- 固定 CSP，不加载远程脚本或样式；Hook 连接最多等待 300ms，异常静默处理。
- 本机来源声明不是身份签名：loopback 上的其他程序理论上也可以模拟 Agent 来源，不能把标签当作安全审计证据。
- 插件会写入用户项目文件夹，**必须获得同意之后才能复制安装**；默认 Skill 不执行插件安装。

## 操作验证

```bash
cargo run --bin vibepet -- serve
# 浏览器 http://127.0.0.1:7878
```

新终端运行：

```bash
cargo run --bin vibepet -- emit tool_start --source demo
cargo run --bin vibepet -- status
```

正式 Hook 验证应让 CodeArts/OpenCode 真正启动并执行一次工具调用，在网页中看到对应来源与忙碌状态。Demo 事件不能替代这个验收。

## 自动化门槛

1. Linux、Windows、macOS：`cargo fmt` / Clippy / Rust 单元测试。
2. Node：Hook 最小权限、敏感信息不透传、无服务时不阻断 Agent 的模拟测试。
3. Python：普通/CodeArts ZIP 安全与哈希、确定性打包、完整文件清单。
4. Python：启动真实 Rust 本地服务，校验网页、REST、CLI、Host/Origin 与隐私边界。
5. GitHub Actions 产出平台专用压缩包；仅打 `vibepet/v*` 标签才正式创建 GitHub Release。

**v0.1.0 不包含** ESP32 硬件、进度持久化、开放局域网服务、生产环境账号连接或小红书市场上架。这些会在后续版本独立验收。
