# VibeCoding Pet v0.1.0 · 粒粒的编程宇宙

> 你写代码，粒粒负责为每个小小进步欢呼。一个 Rust 原生、网页可视化、默认离线且无需 API Key 的 AI 编程宠物。

**当前阶段：可运行的最小完整闭环，还未在 Skill 市场上架。**

## 功能

- 角色动画：专注、忙碌、等待、开心、低落、休息。
- CodeArts CLI / OpenCode 的**可选**生命周期 Hook；默认不安装，需用户明确同意。
- 趣味成长：能量、快乐值、XP、等级、任务记录和连胜。
- 演示事件和来自 Hook 的事件在网页内分别标识；演示按钮不会伪装为 Agent 成功。
- 不读取或上传提示词、源代码、文件名、执行输出、令牌、Session ID。

## 启动

仓库源码模式：

```bash
cargo run --bin vibepet -- serve
# 用浏览器打开 http://127.0.0.1:7878
```

下载 ZIP 时：macOS / Linux 在解压的 Skill 目录执行 `./bin/vibepet serve`；Windows 使用 `bin/vibepet.exe serve`。

另一终端：

```bash
cargo run --bin vibepet -- status
cargo run --bin vibepet -- emit session_start --source demo
cargo run --bin vibepet -- emit tool_start --source demo
cargo run --bin vibepet -- emit tool_done --source demo
cargo run --bin vibepet -- emit task_success --source demo
```

## CodeArts CLI 与 OpenCode Hook 接入

**必须经用户同意才能安装插件**。复制适配器到当前项目后，重新启动相应 Agent：

```bash
# CodeArts CLI：在开发项目根目录执行
mkdir -p .codeartsdoer/plugins
cp skills/vibecoding-pet/adapters/codearts-plugin.js .codeartsdoer/plugins/vibecoding-pet.js

# OpenCode：在开发项目根目录执行
mkdir -p .opencode/plugins
cp skills/vibecoding-pet/adapters/opencode-plugin.js .opencode/plugins/vibecoding-pet.js
```

以上 `cp` 示例假设当前项目中确实存在 `skills/vibecoding-pet/adapters/`。如从单独的 Skill ZIP 解压，应改用解压目录的实际路径。两种 Hook 均将固定事件类型发送到本机 7878 端口，连接失败不影响 Agent 工作。

CodeArts CLI / OpenCode 插件接口已按[华为官方 Hooks 文档](https://support.huaweicloud.com/usermanual-cli/codeartsagent_cli_0018.html)和[OpenCode 官方 Plugins 文档](https://docs.opencode.ai/docs/plugins/)编写，并通过 Mock 回归测试；**尚未在用户实际工具会话中验证自动投递**。

## 测试与分发

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --locked -- -D warnings
cargo test --all-targets --locked
node --test tests/test_vibepet_plugins.mjs
python -m unittest discover -s tests -p 'test_vibepet_dist.py' -v
```

`tools/vibepet_dist.py` 负责独立普通 ZIP 与 CodeArts 顶层 Skill ZIP；归档保留二进制、网页、插件及 SHA-256 清单。CI 测试 Linux、macOS、Windows。

## 约束

- Rust 标准库实现；无额外 Cargo 第三方依赖。
- 本机 HTTP 限制 Host、Origin、长度和事件白名单，但 loopback 来源名称只是**声明**，不是独立身份认证。
- 进度存在内存，停止服务即清零；不支持云端同步、持久化、自动修复或 ESP32 硬件控制。
- XP 和连胜是娱乐指标，不代表客观代码质量或开发效率。
- `session.idle` / `chat.finished` 不等于任务成功，插件不会据此发 `task_success`。

详细架构与验收：[docs/VIBEPET.md](../../docs/VIBEPET.md)。
