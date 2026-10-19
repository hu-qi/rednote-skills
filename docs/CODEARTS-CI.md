# RepoDoctor — CodeArts CLI integration and competition submission

This workflow intentionally separates **tested locally**, **verified by CodeArts Agent**, and **published to two markets**.

## Official submission instruction

According to the 2026 Huawei Developer Competition "创作与提交" page, instruct CodeArts:

> 我正在参加小红书Skill创新赛，帮我把这个Skill先发布到华为云Skill市场，再使用redskillhub-upload发布到小红书Skill市场

The page notes that extra prompts/confirmations may occur. A CLI response claiming success does **not** by itself establish publication. Check each public marketplace listing and record its ID/URL before declaring the competition submission complete.

## Automated tests

- The default Rust CI checks static code, Rule benchmarks, Skill packaging, cross-platform releases.
- `.github/workflows/codearts-cli.yml` downloads the installer from the official China North 4 OBS URL, installs CodeArts CLI on a fresh Linux runner, checks its version, and provisions `skills/repodoctor/SKILL.md` with the compiled binary in `.codeartsdoer/skills/repodoctor/`.
- It runs `codearts models` with ephemeral `CODEARTS_CLI_AK` and `CODEARTS_CLI_SK` environment variables and validates the actual model identifiers.
- `codearts run ... --sandbox` is invoked to perform a read-only scan on a synthetic fixture containing `permissions: write-all`. **Passing requires an actual JSON artifact containing RD001**, not just an affirmative LLM sentence.
- Primary model: `glm-5.3-flash`; fallback: `Gemini-3.8-Flash-Medium` **only on explicit quota/rate-limit failures**. Models must be advertised by `codearts models`; if identifiers differ, update matching rules based on actual model listing rather than guessing.
- All CI status artifacts are sanitized. Raw model transcripts, CLI authentication outputs, tokens and access keys are never uploaded.

## Required Secrets

GitHub Actions repository secrets `AK` and `SK` must contain the CodeArts IAM credentials (their values are not printed). They are exposed **only to the CodeArts Agent invocation step**. If actual secret names differ, adjust the two env mappings in the workflow.

If `codearts models` fails or the agent cannot execute the Skill in sandbox, CI deliberately fails. Logs and the sanitized `codearts-cli-result-<run_id>` artifact identify the stage without disclosing credentials.

## Submission attempt — manual only

After a passing CodeArts smoke run:

1. Open [CodeArts CLI Integration](https://github.com/hu-qi/rednote-skills/actions/workflows/codearts-cli.yml).
2. Choose **Run workflow**, branch `main`, phase `submit`.
3. CLI sends the above competition submission request and tries both marketplace publications in sequence.
4. Inspect the sanitized result artifact. `submission_attempt_needs_marketplace_confirmation` means the AI run returned, **not** that both markets accepted the upload.
5. Finish any required account login, publisher approval, CAPTCHA or interactive confirmation on CodeArts Web/IDE. Verify **both** public marketplace pages and record their IDs/URLs.

The workflow intentionally never uses `--auto`, since granting an AI CLI unrestricted command execution in CI while AK/SK are present is unsafe. The default `--sandbox` may block publication tools: the safe remedy is an interactive CodeArts session with user approval, not a blanket bypass.

## Security and restrictions

- Use only tagged or reviewed `main` work, not untrusted pull requests, with cloud credentials.
- Never log AK/SK, credentials, raw conversations or signed URLs.
- Runtime downloads the official installer over HTTPS. Since upstream installer artifacts are mutable, consider vendor checksums or pinning a version after a known-good run.
- A green `codearts --version` is **installation proof only**. The smoke harness separately checks agent invocation and a real RepoDoctor output file.
- The workflow does not bypass contest registration requirements, and cannot guarantee external marketplace publication when approval is required.
- GitHub's `workflow_dispatch` run is intentionally explicit to prevent repeat submissions during normal CI pushes.
