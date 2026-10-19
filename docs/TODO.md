# RepoDoctor｜后续开发与参赛事项（2026-10-19）

## 已完成

- [x] Rust 离线只读扫描 CLI；RepoDoctor SKILL.md、元数据与原生分发包。
- [x] JSON、Markdown、SARIF 报告格式；`static-lead` 证据等级及 `scan.truncated` 范围披露。
- [x] Linux、macOS、Windows GitHub Actions 构建、测试、分发 ZIP 与 SHA-256 校验。
- [x] [GitHub 正式发行 v0.2.0](https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0)。
- [x] [真实 CodeArts CLI Agent 调用 RepoDoctor 并生成 RD001 报告](https://github.com/hu-qi/rednote-skills/actions/runs/39218426522)。
- [x] CodeArts Skill ZIP 包结构及 5 MiB 限制验证。
- [x] **用户反馈**：华为云 Skill 市场 `repodoctor`（市场版本 1.0.0）已上架。
- [x] **用户反馈**：小红书 SkillHub `repodoctor-cn`（skill_id=101678，市场版本 1.0.0）已审核通过上架。
- [x] 中文优先的 Skill 说明和[小红书参赛发布文案](MARKETPLACE.zh-CN.md)。

## 尚需完善

- [ ] 收集两个市场稳定的作品**详情页 URL**，保存到参赛资料中，进行公开核验。
- [ ] 确认参赛报名/活动页最终收件状态及后续评审通知（市场上架不等于赛事最终获奖）。
- [ ] IDE 图形界面独立导入、宿主平台兼容性及首次使用文档。
- [ ] 更多真实代码的标注评测样本、精确率/召回率和误报漏报分析。
- [ ] 获得明确授权后进行真实公开仓库诊断与前后对比演示。
- [ ] 加固语言解析和检测规则；避免把启发式线索宣传为已验证漏洞。
- [ ] 选择性扩展 AI 辅助建议、严格数据脱敏和预算控制；默认保持离线只读。

## 独立 Skill 基础设施

- [x] 每个发行包包含校验清单，安装器可验证哈希，支持显式升级和回滚。
- [ ] 如有需求，补充可验证签名和供应链证明（当前为 SHA-256 校验，不是签名）。
- [ ] VibeCoding Pet Skill（单独迭代）。
- [ ] Rednote Creator Lab Skill（单独迭代）。

**版本说明：** GitHub v0.2.0 与两个市场的 1.0.0 是独立版本体系。更新源码需通过市场版本管理流程才能反映到已上架 Skill，不能默认自动同步。
