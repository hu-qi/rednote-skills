# Rednote Skills｜开源 Agent Skills

Rust-first、可复用、可独立分发的 Agent Skills。当前已实现并公开发布 **RepoDoctor**；VibeCoding Pet 和 Rednote Creator Lab 仍在规划阶段。

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

## English

RepoDoctor is an offline, read-only Rust repository risk triage Skill. Native executables and CodeArts packages are available in [GitHub Releases](https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0). Findings are heuristic review leads, not confirmed vulnerabilities.
