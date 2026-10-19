# RepoDoctor — Competition publication attempt

Official contest reference supplied by the participant:

> 我正在参加小红书Skill创新赛，帮我把这个Skill先发布到华为云Skill市场，再使用redskillhub-upload发布到小红书Skill市场

The CodeArts CLI integration smoke [#39218426522](https://github.com/hu-qi/rednote-skills/actions/runs/39218426522) has **passed**: the Agent loaded the Skill and generated a JSON report identifying RD001.

## First external publication attempt

A **one-time** GitHub Actions workflow in `.github/workflows/repodoctor-submit-once.yml` triggers only on the initial push of that file to `main`, verifies the known-good smoke and attempts to publish the complete independent Skill directory `.codeartsdoer/skills/repodoctor/`. The workflow invokes CodeArts CLI using reviewed code and the repository's preconfigured AK/SK Secrets.

The user explicitly authorized the external publication attempt. The Agent must obey interactive confirmations and stop rather than bypass publisher permissions. Running the Agent successfully does not establish market acceptance.

### Proof required before declaring submission complete

- Huawei Cloud Skill Market: an actual public listing URL or work ID.
- Xiaohongshu Skill Market: a separate public listing URL or work ID, after successful `redskillhub-upload`.
- Creator/publisher approvals, originality declarations, verification codes or QR login completed via the official authenticated interface.
- Clear evidence of accepted submission, not merely a draft.

The workflow deliberately returns nonzero and uploads a sanitized status artifact when external marketplace confirmation is missing. The attempt does not echo AK/SK, raw model transcripts or marketplace session tokens.

After the initial run, remove the one-time workflow to eliminate re-publication risk. If marketplace login or human approval is required, finish on the official CodeArts/creator UI. Do not claim completion based solely on the Agent text response.
