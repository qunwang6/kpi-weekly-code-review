# KPI Weekly Code Review

按周评估软件项目代码提交、交付质量、测试验证、协作信号和风险水平，并按照 A/B/C 绩效档位输出结构化 KPI 结论。

这个 skill 适合用于：

- 评估某个项目最近一周的代码工作质量
- 对单个开发者的周度提交做绩效评分
- 基于 git 证据、测试结果和代码 diff 给出 A++ 到 C 的等级
- 输出可用于周报、绩效沟通或代码质量复盘的中文结论

## 能力概览

评分会优先基于可验证证据，而不是单纯看提交数量或代码行数。默认评估最近 7 天的工作，并从以下维度综合判断：

- 交付：功能完成度、目标达成情况、是否有实际可验证产出
- 代码质量：正确性、可维护性、复杂度、风格一致性、可 review 性
- 缺陷风险：回归、失败检查、不安全迁移、安全问题、脆弱实现
- 测试验证：测试新增或更新情况、覆盖关键行为、是否有验证证据
- 协作：提交信息、PR 清晰度、跨文件协调、对他人工作的影响
- 主动性：主动清理、难题承担、有效重构、复盘深度

最终等级范围：

| 等级 | 含义 |
| --- | --- |
| A++ | 标杆级，团队学习对象 |
| A+ | 非常优秀，主动担难活 |
| A | 稳定超预期，团队中坚 |
| B++ | 合格偏上，偶有亮点 |
| B+ | 合格，偶需提醒 |
| B | 勉强达标，警示档 |
| C++ | 多处不达标，需谈话 |
| C+ | 严重不足，进入 PIP |
| C | 不合格，面临淘汰 |

## 文件结构

```text
kpi-weekly-code-review/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── weekly_kpi_collect.py
```

- `SKILL.md`：skill 的主说明，包含触发场景、评分维度、硬性降档规则和输出格式。
- `scripts/weekly_kpi_collect.py`：从目标 git 仓库采集最近提交、变更文件、代码行数和推荐质量检查命令。
- `agents/openai.yaml`：agent 展示名称、简短说明和默认提示词配置。

## 安装

使用 skills CLI 安装：

```bash
npx skills add https://github.com/qunwang6/kpi-weekly-code-review
```

安装后，支持 Codex、Claude Code、Cursor 等兼容 Agent Skills 的编码助手按需加载该 skill。

## 使用方式

安装后，在 Claude Code 或 Codex 中打开要评估的代码仓库，然后直接用自然语言触发该 skill。

评估当前项目最近一周的整体表现：

```text
使用 kpi-weekly-code-review，分析当前项目最近一周的代码提交和质量，按 KPI 绩效标准给出评分、证据和改进建议。
```

评估指定开发者：

```text
使用 kpi-weekly-code-review，只评估 Alice 最近 7 天的提交，结合测试结果和 diff 风险给出 KPI 等级。
```

评估当前 feature branch 相对主干的工作：

```text
使用 kpi-weekly-code-review，基于当前分支相对 main 的变更，做一次周度代码 KPI review。
```

指定时间范围：

```text
使用 kpi-weekly-code-review，评估 2026-05-08 以来的代码提交，输出中文 KPI 评分报告。
```

在 Claude Code 或 Codex 中，agent 会按需运行 `scripts/weekly_kpi_collect.py` 收集 git 证据，并结合可用的测试、lint、typecheck、diff 风险和项目上下文给出结论。

如需手动采集证据，也可以在目标仓库根目录运行：

```bash
python3 /Users/qun/.codex/skills/kpi-weekly-code-review/scripts/weekly_kpi_collect.py --days 7
```

## 推荐评估流程

1. 在目标仓库确认根目录：

   ```bash
   git rev-parse --show-toplevel
   ```

2. 运行 `weekly_kpi_collect.py` 收集最近一周证据。

3. 根据项目类型运行可用的质量检查，例如：

   ```bash
   npm test
   npm run lint
   npm run typecheck
   pytest
   ruff check .
   go test ./...
   cargo test
   ```

4. 重点查看高风险 diff，例如核心业务逻辑、接口边界、数据库迁移、鉴权、安全、并发、错误处理和测试文件。

5. 按评分维度打分，并结合硬性降档规则确定最终等级。

6. 用中文输出最终 KPI 评分、证据、分项分和改进建议。

## 默认权重

| 维度 | 权重 |
| --- | ---: |
| Delivery | 30% |
| Code quality | 25% |
| Defect risk | 20% |
| Testing | 10% |
| Collaboration | 10% |
| Initiative | 5% |

`Defect risk` 按低风险得高分处理：`10` 代表风险很低，`0` 代表严重风险。

## 硬性降档规则

- 如果测试、类型检查或 lint 失败，且失败由本周变更造成，最高不超过 `B+`。
- 如果存在生产破坏、未 review 的破坏性迁移、提交密钥或安全回归，最高不超过 `B`。
- 如果交付内容大多未合并、不可运行或无法验证，最高不超过 `B`。
- 如果有多次延期、低质量代码、敷衍周报、负向协作或流程违规等明确证据，最高不超过 `C++`。
- 只有在严重不足证据充分时，才评为 `C+` 或 `C`。
- 没有团队级复用价值、文档沉淀、指导他人、重大风险预防等证据时，不应给 `A++`。

## 输出格式

默认用中文输出：

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

如果证据不足，应明确说明哪些信息不可得，并给出暂定等级，例如 `暂定 B+`，不要伪装成确定结论。

## 证据原则

- 提交数只能作为背景信息，不能直接等同于绩效。
- 代码行数需要排除 lockfile、生成文件、vendor、构建产物、快照和格式化噪音后再判断。
- 没有测试不一定低分，但必须有低风险或其他验证证据支撑。
- 大 diff、模糊提交、缺少复现说明、无验证记录会降低可信度。
- 个人评分与项目评分要分开；使用 `--author` 时，不应把无关仓库问题归因给该开发者。

## 示例提示词

```text
分析当前项目最近一周的代码提交和质量，按 KPI 绩效标准给出评分、证据和改进建议。
```

```text
只评估 Alice 最近 7 天的提交，结合测试结果和 diff 风险给出 KPI 等级。
```

```text
基于当前 feature branch 相对 main 的变更，做一次周度代码 KPI review。
```
