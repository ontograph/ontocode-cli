# Qt Unit Test Generate — Skill 架构设计

## 目标

为已有 Qt 源码项目和新开发 Qt 项目自动生成单元测试，核心原则：

1. 按传统测试理论分级设计（不只是覆盖率）
2. 有效拦截高优先级问题（风险驱动，不是盲目覆盖）
3. 利用代码图谱技术做智能分析和优先级排序
4. 生成的测试符合 Qt Test 框架规范，可编译可运行

## 设计哲学

传统单元测试生成的通病是"高覆盖率低价值"——行覆盖率高，但测试只在跑
happy path，漏掉了边界、异常、交互缺陷。本 Skill 的核心理念是：

  风险驱动 + 理论分级 + 图谱引导 = 有效拦截

具体而言：
  - 不追求 100% 覆盖率，而是追求高风险路径的高强度覆盖
  - 用经典测试设计理论（等价类、边界值、判定表、状态转换）保证设计质量
  - 用代码图谱（调用图、依赖图）识别高风险节点和关键路径
  - 用变异测试验证测试集的有效性（测试能不能真正发现 bug）

## 工作流阶段设计

阶段命名映射到测试专家的心智过程，不是抽象编号。

```
Stage 0: 项目勘察 (Survey)
    ↓
Stage 1: 代码图谱构建 (Code Graph)
    ↓
Stage 2: 风险分析与优先级排序 (Risk Prioritization)
    ↓
Stage 3: 测试分级设计 (Test Design)
    ↓
Stage 4: 测试代码生成 (Test Generation)
    ↓
Stage 5: 构建验证与有效性度量 (Validation)
    ↓
Stage 6: 迭代优化 (Iteration)
```

### Stage 0: 项目勘察 (Survey)

测试专家拿到一个项目时，第一件事不是写测试，而是了解项目。

做什么:
  - 检测 Qt 版本 (Qt5/Qt6)、构建系统 (CMake/qmake)
  - 扫描项目结构：源码目录、头文件、已有测试目录
  - 识别已有测试 (tests/ autotests/ 目录、CMakeLists 中的 enable_testing())
  - 分析构建配置：编译参数、链接依赖、QT 模块依赖
  - 生成 state.json，记录项目元信息

输出:
  - state.json: { project_dir, qt_version, build_system, source_dirs,
    header_dirs, existing_tests, qt_modules, compiler_flags }
  - survey-report.md: 项目结构摘要

### Stage 1: 代码图谱构建 (Code Graph)

用 libclang 解析源码，构建两种图谱：

1. 调用图谱 (Call Graph)
   - 节点：函数/方法
   - 边：A 调用 B
   - 从 libclang AST 提取 CALL_EXPR → referenced FunctionDecl

2. 依赖图谱 (Dependency Graph)
   - 节点：类/文件
   - 边：A 依赖 B (#include, 继承, 组合)
   - 从 AST 提取 RecordDecl 继承关系和 IncludeDirective

3. 复杂度图谱
   - 每个函数/方法的圈复杂度 (McCabe)
   - 从 AST 的控制流结构统计 (if/for/while/switch/case/&&/||/?:)

脚本: scripts/build_call_graph.py
  - 输入：源码目录列表、编译参数
  - 输出：call_graph.json (networkx 序列化为 node-link format)
  - 输出：dependency_graph.json
  - 输出：complexity_report.json

输出:
  - call_graph.json: 调用图谱 (节点=函数, 边=调用关系)
  - dependency_graph.json: 依赖图谱 (节点=类, 边=依赖关系)
  - complexity_report.json: 每个函数的圈复杂度和参数信息

### Stage 2: 风险分析与优先级排序 (Risk Prioritization)

基于代码图谱做风险评分，决定哪些函数/方法最需要测试。

风险评分模型 (Risk Score = 0-100):

  R(f) = w1 * Complexity(f)      # 圈复杂度归一化 (0-1)
       + w2 * Centrality(f)        # 图中心性 (被调用次数/入度)
       + w3 * FanOut(f)           # 扇出 (调用其他函数数量)
       + w4 * BranchDepth(f)      # 所在调用链深度
       + w5 * ChangeRate(f)       # 变更频率 (git log, 已有项目)
       + w6 * PublicSurface(f)    # 公共接口权重

  默认权重: w1=0.30, w2=0.20, w3=0.15, w4=0.10, w5=0.15, w6=0.10
  权重可配置，存在 state.json 中。

图谱分析算法 (networkx):
  - 入度 (in_degree): 被多少函数调用 — 核心函数
  - PageRank: 识别图谱中的关键节点
  - 最短路径: 识别入口点到关键函数的路径
  - 强连通分量 (SCC): 识别循环依赖集群
  - 桥边 (bridges): 识别高耦合连接点

优先级分级:
  P0 (必须测试): Risk Score >= 70, 或圈复杂度 >= 15, 或 PageRank top 5%
  P1 (应该测试): Risk Score >= 40, 或圈复杂度 >= 8
  P2 (建议测试): Risk Score >= 20
  P3 (可选测试): Risk Score < 20, 简单 getter/setter/trivial

脚本: scripts/prioritize_targets.py
  - 输入：call_graph.json, complexity_report.json, git log (可选)
  - 输出：priority_report.json
  - 输出：priority_report.md (人可读报告)

### Stage 3: 测试分级设计 (Test Design)

这是核心阶段。按经典测试理论分级设计测试用例。

#### 测试设计级别 (Test Design Levels)

Level 0 — 基础验证 (Smoke Test)
  目标：函数能正常调用并返回，不崩溃
  技术：无，只需一次正常调用
  覆盖目标：语句覆盖
  适用：P3 级别的简单函数

Level 1 — 规范测试 (Specification-Based)
  目标：按函数规范验证输入输出关系
  技术：
    - 等价类划分 (Equivalence Partitioning)
    - 边界值分析 (Boundary Value Analysis)
    - 决策表测试 (Decision Table Testing)
  覆盖目标：分支覆盖 + 边界覆盖
  适用：P2/P1 级别的函数

Level 2 — 结构测试 (Structure-Based)
  目标：覆盖函数内部所有执行路径
  技术：
    - 分支覆盖 (Branch Coverage)
    - 条件覆盖 (Condition Coverage)
    - 基路径测试 (Basis Path Testing) — 基于 McCabe 圈复杂度
    - 路径覆盖 (Path Coverage, 限于可行路径)
  覆盖目标：分支覆盖 >= 90%, 条件覆盖 >= 80%
  适用：P1/P0 级别的函数

Level 3 — 交互测试 (Interaction Test)
  目标：验证函数与其调用链中其他函数的交互正确性
  技术：
    - 调用链路径测试 (从调用图谱提取)
    - 边界接口测试 (参数传递、返回值链)
    - Mock/Stub 对下游依赖的验证 (QSignalSpy 验证信号)
  覆盖目标：关键调用链路径覆盖
  适用：P0 级别 + 高入度函数

Level 4 — 故障注入测试 (Fault Injection / Mutation-Guided)
  目标：验证测试集能否发现真实缺陷
  技术：
    - 变异测试 (Mutation Testing) 生成变异体
    - 错误猜测 (Error Guessing) 基于经验
    - 边界故障注入 (溢出、空指针、越界)
  覆盖目标：变异得分 (Mutation Score) >= 80%
  适用：P0 级别的核心函数

#### 各级别与 Qt Test 的映射

| 设计级别 | Qt Test 实现方式 |
|---------|-----------------|
| Level 0 | 基本 QVERIFY + 一次调用 |
| Level 1 | 数据驱动测试 (_data() + QFETCH + QCOMPARE) |
| Level 2 | 多个测试函数 + QVERIFY2 带消息 |
| Level 3 | QSignalSpy + Mock 对象 + 调用链验证 |
| Level 4 | 变异测试脚本 + QTest::qExec 子测试 |

### Stage 4: 测试代码生成 (Test Generation)

根据 Stage 3 的设计，生成符合 Qt Test 规范的测试代码。

生成规则:
  - 每个被测类生成一个 TestClass 继承 QObject
  - 测试函数命名: test_<被测函数>_<场景>
  - 数据驱动测试: test_<被测函数>_data() + test_<被测函数>()
  - init()/cleanup() 管理测试夹具
  - QTEST_MAIN(TestClass) 入口
  - CMakeLists.txt 集成 CTest

模板文件:
  templates/test_class_header.tmpl  — 测试类头文件
  templates/test_class_source.tmpl — 测试类源文件
  templates/cmake_test_module.tmpl — CMake 测试模块配置
  templates/data_driven_test.tmpl  — 数据驱动测试模板

输出:
  - tests/test_<classname>.h
  - tests/test_<classname>.cpp
  - tests/CMakeLists.txt (或追加到现有)
  - test_design_doc.md: 每个测试的设计依据 (级别、技术、依据)

### Stage 5: 构建验证与有效性度量 (Validation)

生成的测试必须能编译、能运行、能真正拦截缺陷。

验证步骤:
  1. 编译测试: cmake + make (捕获编译错误，自动修复)
  2. 运行测试: ctest --output-on-failure (确保全部通过)
  3. 覆盖率分析: gcov + lcov (生成分级覆盖率报告)
     - 检查 P0 函数分支覆盖 >= 90%
     - 检查 P1 函数分支覆盖 >= 80%
     - 不强制 P2/P3 的覆盖率
  4. 变异测试 (可选): 对 P0 函数做变异测试
     - 变异算子: 算术运算符替换、逻辑运算符替换、边界条件修改
     - 变异得分 >= 80% 视为通过
  5. 生成验证报告

脚本: scripts/validate_coverage.py
  - 输入：测试构建目录
  - 输出：coverage_report.json (按函数、按级别的覆盖率)
  - 输出：validation_report.md

### Stage 6: 迭代优化 (Iteration)

分析覆盖率缺口和变异得分，补充测试。

做什么:
  - 识别变异得分 < 80% 的函数 → 补充 Level 4 测试
  - 识别分支覆盖不足的函数 → 补充 Level 2 测试
  - 识别未覆盖的边界值 → 补充 Level 1 测试
  - 对新增代码或变更代码重新执行 Stage 1-5

## 文件结构

```
qt-unit-test-generate/
├── SKILL.md                              # L0 索引：触发条件、全局原则、阶段映射
├── references/
│   ├── test-design-theory.md             # 测试设计理论与分级详解
│   ├── code-graph-analysis.md            # 代码图谱构建与分析方法
│   ├── risk-prioritization.md            # 风险评分模型与优先级算法
│   ├── qt-test-patterns.md               # Qt Test 框架模式与最佳实践
│   ├── cmake-integration.md               # CMake/CTest 集成模式
│   └── mutation-testing.md               # 变异测试方法与算子定义
├── scripts/
│   ├── build_call_graph.py               # 构建 AST 级调用图谱 (libclang)
│   ├── analyze_complexity.py             # 圈复杂度分析
│   ├── prioritize_targets.py             # 风险评分与优先级排序
│   ├── generate_test_skeleton.py         # 生成测试骨架代码
│   ├── validate_coverage.py              # 编译运行+覆盖率验证
│   └── mutation_score.py                 # 变异测试得分计算
├── templates/
│   ├── test_class_header.tmpl            # 测试类头文件模板
│   ├── test_class_source.tmpl            # 测试类源文件模板
│   ├── cmake_test_module.tmpl            # CMake 测试模块模板
│   └── data_driven_test.tmpl             # 数据驱动测试模板
└── state.json                            # 工作流状态 (各阶段间传递)
```

## 技术依赖

必需 (已验证可用):
  - libclang (Python binding) — AST 解析、调用图谱
  - networkx — 图谱分析算法
  - Qt5Test / Qt6Test — 测试框架
  - cmake + ctest — 构建和运行
  - gcov + lcov — 覆盖率分析

可选 (需安装):
  - lizard — 复杂度分析 (pip install lizard)
  - tree-sitter — 增量解析 (pip install tree-sitter tree-sitter-cpp)
  - mull-runner — C++ 变异测试框架

## 适配已有项目 vs 新项目

已有项目:
  - Stage 0 增量扫描：只分析源码，不修改源码
  - Stage 1 带上编译参数 (从 CMakeCache.txt 或 compile_commands.json 提取)
  - Stage 4 测试文件放已有 tests/ 目录，追加到已有 CMakeLists
  - Stage 2 变更频率权重启用 (git log 分析)

新项目:
  - Stage 0 脚手架：创建 src/ tests/ CMakeLists.txt 标准结构
  - Stage 1 从零构建图谱
  - Stage 4 创建独立 tests/ 目录
  - Stage 2 变更频率权重禁用 (无 git 历史)

## state.json Schema

```json
{
  "project_dir": "<absolute path>",
  "mode": "existing|new",
  "artifact_dir": "<absolute path>",
  "qt_version": "5|6",
  "build_system": "cmake|qmake",
  "source_dirs": ["src/", "lib/"],
  "header_dirs": ["include/", "src/"],
  "existing_tests": "tests/|none",
  "qt_modules": ["Core", "Widgets", "Network"],
  "compiler_flags": ["-std=c++14", "-fPIC"],
  "stage": {
    "survey": { "completed": true, "report": "survey-report.md" },
    "code_graph": { "completed": false, "call_graph": "call_graph.json" },
    "risk": { "completed": false, "report": "priority_report.json" },
    "test_design": { "completed": false, "designs": [] },
    "generation": { "completed": false, "files": [] },
    "validation": { "completed": false, "results": null },
    "iteration": { "completed": false, "rounds": 0 }
  },
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
