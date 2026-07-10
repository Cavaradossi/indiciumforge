# IndiciumForge

<p align="center">
  <b>面向金融研究工作流的开源核心工具包</b><br>
  用可复现的流程、标准化的输出工件和清晰的扩展边界，把公开框架与私有数据、因子逻辑和研究配方隔离开来。
</p>

<p align="center">
  <a href="./README.md">English README</a>
</p>

---

## 项目一句话

**IndiciumForge** 是一个开源核心（open core），帮助你搭建**可复现的金融研究工作流**：定义流程步骤、写出可检查的输出工件、接入自己的数据源与因子逻辑，同时把私有实现留在仓库之外。

> 默认示例使用合成数据。本项目产出的是**研究工作流输出**，用于人工审阅与流程验证，**不是**自动下单系统，**不是**券商网关，**也不构成**任何形式的投资建议。

---

## 它解决什么问题？

很多金融研究团队在本地积累了大量脚本、表格和阶段性结论，但常见痛点是：

- 流程步骤散落在笔记本和私有脚本里，难以复现；
- 输出格式不统一，换人或换机器后很难核对「当时到底算了什么」；
- 想把核心框架开源，又担心 proprietary 数据路径、因子逻辑和研究配方被一并暴露；
- 升级或重构时，缺少「对答案」的方式验证新流程是否仍产生预期输出。

IndiciumForge 把这些需求收敛成三件事：

1. **可重复的研究流程链**（workflow + recipe）  
2. **带版本信息的输出工件**（artifact）  
3. **可插拔的私有扩展**（extension pack），无需 fork 核心代码  

项目从一套**内部金融研究工作流**中抽象并泛化而来，目标是成为可复用的开源工具包，而不是某一家机构的私有脚本合集。

---

## 它适合谁？

| 角色 | 典型场景 |
| --- | --- |
| 量化 / 研究工程师 | 把日度研究流程串成可复现的 CLI 工作链 |
| 流程作者 | 定义研究配方（recipe）和各阶段交接格式 |
| 扩展开发者 | 用 YAML 包装私有数据源、因子检测器、配方实现 |
| 需要流程治理的团队 | 对输出做工件完整性检查，并与参考结果对比 |

---

## 它不适合谁？

- 需要**实盘下单、报单路由、组合管理**的团队 — 请使用交易/执行类框架；
- 希望「装完就能给出买卖信号」的用户 — 本项目不提供策略推荐或绩效承诺；
- 只想跑一个单次回测脚本、不需要流程契约与输出治理的场景 — 可能过重；
- 期望开源仓库内包含真实行情路径、账户数据或 proprietary 因子的用户 — 这些应放在**私有扩展包**中。

---

## 快速开始

环境：Python 3.10+。

```bash
cd <仓库根目录>
python -m pip install -e packages/indiciumforge-core \
                       -e packages/indiciumforge-workflow \
                       -e packages/indiciumforge-cli \
                       -e ".[dev]"
indiciumforge --help
indiciumforge workflow synthetic-e2e \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/indiciumforge-demo \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml \
  --preopen-review-fixture tests/fixtures/workflow/preopen_buy_point_review_demo.csv
```

Windows 请将 `/tmp/...` 换成可写目录，例如 `%TEMP%\indiciumforge-demo`。

运行成功后，可在 `--artifact-root` 下看到按日期与阶段组织的 JSON/CSV 输出工件。

---

## 核心能力

| 能力 | 说明 |
| --- | --- |
| 工作流 CLI | `indiciumforge workflow ...` 运行合成端到端示例与流程链 |
| 输出工件契约 | 各阶段输出带 schema 标识，便于机器读取与人工核对 |
| 输出完整性检查 | `indiciumforge artifact audit` 检查文件是否齐全、格式是否一致 |
| 参考输出对比 | 与仓库内参考样例或你本地的参考树做结构化对比（parity） |
| 扩展包加载 | 数据源、因子、配方通过 YAML + entry point 接入，无需改核心 |
| 合成演示数据 | 默认 CI 与 quickstart 不依赖真实行情路径或 API 密钥 |

术语说明见 [docs/GLOSSARY.md](docs/GLOSSARY.md)。

---

## 开源核心与私有扩展

**本仓库（开源核心）包含：**

- 流程接口（ports）、输出 schema、演示用合成数据；
- 工作流运行器、CLI、输出完整性检查与对比工具；
- 扩展模板与作者指南。

**应放在你本地私有包中的内容：**

- 真实行情/基本面数据适配器；
- proprietary 因子与信号逻辑；
- 生产级研究配方实现；
- 任何含凭证、账户信息或不可公开路径的配置。

入门：[docs/EXTENSION_AUTHOR_GUIDE.md](docs/EXTENSION_AUTHOR_GUIDE.md) · 模板：[examples/private_extension_template/](examples/private_extension_template/)

---

## 与交易框架的边界

IndiciumForge 关注的是**研究流程与可审计输出**，不是执行层：

| 维度 | IndiciumForge | 常见交易 / 回测框架 |
| --- | --- | --- |
| 主要产出 | 分阶段 JSON/CSV 工件与检查报告 | 订单、持仓、损益曲线 |
| 执行 | 明确不在范围内 | 常含模拟或实盘接口 |
| 扩展方式 | 端口 + 扩展包契约 | 策略类 / 回调 |
| 回归方式 | 输出对比、参考样例测试 | 净值或成交记录对比 |

---

## 当前局限

- 默认 quickstart 使用**合成 fixtures**，不代表真实市场数据质量；
- 输出完整性检查验证**结构与 schema**，不证明经济含义正确；
- 与参考输出的对比是**研究流程层面的对答案**，不是生产环境认证；
- v2.1 计划中的 **OpenBB 公开演示**尚未实现（见下文）；
- 部分历史迁移与签核材料面向维护者，见英文 README 的 Maintainer notes。

---

## 下一步：OpenBB 公开演示

计划在 v2.1.0 提供基于 [OpenBB](https://github.com/OpenBB-finance/OpenBB) 的**公开数据**演示：一条命令、几分钟内产出小型确定性工件树，无需私有文件或 API 密钥进仓库。

详情（规划文档，**当前未实现**）：[docs/OPENBB_PUBLIC_DEMO_PLAN.md](docs/OPENBB_PUBLIC_DEMO_PLAN.md)

---

## 安装和测试

### 从 PyPI 安装（v2.0.1）

```bash
pip install indiciumforge-cli==2.0.1
```

也可分别安装 `indiciumforge-core`、`indiciumforge-workflow`。

### 从源码安装

见上文快速开始中的 `pip install -e ...` 命令。

### 运行测试

```bash
python -m pytest -q
python -m ruff check .
```

---

## 文档入口

### 用户与扩展开发者

| 主题 | 路径 |
| --- | --- |
| 术语表（推荐先读） | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| 扩展作者指南 | [docs/EXTENSION_AUTHOR_GUIDE.md](docs/EXTENSION_AUTHOR_GUIDE.md) |
| 扩展模板 | [examples/private_extension_template/](examples/private_extension_template/) |
| OpenBB 公开演示计划 | [docs/OPENBB_PUBLIC_DEMO_PLAN.md](docs/OPENBB_PUBLIC_DEMO_PLAN.md) |
| 工作流会话模型 | [docs/WORKFLOW_SESSION_MODEL.md](docs/WORKFLOW_SESSION_MODEL.md) |
| 安全说明 | [SECURITY.md](SECURITY.md) |
| 发布说明 | [RELEASE_NOTES.md](RELEASE_NOTES.md) |

### 维护者与贡献者

| 主题 | 路径 |
| --- | --- |
| 系统结构图 | [docs/SYSTEM_MAP.md](docs/SYSTEM_MAP.md) |
| 能力登记表 | [CAPABILITY_REGISTER.md](CAPABILITY_REGISTER.md) |
| 设计决策记录（ADR） | [docs/decisions/](docs/decisions/) |
| 迁移路线图 | [docs/MIGRATION_ROADMAP.md](docs/MIGRATION_ROADMAP.md) |
| Agent 协作指南 | [docs/AGENT_QUICKSTART.md](docs/AGENT_QUICKSTART.md) · [AGENTS.md](AGENTS.md) |
| PyPI 发布清单 | [docs/PYPI_RELEASE_CHECKLIST.md](docs/PYPI_RELEASE_CHECKLIST.md) |

---

## 许可证

[Apache License 2.0](LICENSE)
