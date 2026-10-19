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

## Verification not yet performed

A correctly structured ZIP does **not** prove import or runtime success. Actual CodeArts IDE import, Agent recognition, command invocation permissions, output handling and competition submission must be verified with a real logged-in platform session. Cloud sandboxes may prohibit native executables and require a script or service adapter instead.
