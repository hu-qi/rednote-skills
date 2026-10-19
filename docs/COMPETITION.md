# 华为 CodeArts / 小红书 Skill 创新赛 — RepoDoctor 验收清单

**更新于 2026-10-19。** 市场上架状态依据参赛者的发布确认；CI 验证和 GitHub Release 另有可公开核实的运行记录。

- [x] RepoDoctor Rust CLI 与 `name` / `description` 的 Skill Frontmatter
- [x] JSON、Markdown、SARIF 2.1.0 输出，包含规则 ID、相对文件路径和行号
- [x] Linux / macOS / Windows 多平台 CI、完整独立分发包及 SHA-256 完整性检查
- [x] [GitHub Release repodoctor/v0.2.0](https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0) 四平台构建与发布
- [x] CodeArts ZIP 包 `repodoctor/SKILL.md` 顶层结构及 5 MiB 压缩大小检查
- [x] [真实 CodeArts CLI Agent 验证](https://github.com/hu-qi/rednote-skills/actions/runs/39218426522)：加载 Skill、运行 Rust 扫描、生成 RD001 JSON 证据
- [x] **用户确认**华为云 Skill 市场 `repodoctor` 1.0.0 已上架
- [x] **用户确认**小红书 SkillHub `repodoctor-cn` 1.0.0 已审核通过上架（skill_id=101678，version_id=108108）
- [x] 建立完整的[简体中文市场介绍与发布须知](MARKETPLACE.zh-CN.md)
- [ ] 获取两个市场稳定、可公开访问的**作品详情链接**用于独立核实和比赛展示（目前只有华为云市场首页）
- [ ] 从用户界面独立复测 CodeArts IDE 的 ZIP 导入与首次 Skill 调用流程（GitHub Runner 的 CLI 调用已成功）
- [ ] 补充覆盖真实代码场景的标注评测，记录误报和漏报
- [ ] 用用户授权的代表性仓库做发布前/后对照演示并提供可复现证据
- [ ] 按赛事规则确认作品审核、参赛报名、活动页终审与展示素材的最终要求

**证据边界：** 当前检测是静态风险线索（`static-lead`），不是已证实漏洞；自动修复、漏洞动态复现和补丁验证**均未实现**。不得将“市场上架”写成“比赛获奖”，也不得在缺少基准数据时宣称检测准确率。

GitHub CLI 发布版本 `v0.2.0` 与两个市场的展示版本 `1.0.0` 独立管理。源代码和中文文案修订不会自动更新已审核市场版本。
