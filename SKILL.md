---
name: kpi-weekly-code-review
description: Weekly KPI performance review for software projects based on recent git commits, code quality, delivery evidence, collaboration signals, and the A/B/C grading rubric from Chinese KPI standards. Use when the user asks to evaluate weekly code submissions, assess developer or project performance, score KPI/绩效, review one week of commits, rate code quality and delivery, or produce A++/A+/A/B++/B+/B/C++/C+/C performance conclusions.
---

# KPI Weekly Code Review

## Overview

Evaluate a project's recent code work, normally the last 7 days, and produce a KPI score using the provided rubric:

- `A++`: 标杆级，团队学习对象
- `A+`: 非常优秀，主动担难活
- `A`: 稳定超预期，团队中坚
- `B++`: 合格偏上，偶有亮点
- `B+`: 合格，偶需提醒
- `B`: 勉强达标，警示档
- `C++`: 多处不达标，需谈话
- `C+`: 严重不足，进入 PIP
- `C`: 不合格，面临淘汰

Default to evidence-based scoring. Do not infer attitude, diligence, or collaboration from commit count alone. When evidence is missing, mark it as `无法判断` and avoid over-penalizing unless the missing signal is itself a clear risk.

## Quick Start

When this skill is loaded, resolve `<skill-dir>` as the directory that contains this `SKILL.md`. Do not use a hardcoded install path, because different skill managers may install the skill under different directories.

From the target repository root, run:

```bash
python3 <skill-dir>/scripts/weekly_kpi_collect.py --days 7
```

Use `--author` to evaluate one person:

```bash
python3 <skill-dir>/scripts/weekly_kpi_collect.py --days 7 --author "Alice"
```

Use `--base main` when the repo has a clear mainline branch and the week's work is on a feature branch:

```bash
python3 <skill-dir>/scripts/weekly_kpi_collect.py --days 7 --base main
```

## Workflow

1. Confirm the repository root with `git rev-parse --show-toplevel`.
2. Collect evidence with `<skill-dir>/scripts/weekly_kpi_collect.py`, where `<skill-dir>` is the directory containing this `SKILL.md`.
3. Run project quality checks when available and safe:
   - Node: `npm test`, `npm run lint`, `npm run typecheck` when scripts exist.
   - Python: `pytest`, `ruff check`, `mypy` when configured.
   - Swift/iOS: `xcodebuild test` only when scheme/project is clear.
   - Rust/Go: `cargo test` / `go test ./...`.
4. Inspect representative diffs for correctness, maintainability, and risk. Prefer files with high churn, core business logic, tests, database migrations, auth/security, API boundaries, concurrency, and error handling.
5. Score each dimension below, then map to the final KPI level.
6. Output the final grade with concrete evidence, not generic praise or criticism.

## Scoring Dimensions

Score each dimension from 0 to 10.

- Delivery: tasks completed on time, weekly goal completion, meaningful shipped functionality.
- Code quality: correctness, maintainability, simplicity, style consistency, reviewability.
- Defect risk: regressions, failing checks, unsafe migrations, security issues, broken tests, brittle behavior.
- Testing: meaningful test additions/updates, coverage of changed behavior, verification evidence.
- Collaboration: commit/PR clarity, review responsiveness, cross-file coordination, low disruption to teammates.
- Initiative: proactive cleanup, hard problem ownership, useful refactoring, deeper weekly report thinking.

Use weights unless the user provides different business priorities:

- Delivery: 30%
- Code quality: 25%
- Defect risk: 20%
- Testing: 10%
- Collaboration: 10%
- Initiative: 5%

For `Defect risk`, invert the risk score before weighting: `10` means low risk, `0` means severe risk.

## Grade Mapping

Use the weighted score as the starting point, then adjust by hard gates.

- `A++`: 9.5-10.0 and strong evidence of exemplary delivery, near-zero quality issues, meaningful tests, and reusable team value.
- `A+`: 9.0-9.49 with excellent delivery, clear ownership of difficult work, and no serious quality gaps.
- `A`: 8.3-8.99 with stable over-delivery, strong quality, and reliable collaboration.
- `B++`: 7.6-8.29 with qualified work plus one or more clear highlights.
- `B+`: 7.0-7.59 with qualified work and minor reminders needed.
- `B`: 6.0-6.99 with barely acceptable delivery or quality; warning level.
- `C++`: 5.0-5.99 with multiple unmet expectations; requires direct conversation.
- `C+`: 4.0-4.99 with serious shortage; recommend PIP if pattern repeats or impact is high.
- `C`: below 4.0 or objectively failed delivery with severe quality/process violations.

## Hard Gates

Apply these after weighted scoring:

- Cap at `B+` if tests/typechecks/lint fail and the failure is caused by the reviewed changes.
- Cap at `B` if the week has meaningful production-breaking behavior, unreviewed destructive migrations, committed secrets, or security regressions.
- Cap at `B` if delivery is mostly unmerged, non-runnable, or cannot be verified.
- Cap at `C++` if there are repeated missed deadlines, poor-quality code, perfunctory weekly reporting, negative collaboration, or attendance/process violations supported by evidence.
- Cap at `C+` or `C` only when there is strong evidence of severe insufficiency, not merely low commit volume.
- Do not award `A++` without evidence of team-level leverage, such as reusable abstractions, high-quality documentation, mentorship, major incident prevention, or a benchmark implementation.

## Evidence Rules

Use these heuristics to avoid shallow scoring:

- Commit count is context, not a grade. Small high-value fixes can score high; large noisy churn can score low.
- Lines changed are only meaningful after excluding lockfiles, generated files, vendored files, formatting-only changes, and snapshots.
- A week with no tests can still be `B+` or higher only if the changes are low risk and verified another way.
- Penalize unclear work when there are vague commits, unexplained large diffs, missing reproduction steps, or no verification notes.
- Reward maintainable problem solving: simpler APIs, smaller blast radius, backward compatibility, explicit error handling, and readable tests.
- Separate project-level score from individual score. If using `--author`, do not attribute unrelated repository failures to the person unless their changes caused them.

## Output Format

Respond in Chinese unless the user asks otherwise.

```markdown
**KPI 评分**
最终等级：A/B/C...
综合分：x.x/10
结论：一句话说明为什么是这个等级。

**证据**
- 交付：...
- 质量：...
- 测试与验证：...
- 协作：...
- 风险：...

**分项分**
- Delivery: x/10
- Code quality: x/10
- Defect risk: x/10
- Testing: x/10
- Collaboration: x/10
- Initiative: x/10

**改进建议**
- ...
```

If evidence is insufficient, explicitly say what was unavailable and give a provisional score such as `暂定 B+` instead of pretending certainty.
