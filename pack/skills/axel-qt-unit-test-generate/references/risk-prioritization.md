# 风险评分模型与优先级算法

## 概述

本文件定义 Stage 2 的风险评分模型。目标是识别哪些函数最需要测试，
而非盲目追求全量覆盖。

## 风险评分公式

R(f) = w1 * Complexity(f) + w2 * Centrality(f) + w3 * FanOut(f)
     + w4 * BranchDepth(f) + w5 * ChangeRate(f) + w6 * PublicSurface(f)

归一化: 每个因子归一化到 [0, 1]，R(f) 最终值域 [0, 100]

## 评分因子

### 1. Complexity (圈复杂度) — 权重 0.30

来源: Stage 1 的 complexity_report.json

归一化:
  complexity_score = min(V(f) / 20, 1.0) * 100

  V(f) >= 20 视为最高风险 (满分)
  V(f) = 1 视为最低风险 (0 分)

阈值参考 (McCabe 1976):
  1-10: 低风险
  11-15: 中等风险
  16-20: 高风险
  > 20: 极高风险

### 2. Centrality (图中心性) — 权重 0.20

来源: networkx in_degree

归一化:
  max_in_degree = max(所有函数的 in_degree)
  centrality_score = (in_degree(f) / max_in_degree) * 100

解读: 被越多的函数调用，越核心，越需要测试。
补充指标: PageRank top 5% 直接给满分。

### 3. FanOut (扇出) — 权重 0.15

来源: networkx out_degree

归一化:
  max_out_degree = max(所有函数的 out_degree)
  fanout_score = (out_degree(f) / max_out_degree) * 100

解读: 调用越多的其他函数，交互越复杂，越需要交互测试。

### 4. BranchDepth (调用链深度) — 权重 0.10

来源: 从入口点到 f 的最长路径长度

归一化:
  max_depth = max(所有函数的 branch_depth)
  depth_score = (depth(f) / max_depth) * 100

解读: 离入口点越远，调用链越长，问题越难定位。

### 5. ChangeRate (变更频率) — 权重 0.15

来源: git log (已有项目)

归一化:
  max_commits = max(所有文件的提交数)
  change_rate_score = (commits(f) / max_commits) * 100

解读: 变更越频繁，引入新 bug 的概率越高。

注意:
  - 新项目无 git 历史 → 此因子设为 0，权重重新分配
  - 权重重分配: w5=0, 其他权重按比例放大
  - 可通过 state.json 配置关闭

### 6. PublicSurface (公共接口权重) — 权重 0.10

来源: AST 中函数的访问修饰符

判定:
  public 槽/signal: 100
  public 方法: 80
  protected 方法: 40
  private 方法: 20
  匿名命名空间: 10

解读: 公共接口是外部依赖点，出问题影响范围大。

## 优先级分级

| 优先级 | Risk Score | 测试要求 | 覆盖目标 |
|--------|-----------|---------|---------|
| P0 | >= 70 | Level 4 (含变异测试) | 分支>=90%, 变异>=80% |
| P1 | >= 40 | Level 2 (结构测试) | 分支>=90%, 条件>=80% |
| P2 | >= 20 | Level 1 (规范测试) | 分支覆盖+边界 |
| P3 | < 20 | Level 0 (Smoke) | 语句覆盖 |

## 特殊规则 (覆盖评分)

以下情况直接提升优先级，不论 Risk Score:

1. 圈复杂度 >= 15 → 直接 P0
2. PageRank top 5% → 至少 P1
3. 循环依赖 SCC 成员 → 至少 P1
4. 安全敏感函数 (认证/权限/加密/数据处理) → 至少 P0
   检测: 函数名/文件名包含 auth, login, password, encrypt, decrypt,
   parse, validate, check, verify, sanitize, escape 等

## 权重配置

默认权重可通过 state.json 的 risk_weights 字段调整:

```json
{
  "risk_weights": {
    "complexity": 0.30,
    "centrality": 0.20,
    "fan_out": 0.15,
    "branch_depth": 0.10,
    "change_rate": 0.15,
    "public_surface": 0.10
  }
}
```

已有项目 vs 新项目的权重差异:

| 因子 | 已有项目 | 新项目 | 说明 |
|------|---------|--------|------|
| complexity | 0.30 | 0.35 | 新项目无变更数据，复杂度权重提高 |
| centrality | 0.20 | 0.25 | 中心性权重提高 |
| fan_out | 0.15 | 0.20 | 扇出权重提高 |
| branch_depth | 0.10 | 0.10 | 不变 |
| change_rate | 0.15 | 0.00 | 新项目无 git 历史 |
| public_surface | 0.10 | 0.10 | 不变 |

## 输出格式

priority_report.json:
```json
{
  "functions": [
    {
      "id": "Calculator::compute",
      "name": "compute",
      "class": "Calculator",
      "file": "src/calculator.cpp",
      "line": 45,
      "risk_score": 82.5,
      "priority": "P0",
      "factors": {
        "complexity": 75.0,
        "centrality": 60.0,
        "fan_out": 50.0,
        "branch_depth": 100.0,
        "change_rate": 0,
        "public_surface": 80.0
      },
      "complexity": 12,
      "in_degree": 3,
      "out_degree": 2,
      "branch_depth": 5,
      "special_rules": ["complexity >= 15"]
    }
  ],
  "summary": {
    "total": 50,
    "P0": 5,
    "P1": 12,
    "P2": 20,
    "P3": 13
  }
}
```

priority_report.md: 人可读的风险分析报告，包含:
- 优先级分布统计
- Top 10 高风险函数清单
- 特殊规则触发的函数清单
- 循环依赖 SCC 报告
- 桥边分析报告
