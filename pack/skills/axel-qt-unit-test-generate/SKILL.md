---
name: axel-qt-unit-test-generate
description: "Generate risk-ranked Qt Test unit-test candidates, analyze coverage quality, and prioritize high-risk C++ functions."
version: 0.2.1
author: ut000520, Hermes Agent
license: Apache-2.0
platforms: [linux]
metadata:
  vendored_from: https://github.com/eric2023/qt-unit-test-generate
  vendored_ref: ee11ff31f6f0b31b5a4ab8cb9c4cf9ee904b9c3e
  vendored_on: "2026-08-22"
  hermes:
    tags: [qt, unit-test, code-graph, mutation-testing, risk-driven]
    related_skills: [test-driven-development, systematic-debugging]
---

# Qt Unit Test Generate Skill

为 Qt 项目（已有源码或新开发）自动生成分级单元测试。核心是风险驱动 +
理论分级 + 代码图谱引导，确保测试有效拦截高优先级问题，而非只追覆盖率。

## Axel Scope

- Target C++ Qt code under `qt/`. Generated tests are review candidates until
  they are built, run, and promoted into the repository-owned test suite.
- Do not trust the upstream LLVM-13 example path blindly. Resolve the available
  `libclang` with `llvm-config`, `pkg-config`, or the project build configuration.
- Run headless validation with `QT_QPA_PLATFORM=offscreen` and cap builds at
  `-j8`.
- Keep mutation runs in a disposable build directory; never edit product sources
  in place.
- The upstream README incorrectly labels the project MIT; the authoritative
  bundled LICENSE and this skill declare Apache-2.0.

## 核心原则

1. 风险驱动，不是盲目覆盖。优先测试高复杂度、高扇出、高入度的核心函数。
2. 理论分级设计。按经典测试设计理论（等价类、边界值、判定表、基路径、变异）
   分 5 个级别设计用例，每个级别有明确目标和技术。
3. 图谱引导。用 libclang 构建 AST 级调用图谱和依赖图谱，用 networkx 分析
   中心性、关键路径、强连通分量，驱动优先级排序。
4. 生成可编译可运行的 Qt Test 代码。不是伪代码或描述，是直接能 ctest 的产物。
5. 有效性度量。不只看覆盖率，用变异得分验证测试集能否真正发现缺陷。

## When to Use

- 用户要为已有的 Qt 项目补充单元测试
- 用户要为新 Qt 项目从零生成单元测试
- 用户要分析现有测试的覆盖质量和有效性
- 用户提到 Qt Test、QTest、Qt 单元测试相关问题
- 用户要从代码图谱/调用关系角度分析测试优先级

Don't use for:
- 非 Qt 项目的测试生成（golang、rust 等）
- 纯性能测试或集成测试
- UI 自动化测试（不在本 Skill 范围）

## Prerequisites

- libclang (Python binding) — 已验证 /usr/lib/llvm-13/lib/libclang.so 可用
- networkx — 图谱分析
- Qt5Test (5.11+) 或 Qt6Test
- cmake 3.16+ + ctest
- gcov + lcov — 覆盖率分析
- Python 3.7+

## 阶段总览

| 阶段 | 名称 | 核心动作 | 脚本 |
|------|------|---------|------|
| 0 | 项目勘察 | 检测 Qt 版本/构建系统/项目结构 | — |
| 1 | 代码图谱 | 构建调用图+依赖图+复杂度 | build_call_graph.py |
| 2 | 风险排序 | 评分+分级 P0-P3 | prioritize_targets.py |
| 3 | 分级设计 | 按理论 5 级设计用例 | — (AI 完成) |
| 4 | 代码生成 | 生成 Qt Test 代码+CMake | generate_test_skeleton.py |
| 5 | 验证度量 | 编译运行+覆盖率 | validate_coverage.py |
| 6 | 变异测试 | 变异得分验证有效性 | mutation_score.py |

## 执行流程

### Stage 0: 项目勘察

1. 确认 project_dir = 当前工作目录
2. 检测 Qt 版本: `pkg-config --modversion Qt5Test` 或 Qt6Test
3. 检测构建系统: 查找 CMakeLists.txt 或 .pro 文件
4. 扫描源码目录结构 (search_files target='files' pattern='*.cpp'/'*.h')
5. 检测已有测试: tests/ autotests/ 目录, CMakeLists 中的 enable_testing()
6. 提取编译参数: 优先 compile_commands.json，否则从 CMakeLists 解析
7. 写 state.json

完成标准: state.json 包含 project_dir, qt_version, build_system, source_dirs,
header_dirs, compiler_flags, mode (existing|new)

### Stage 1: 代码图谱构建

运行 `python3 scripts/build_call_graph.py --state state.json`

脚本用 libclang 解析每个源文件，提取:
- 调用图谱: FunctionDecl → CALL_EXPR → referenced FunctionDecl
- 依赖图谱: RecordDecl 继承关系 + IncludeDirective
- 复杂度: 从 AST 控制流节点统计 McCabe 圈复杂度

输出: call_graph.json, dependency_graph.json, complexity_report.json

完成标准: 三个 JSON 文件生成，节点数 > 0

### Stage 2: 风险分析与优先级排序

运行 `python3 scripts/prioritize_targets.py --state state.json`

用 networkx 分析图谱:
- in_degree: 被调用次数 → 中心性
- PageRank: 关键节点识别
- 最短路径: 入口点到关键函数
- 桥边: 高耦合连接

风险评分: R(f) = w1*Complexity + w2*Centrality + w3*FanOut + w4*BranchDepth
+ w5*ChangeRate + w6*PublicSurface

优先级: P0 (>=70) / P1 (>=40) / P2 (>=20) / P3 (<20)

输出: priority_report.json, priority_report.md

完成标准: 每个函数有 priority 标签和 risk_score

### Stage 3: 测试分级设计

这是 AI 的核心工作阶段，不可脚本化。按以下 5 级设计:

Level 0 (Smoke): 一次正常调用 + QVERIFY。适用 P3。
Level 1 (Specification): 等价类划分 + 边界值分析 + 判定表。适用 P2/P1。
  - 数据驱动: _data() + QFETCH + QCOMPARE
Level 2 (Structure): 分支覆盖 + 条件覆盖 + 基路径测试。适用 P1/P0。
  - 按 McCabe 圈复杂度确定基路径数量
  - 每个独立路径一个测试函数
Level 3 (Interaction): 调用链路径 + 信号验证 + Mock。适用 P0。
  - 从调用图谱提取关键调用链
  - QSignalSpy 验证信号
  - 对下游依赖做 Mock
Level 4 (Fault Injection): 变异测试 + 错误猜测。适用 P0 核心。
  - 变异算子: 算术替换(+→-), 逻辑替换(&&→||), 边界修改(< → <=)
  - 变异得分 >= 80%

设计依据写入 test_design_doc.md。

完成标准: 每个目标函数有明确的测试级别和技术选择

### Stage 4: 测试代码生成

运行 `python3 scripts/generate_test_skeleton.py --state state.json --design test_design_doc.md`

按模板生成:
- 每个被测类一个 TestClass (QObject, Q_OBJECT)
- private slots 测试函数
- 数据驱动测试 _data() 函数
- init()/cleanup() 夹具
- QTEST_MAIN 入口
- CMakeLists.txt 集成 CTest (AUTOMOC, Qt::Test)

输出: tests/test_*.h, tests/test_*.cpp, tests/CMakeLists.txt

完成标准: 测试文件生成，CMake 可配置

### Stage 5: 构建验证与覆盖率度量

运行 `python3 scripts/validate_coverage.py --state state.json`

步骤:
1. cmake + make 编译 (编译错误自动修复)
2. ctest --output-on-failure 运行
3. gcov + lcov 覆盖率分析
4. 分级检查: P0 分支覆盖>=90%, P1>=80%

输出: coverage_report.json, validation_report.md

完成标准: 测试全部通过，覆盖率达标

### Stage 6: 变异测试与迭代优化

运行 `python3 scripts/mutation_score.py --state state.json --all-p0`

变异测试验证测试集的有效性:
1. 对 P0 函数生成变异体 (AOR/ROR/LOR/CRC/RVF 算子)
2. 编译每个变异体, 运行测试集
3. 杀死 (测试失败) → 测试有效; 存活 (测试通过) → 测试有缺口
4. 变异得分 = 杀死 / (杀死 + 存活), 目标 >= 80%

输出: mutation_report.md, mutation_report.json

迭代优化:
- 变异得分 < 80% → 补充 Level 4 测试
- 分支覆盖不足 → 补充 Level 2 测试
- 边界值遗漏 → 补充 Level 1 测试
- 新增/变更代码 → 重跑 Stage 1-6

## 风险评分权重 (可配置)

默认权重 (存在 state.json 的 risk_weights 中):
- complexity: 0.30 (圈复杂度)
- centrality: 0.20 (图中心性/入度)
- fan_out: 0.15 (扇出)
- branch_depth: 0.10 (调用链深度)
- change_rate: 0.15 (变更频率, 已有项目)
- public_surface: 0.10 (公共接口)

## Gotchas

1. libclang 需要 Config.set_library_file('/usr/lib/llvm-13/lib/libclang.so')，
   否则 Python binding 找不到 libclang.so
2. Qt5 项目的编译参数必须包含 -fPIC，否则 libclang 解析可能产生错误诊断
3. compile_commands.json 是最佳参数来源；没有时从 CMakeLists.txt 解析
   但可能遗漏 -I 路径导致 AST 解析不完整
4. libclang 解析 Qt 信号槽需要 moc 生成的文件；对 Q_OBJECT 类的方法，
   signal/slot 声明在 moc 输出中，源文件解析可能看不到
5. ctest 运行需要 QT_QPA_PLATFORM=offscreen (无显示器环境)
6. gcov 覆盖率需要编译时 -fprofile-arcs -ftest-coverage
7. 变异测试修改源码后必须重新编译；在独立 build 目录操作，不污染源码。
   恢复原始源码后必须 `make clean && make`，不能只 `make`——
   否则 stale .o 文件会导致测试结果不可靠 (假失败或假通过)
8. Python 3.7 不支持 := (walrus operator), 脚本避免使用

### 测试代码生成 (Stage 4) 的 Gotchas

9. QFETCH 不支持指针类型 (如 `bool *ok`)。Qt 的 metatype 系统不注册
   指针类型, 会导致 `Q_STATIC_ASSERT_X` 编译错误。生成器必须检测
   指针参数并跳过数据驱动测试 (_data()/_test() 对), 只生成 smoke 桩。
10. 私有方法 (access=='private') 不能从测试类直接调用, 会编译失败。
    生成器应检测 access 标签, 对私有方法只生成注释桩
    ("test indirectly via public callers"), 通过公共接口间接测试。
11. 构造函数和析构函数需要特殊处理: `obj.Calculator()` 是无效 C++。
    构造函数: 生成 `Calculator obj; QVERIFY(true);`。
    析构函数: 生成 `Calculator *obj = new Calculator(); delete obj;`。
12. Smoke test 断言必须按返回类型分支选择安全断言, 否则编译失败:
    - int/double: `QVERIFY(result >= 0 || result < 0)` (恒真)
    - QString: `QVERIFY(!result.isEmpty() || result.isEmpty())` (恒真, 无 operator>=)
    - bool: `QVERIFY(result || !result)` (恒真)
    - 其他类型: `Q_UNUSED(result); QVERIFY(true);`
    - void: 不捕获返回值, `obj.method(args); QVERIFY(true);`
    + TODO 注释标记, 等 AI 补充真实断言后再替换。
    否则骨架生成的测试全部 FAIL, 无法通过 Stage 5 验证。

### 覆盖率分析 (Stage 5) 的 Gotchas

13. ctest 输出有 3 种格式, 解析器必须全部兼容:
    - "N% tests passed, M tests failed out of T"
    - "Total Tests: N, Passed: N, Failed: N"
    - 逐行 "  Test #N: name ... Passed/Failed"
14. lcov 过滤被测库覆盖率时, 优先用 `lcov --extract` 指定源码路径,
    而非 `lcov --remove` 排除系统路径。remove 模式在测试文件无覆盖率
    数据时会过滤掉所有记录, 导致 "no valid records found" 错误。
15. 被测库的 .gcda 文件只在测试运行后生成。如果测试只含 placeholder
    断言 (QVERIFY(true)), 覆盖率数据虽然存在但意义不大。
    validate_coverage.py 应检测此情况并给出 "需补充真实断言" 的建议。
16. Level 1 数据驱动测试对 void 返回函数不能添加 `expected` 列和
    `QFETCH(expected)` — void 方法没有返回值可捕获。模板必须按返回类型
    分支: void 用 `{call_line}` + `{assert_line}` 占位符, 非 void 才
    添加 `QTest::addColumn<ret_type>("expected")` 和 `QFETCH(ret_type, expected)`。

### 代码图谱 (Stage 1) 的 Gotchas

17. libclang 无法从源码可靠区分 Q_SLOTS/slots: 段和普通 public/private 方法。
    moc 关键字 Q_SLOTS/Q_SIGNALS 被预处理后变成访问修饰符, libclang 看到的
    只是 public/private/protected。不要用 `cursor.is_definition()` 判断
    is_slot — 这会将所有有函数体的方法误标记为 slot。
    正确做法: is_slot 默认 False, is_signal 用启发式 (无定义体 + public +
    返回 void)。需要精确判断时必须解析 moc 生成的文件。
18. 调用图谱中 callee ID 必须用 `cursor.referenced.definition` 获取定义行号,
    而非 `cursor.referenced.location.line` (声明位置)。否则同名函数的声明
    和定义位置不匹配, 导致调用边连接到错误节点。

### 风险排序 (Stage 2) 的 Gotchas

19. `nx.all_simple_paths` 在大型调用图谱上会指数爆炸。必须添加 `cutoff=20`
    限制搜索深度, 否则几百个节点的图就会让进程挂起数小时。

### 变异测试 (Stage 6) 的 Gotchas

20. AOR 变异算子必须检测一元运算符: `-1` 中的 `-` 是符号而非减法,
    `+1` 中的 `+` 是正号而非加法。用 `_is_unary_op()` 检查前一个非空白
    字符: 如果是运算符/括号/逗号/等号等则为一元, 应跳过。
    还需跳过复合赋值 (`+=`, `-=`) 和自增自减 (`++`, `--`)。
21. `in_string()` 必须是完整的逐字符状态机, 覆盖: 双引号字符串、单引号
    字符字面量、`//` 和 `/* */` 注释、`\\` 转义序列。只检查双引号计数
    (偶/奇) 会遗漏字符字面量和注释中的运算符, 导致误变异。
22. 变异测试必须有源码安全恢复机制: atexit + SIGTERM/SIGINT 信号处理 +
    `_PENDING_RESTORES` 全局列表。如果进程被 kill, 源码永久变异。
    每个变异-恢复周期在 finally 块中移除对应的 pending 条目。

## 适配模式

已有项目 (mode=existing):
- 不修改源码，只新增测试文件
- 读取 compile_commands.json 获取精确编译参数
- git log 分析变更频率 (Stage 2 权重启用)
- 测试文件放已有 tests/ 目录

新项目 (mode=new):
- Stage 0 创建 src/ tests/ CMakeLists.txt 脚手架
- 从零构建图谱
- 创建独立 tests/ 目录
- 变更频率权重禁用 (无 git 历史)
