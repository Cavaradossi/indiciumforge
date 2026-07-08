# workflow market gate calibration audit - 2026-06-24

本报告仅用于研究复核，不是实盘买入指令。

- strict execution gate stays strict; this audit is for rule calibration.
- candidate_count: 1
- strict_count: 0
- observation_count: 0
- watch_count: 1
- rejected_count: 1
- quality_gate_warning: 严格执行门为0：不代表市场没有机会，需同时查看主动观察和遗漏审计
- outcome_status: 待后续收盘数据回填

## Top Missed / Active Watch

|   代码 | 股票名称   | 候选等级                | 盘面门控结论   | 主动观察级别   | 主动观察原因                                                                                                       | 剔除原因            | 观察原因   |
|-------:|:-----------|:------------------------|:---------------|:---------------|:-------------------------------------------------------------------------------------------------------------------|:--------------------|:-----------|
|      6 | 强势C      | C-历史样本/行情可能后段 | 剔除           | 遗漏审计       | 盘面共振=强方向;短线观察等级=高;盯盘分层=重点盯盘;主线强度=strong_short_pulse;形态可信度=高;C级但具备强势/承接线索 | 持有周期分层=仅复盘 |            |

## Notes

- 本审计不放松market-gate严格执行门
- 财务红旗是观察风险上下文，不是主动观察层的一票否决
- C级候选需区分形态走坏与规则未覆盖的强势样本