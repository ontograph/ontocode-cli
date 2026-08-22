# 测试设计文档 (Stage 3)

## 设计依据

测试用例按经典测试理论分 5 级设计:
- Level 0 (Smoke): 基础验证, 确保函数可调用不崩溃
- Level 1 (Specification): 等价类划分 + 边界值分析 + 判定表
- Level 2 (Structure): 分支覆盖 + 条件覆盖 + 基路径测试
- Level 3 (Interaction): 调用链路径 + 信号验证 + Mock
- Level 4 (Fault Injection): 变异测试 + 错误猜测

## 类: Calculator

| 函数 | 优先级 | 风险分 | 测试级别 | 复杂度 | 设计技术 |
|------|--------|--------|---------|--------|---------|
| add | P1 | 54.5 | L2 | 1 | Smoke + 等价类+边界值 + 基路径(V=1) |
| sub | P1 | 54.5 | L2 | 1 | Smoke + 等价类+边界值 + 基路径(V=1) |
| doDivide | P1 | 50.0 | L2 | 2 | Smoke + 等价类+边界值 + 基路径(V=2) |
| doMultiply | P1 | 48.5 | L2 | 1 | Smoke + 等价类+边界值 + 基路径(V=1) |
| compute | P1 | 41.0 | L2 | 2 | Smoke + 等价类+边界值 + 基路径(V=2) |
| formatResult | P2 | 39.5 | L1 | 11 | Smoke + 等价类+边界值 |
| validateInput | P0 | 38.0 | L4 | 10 | Smoke + 等价类+边界值 + 基路径(V=10) + QSignalSpy+Mock + 变异测试 |
| parseNumber | P0 | 36.5 | L4 | 9 | Smoke + 等价类+边界值 + 基路径(V=9) + QSignalSpy+Mock + 变异测试 |
| classify | P2 | 27.5 | L1 | 3 | Smoke + 等价类+边界值 |
| divide | P2 | 26.0 | L1 | 2 | Smoke + 等价类+边界值 |
| Calculator | P2 | 24.5 | L1 | 1 | Smoke + 等价类+边界值 |
