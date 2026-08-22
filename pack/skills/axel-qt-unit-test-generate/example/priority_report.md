# 风险分析报告 (Stage 2)

## 优先级分布

| 优先级 | 数量 | 测试要求 | 覆盖目标 |
|--------|------|---------|---------|
| P0 | 2 | Level 4 (含变异测试) | 分支>=90%, 变异>=80% |
| P1 | 5 | Level 2 (结构测试) | 分支>=90%, 条件>=80% |
| P2 | 4 | Level 1 (规范测试) | 分支覆盖+边界 |
| P3 | 0 | Level 0 (Smoke) | 语句覆盖 |

## Top 10 高风险函数

| 排名 | 函数 | 风险分 | 优先级 | 复杂度 | 入度 | 出度 | 文件 |
|------|------|--------|--------|--------|------|------|------|
| 1 | Calculator::add | 54.5 | P1 | 1 | 1 | 0 | src/calculator.cpp |
| 2 | Calculator::sub | 54.5 | P1 | 1 | 1 | 0 | src/calculator.cpp |
| 3 | Calculator::doDivide | 50.0 | P1 | 2 | 1 | 0 | src/calculator.cpp |
| 4 | Calculator::doMultiply | 48.5 | P1 | 1 | 1 | 0 | src/calculator.cpp |
| 5 | Calculator::compute | 41.0 | P1 | 2 | 0 | 4 | src/calculator.cpp |
| 6 | Calculator::formatResult | 39.5 | P2 | 11 | 0 | 0 | src/calculator.cpp |
| 7 | Calculator::validateInput | 38.0 | P0 | 10 | 0 | 0 | src/calculator.cpp |
| 8 | Calculator::parseNumber | 36.5 | P0 | 9 | 0 | 0 | src/calculator.cpp |
| 9 | Calculator::classify | 27.5 | P2 | 3 | 0 | 0 | src/calculator.cpp |
| 10 | Calculator::divide | 26.0 | P2 | 2 | 0 | 0 | src/calculator.cpp |

## 特殊规则触发

| 函数 | 规则 | 优先级 |
|------|------|--------|
| Calculator::validateInput | security sensitive | P0 |
| Calculator::parseNumber | security sensitive | P0 |
