# RepoDoctor｜2026 小红书 Skill 创新赛提交记录

## 当前状态（2026-10-19，参赛者反馈）

**华为云 Skill 市场与小红书 SkillHub 均已发布成功。** 此状态依据参赛者在当前对话中提供的官方平台执行结果；本仓库尚未取得两个平台的独立作品详情链接，因此不是通过公共 API 独立复核的市场状态，也**不等于赛事最终评奖结果**。

| 阶段 | 记录 |
| --- | --- |
| CodeArts CLI 完整 Skill 执行 | [Actions #39218426522](https://github.com/hu-qi/rednote-skills/actions/runs/39218426522) 成功，真实调用 Rust 程序并发现测试规则 RD001 |
| GitHub 正式发行 | [repodoctor/v0.2.0](https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0) 已发布，含 macOS / Linux / Windows 平台包及校验和 |
| GitHub Actions 自动化市场发布尝试 | [Actions #39219370115](https://github.com/hu-qi/rednote-skills/actions/runs/39219370115)，CodeArts 会话完成但缺少市场发布凭据，故 CI 未宣称成功 |
| 华为云 Skill 市场 | 作品 `repodoctor`，分类 `development`，市场版本 **1.0.0**，用户确认已上架；首次提交 2026-10-19T08:26:50Z |
| 小红书 SkillHub | 作品 `repodoctor-cn`；skill_id **101678**；version_id **108108**；市场版本 **1.0.0**；用户确认审核通过并已上架 |
| 小红书审核单号 | `101678_108108_1792402119351`；最初 `submitted`（`display_status=1`，待审核），之后用户确认已通过 |

**版本区别：** GitHub Release v0.2.0 是 Rust CLI + Skill 分发版本；市场版本 1.0.0 是发布平台版本。当前仓库后续修改不会自动更新已上架的两个市场包。

## 官方提交流程

参赛者提供的官方说明：

> 我正在参加小红书Skill创新赛，帮我把这个Skill先发布到华为云Skill市场，再使用redskillhub-upload发布到小红书Skill市场。

官方推荐使用 CodeArts 对话完成投稿，如需登录、扫码、确认信息，则在对应平台交互完成。**小红书侧主要展示文案及使用介绍应为简体中文**，保留 `name`、命令和 Schema 字段等程序接口的英文拼写。

## 中文作品介绍及发布材料

参见 [MARKETPLACE.zh-CN.md](MARKETPLACE.zh-CN.md)，其中包含中文标题、简介、功能范围、隐私说明、建议标签、演示命令以及版本映射。

## 后续维护及验收

- 未来新版本仍需单独检查平台发布状态；CI 的 `codearts run` 成功、Skill 加载成功和市场审核通过是三个不同层级的证据。
- 不重复上传 1.0.0；需要改动市场展示内容时，通过平台版本管理明确创建修订版。
- 请记录两个市场的作品**详情页 URL**（不是市场首页），用于后续参赛展示与第三方核验。
- 双市场成功不代表比赛已经完成评审或获奖；参赛结果以比赛官方后台状态为准。
- 一次性 CI 发布工作流在第一次尝试后已从主分支移除，避免重复触发发布；原 Actions 历史运行仍可审计。

## 官方市场及项目链接

- 华为云 Skill 市场首页：https://skills.huaweicloud.com/community
- GitHub 源码：https://github.com/hu-qi/rednote-skills
- GitHub Release：https://github.com/hu-qi/rednote-skills/releases/tag/repodoctor/v0.2.0
