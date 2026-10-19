# CodeArts compatibility and competition package

Huawei CodeArts documentation requires a ZIP with one or more top-level named Skill folders, each containing SKILL.md with YAML name and description. The IDE import instructions currently specify a **5 MiB ZIP upload limit**. This is distinct from the competition's 40 MB / 30 file submission limit.

Sources:
- https://support.huaweicloud.com/usermanual-codeartsagent/codeartsagent_ug_0024.html
- https://support.huaweicloud.com/usermanual-cli/codeartsagent_cli_0019.html

## Building

First build a native RepoDoctor release archive (standard flat ZIP with manifest.json). Next wrap it for CodeArts:

```bash
python3 tools/codearts_package.py dist/repodoctor-v0.2.0-macos-aarch64.zip --output dist/repodoctor-v0.2.0-macos-aarch64-codearts.zip
python3 tools/codearts_package.py dist/repodoctor-v0.2.0-macos-aarch64-codearts.zip --verify
```

The CodeArts ZIP contains repodoctor/SKILL.md, repodoctor/README.md, repodoctor/manifest.json and repodoctor/bin/repodoctor. The source archive is integrity-checked before wrapping; CI checks the 5 MiB upload size and top-level folder. The original flat GitHub distribution ZIP remains unchanged for the secure local installer.

## Installing locally (CLI)

For the CodeArts CLI's project-scoped Skill, the documented location is `<repo>/.codeartsdoer/skills/repodoctor/`. The personal Skill directory is `~/.codeartsdoer/skills/repodoctor/`. It must contain SKILL.md and the matching native executable. Set executable permissions on Unix when necessary.

## 已验证能力与仍需确认的事项

**CodeArts CLI 真实集成已通过：** [GitHub Actions #39218426522](https://github.com/hu-qi/rednote-skills/actions/runs/39218426522) 在临时 Linux Runner 中成功安装 CodeArts CLI、识别项目级 RepoDoctor Skill，通过 `huaweicloud-maas/glm-5.3` 调用 Rust 程序，生成包含 RD001 规则结果的 JSON。验证需要配置正确的 `security.folderTrust.enabled` 和仅针对测试命令的非交互 Bash 授权，并保留 CLI `--sandbox`。上述临时权限配置**不得照搬到不受信任的项目目录**。

**市场发布状态（2026-10-19，用户反馈）：** 华为云 Skill 市场 `repodoctor` 1.0.0 已上架；小红书 SkillHub `repodoctor-cn` 1.0.0（skill_id=101678、version_id=108108）已审核通过上架。详见 [市场中文介绍](MARKETPLACE.zh-CN.md)。

**仍需独立验证：** IDE 图形界面的 ZIP 导入操作、云端沙箱对原生可执行文件的支持范围及两个市场的作品详情页；不要把 Linux Runner CLI 集成成功自动等同于全部宿主环境兼容。后续版本仍需分别验证平台发布。

**注意版本映射：** GitHub v0.2.0 是 CLI 分发版本，两个市场的 1.0.0 是独立市场版本；本仓库变更不会自动更新已发布市场记录。
