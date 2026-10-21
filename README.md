# Rednote Skills｜开源 Agent Skills

Rust-first、可复用、可独立分发的 Agent Skills。**RepoDoctor** 已发布并通过 CodeArts CLI 真实调用验证；**VibeCoding Pet** 正在实现首个可运行的 v0.1.0 MVP；Rednote Creator Lab 仍在规划。

## RepoDoctor｜代码仓库风险体检

RepoDoctor 是默认离线、只读的 Rust 代码风险检查工具。它通过 Agent Skill 接入 CodeArts，也可独立作为命令行工具运行，为 GitHub Actions 工作流权限、Python subprocess、JavaScript/TypeScript eval 及 PEM 私钥文件头提供**文件与行号可追溯的静态风险线索**。

### 使用

```bash
cargo run --bin repodoctor -- validate-skill skills/repodoctor
cargo run --bin repodoctor -- scan . --format json
cargo run --bin repodoctor -- scan . --format markdown
cargo run --bin repodoctor -- scan . --format sarif
cargo test --all-targets
```

**[下载 RepoDoctor v0.2.0 正式发行版](https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0)**：Linux、Windows、macOS Intel 和 Apple Silicon 均提供原生可执行文件及 CodeArts 安装包。

**真实集成验证：** [CodeArts CLI Actions #39218426522](https://github.com/hu-qi/rednote-skills/actions/runs/39218426522) 已成功加载 RepoDoctor Skill、调用 Rust 程序并输出包含 RD001 的诊断报告。

### 双市场发布（2026-10-19 用户反馈）

- **华为云 Skill 市场**：`repodoctor`，市场版本 1.0.0，用户确认已上架。
- **小红书 SkillHub**：`repodoctor-cn`（skill_id=101678、version_id=108108），市场版本 1.0.0，用户确认审核通过并已上架。

中文参赛材料见 [中文市场介绍](docs/MARKETPLACE.zh-CN.md) 和 [提交记录](docs/SUBMISSION.md)。小红书发布文案和说明以**简体中文**为主，但命令、接口名与规则 ID 保持英文原样。GitHub 的 v0.2.0 和市场 1.0.0 是不同的版本体系；本仓库不会自动同步更新已上架的市场作品。

**能力边界：** 目前只提供启发式静态风险线索，**并不等同于已确认漏洞**；不执行目标代码、不上传、不自动修复。扫描结果为零也不意味着仓库绝对安全。

[Skill 使用说明](skills/repodoctor/SKILL.md) · [分发流程](docs/RELEASE.md) · [赛事验收](docs/COMPETITION.md) · [项目路线图](docs/TODO.md)

## VibeCoding Pet v0.1.0｜陪你写代码的小宠物

第二个独立 Skill 的首个 MVP：**Rust 本机事件服务 + CodeArts/OpenCode Hook 适配器 + 可视化动画宠物**。支持 Agent 思考、工具运行、等待审批、错误和休息状态；提供互动投喂、快乐值、能量、经验等级和来源明确的演示事件。

```bash
cargo run --bin vibepet -- serve
# 浏览器打开 http://127.0.0.1:7878
```

```bash
# 第二个终端：仅作演示，不冒充真实 Agent
cargo run --bin vibepet -- emit tool_start --source demo
cargo run --bin vibepet -- emit tool_done --source demo
```

CodeArts CLI / OpenCode Hook 需要用户明确许可后手动安装；它们只发送固定的事件类型，不读取代码、提示词、工具输出或密钥。完整使用说明：[VibeCoding Pet Skill](skills/vibecoding-pet/SKILL.md) · [技术架构与测试](docs/VIBEPET.md)。

**当前状态：** MVP 开发与 CI 阶段。Hook 已按官方插件接口实现，用户环境的真实事件投递和市场上架尚未核实；ESP32 硬件控制、进度持久化等属于后续版本，不将其当成已实现功能。

## English

RepoDoctor is an offline, read-only Rust repository risk triage Skill. Native executables and CodeArts packages are available in [GitHub Releases](https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0). Findings are heuristic review leads, not confirmed vulnerabilities.
