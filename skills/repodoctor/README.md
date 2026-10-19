# RepoDoctor｜发布前代码风险体检

**不用上传源码、不需要大模型 API Key，给代码仓库做一次只读风险检查。**

RepoDoctor 是基于 Rust 开发的离线 Agent Skill，可以在版本发布或代码评审前扫描仓库，识别 GitHub Actions 过高权限、潜在危险的 Shell 调用、动态代码执行以及私钥文件头等**需要人工复核的线索**，并输出带规则编号和文件行号的诊断报告。

## 适用场景

- 发布前检查 CI 工作流权限和常见代码风险。
- 在本地对 Git 仓库进行可复核的静态风险排查。
- 使用 CodeArts Agent Skill 调用 Rust 诊断器，并生成 JSON、Markdown 或 SARIF 报告。

## 如何使用

在源码仓库中：

```bash
cargo run --bin repodoctor -- validate-skill skills/repodoctor
cargo run --bin repodoctor -- scan . --format json
cargo run --bin repodoctor -- scan . --format markdown
cargo run --bin repodoctor -- scan . --format sarif --output repodoctor.sarif
cargo test --all-targets
```

下载 [v0.2.0 GitHub Release](https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0) 中与你的操作系统一致的 ZIP，解压后按 `SKILL.md` 运行。CodeArts 专用 ZIP 与普通 CLI 分发包分别提供，包内含原生可执行程序。macOS Apple Silicon（M1/M2/M3/M4）使用 `macos-aarch64`。

## 检测范围

| 规则 | 需要人工复核的线索 |
| --- | --- |
| RD001 | GitHub Actions 工作流宽泛写权限 |
| RD002 | `pull_request_target` 的信任边界 |
| RD003 | Python `subprocess` 搭配 `shell=True` |
| RD004 | JavaScript/TypeScript `eval(` |
| RD005 | PEM 私钥文件头（不会打印密钥内容） |

扫描默认只读，不执行目标项目代码，不跟随符号链接，也不进行联网和上传。最多扫描 10,000 个符合条件的 UTF-8 文件，单个文件不得超过 1 MiB。**静态风险线索不是已验证漏洞；零发现不意味着绝对安全。** 当前版本不提供自动修复、漏洞复现、动态验证或自动提交 PR。

## 参赛发布

根据参赛者 **2026-10-19** 的反馈：
- 华为云 Skill 市场：`repodoctor`，`development` 分类，市场版本 **1.0.0**，已发布。
- 小红书 SkillHub：`repodoctor-cn`（skill_id=`101678`，version_id=`108108`），市场版本 **1.0.0**，已审核通过并上架；中文介绍、编程开发标签、原创作品。

详见 [中文市场介绍与版本映射](../../docs/MARKETPLACE.zh-CN.md) 和 [赛事发布记录](../../docs/SUBMISSION.md)。

注意：GitHub CLI/Skill 分发版本 **v0.2.0** 与两个市场的展示版本 **1.0.0** 是不同版本体系；更新 GitHub 仓库不会自动更新已上架的市场版本。

## English

RepoDoctor is a Rust-powered, offline and read-only repository risk triage Agent Skill. It produces file/line-numbered, **heuristic static leads**, not verified vulnerabilities. Portable packages are available for macOS, Linux and Windows in the GitHub Release.
