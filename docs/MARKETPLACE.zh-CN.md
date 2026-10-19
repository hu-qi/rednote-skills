# RepoDoctor｜双市场作品信息（简体中文）

> 信息来源：参赛者于 **2026 年 10 月 19 日** 提供的发布确认。市场上架状态属于用户反馈；公开页面的特定作品链接尚未提供，不能把市场首页当作作品详情页。本文不包含账号凭证。

## 正式发布状态

| 平台 | 作品标识 | 版本 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| 华为云 Skill 市场 | `repodoctor` | 市场版本 `1.0.0` | 用户确认已上架 | 2026-10-19T08:26:50Z 提交；[市场首页](https://skills.huaweicloud.com/community) |
| 小红书 SkillHub | `repodoctor-cn`，skill_id `101678` | 市场版本 `1.0.0`，version_id `108108` | 用户确认审核通过、已上架 | 审核单号 `101678_108108_1792402119351` |

**小红书的历史状态 `submitted`／`display_status=1` 是首次提交时的状态，已被用户随后反馈的“审核通过已上架”取代。** 后续如需机器审计，请补充两个作品的稳定详情页 URL 或市场后台审核凭据；在此之前不宣称本仓库独立验证了两平台审核结果。

## 小红书中文发布文案

**推荐作品标题：** RepoDoctor｜开源代码仓库安全体检 Skill

**一句话介绍：** 不上传代码、不执行目标程序，为 GitHub 仓库生成带文件行号和规则说明的静态风险检查报告。

**作品简介：**

RepoDoctor 是一款 Rust 编写的开源代码仓库风险诊断 Skill。适合开发者在代码评审、CI 配置检查和版本发布前进行快速体检。它可以识别 GitHub Actions 权限过宽、`pull_request_target` 工作流信任边界、Python `subprocess(..., shell=True)`、JavaScript/TypeScript `eval(` 以及 PEM 私钥文件头等风险线索。扫描默认离线、只读，不执行仓库代码，也不会回显私钥内容；提供 JSON、Markdown 和 SARIF 报告，包含规则 ID、风险级别以及文件行号，便于人工复核。

> 注意：规则匹配属于**静态风险线索**，并非已证实的安全漏洞；当前版本**不支持自动修复、漏洞复现或自动 PR**，也不能保证发现所有风险。

**分类：** 编程开发 / 开发工具（华为云市场使用 `development` 分类）。

**标签建议：** 编程开发、代码审查、开源、Rust、DevOps、GitHub Actions、代码安全、Agent Skill。

**隐私与权限：** 默认只读、离线扫描；需要用户授权访问本地仓库。仅在用户主动指定报告保存位置时写出报告。

**演示操作：** `repodoctor scan <本地仓库目录> --format markdown`。CodeArts Agent 可调用安装在项目 Skill 目录中的同平台 Rust 二进制，但需要工作目录信任与相应命令执行权限。

## 发布约束与术语

- 小红书市场标题、介绍、核心使用说明及限制条款优先使用**简体中文**，以免因主要内容为英文而影响发布流程。
- `SKILL.md` 必须保留英文机器字段名（`name`、`description`）、原始命令、标志位、规则 ID、JSON Schema 键，不得翻译成不可执行的中文。
- **GitHub Release `repodoctor/v0.2.0` 是代码发行版本**；两个市场记录的 `1.0.0` 是各自市场的展示版本。这两个数字不要求相等，也不能作为同一构建的校验证据。
- GitHub 源码的中文本地化不会自动覆盖或修改两个市场已发布的 `1.0.0` 作品；若需同步，须明确创建新版本并根据平台政策再次审核。
- 不要把市场审核通过误写为比赛获奖或赛题终审通过；二者是不同状态。

## 公开参考

- 代码仓库：https://github.com/hu-qi/rednote-skills
- GitHub Release：https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0
- 真实 CodeArts CLI Skill 调用成功：https://github.com/hu-qi/rednote-skills/actions/runs/39218426522
- 市场发布及首次自动化尝试过程：参见 [SUBMISSION.md](SUBMISSION.md)
