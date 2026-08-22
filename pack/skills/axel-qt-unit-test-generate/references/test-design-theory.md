# 测试设计理论与分级详解

## 概述

本文件定义 Skill 的核心测试设计理论。所有测试用例的生成必须遵循此分级体系。

## 理论来源

分级体系综合以下经典测试理论:

- 等价类划分 (Equivalence Partitioning): Glenford Myers, "The Art of Software
  Testing", 1979
- 边界值分析 (Boundary Value Analysis): Myers, 1979
- 基路径测试 (Basis Path Testing): Thomas McCabe, "A Complexity Measure",
  IEEE TSE, 1976
- 判定表测试 (Decision Table Testing): Boris Beizer, "Software Testing
  Techniques", 1982
- 变异测试 (Mutation Testing): Richard Lipton, "Mutation Analysis: A New
  Approach to Program Testing", 1978
- 状态转换测试 (State Transition Testing): Robert Binder, "Testing
  Object-Oriented Systems", 2000

## 5 级测试设计体系

### Level 0 — 基础验证 (Smoke Test)

定义: 验证函数可以被调用并返回，不崩溃。

适用对象:
  - P3 级别的简单函数 (Risk Score < 20)
  - trivial getter/setter
  - 模块初始化/清理函数

设计技术: 无特殊技术，只需一次正常调用。

Qt Test 实现:
  ```cpp
  void testAdd_basic() {
      Calculator calc;
      QVERIFY(calc.add(1, 2) == 3);
  }
  ```

覆盖目标: 语句覆盖 (Statement Coverage)

### Level 1 — 规范测试 (Specification-Based)

定义: 按函数接口规范验证输入输出关系，使用黑盒技术。

适用对象:
  - P2 级别 (Risk Score >= 20)
  - P1 级别 (Risk Score >= 40) 的辅助函数

设计技术:

1. 等价类划分 (Equivalence Partitioning):
   将输入域划分为有效等价类和无效等价类，每类至少一个测试用例。
   - 有效等价类: 符合规范的输入
   - 无效等价类: 不符合规范的输入 (应被拒绝或抛异常)
   示例: int divide(int a, int b)
   - 有效: (10, 2) → 5
   - 无效: (10, 0) → 异常/错误

2. 边界值分析 (Boundary Value Analysis):
   在等价类边界处取值，错误常发生在边界。
   对于范围 [min, max]:
   - min-1, min, min+1 (下边界)
   - max-1, max, max+1 (上边界)
   对于 n 元素集合:
   - 0, 1, n-1, n, n+1
   示例: int getElement(int index) 容器大小为 n
   - 边界值: index = -1, 0, 1, n-2, n-1, n

3. 判定表测试 (Decision Table Testing):
   当函数有多个条件输入且不同组合产生不同行为时使用。
   构造判定表:
   - 条件: 列出所有输入条件
   - 动作: 列出所有可能输出/行为
   - 规则: 每个条件组合对应的动作
   示例: 电商折扣函数 calculateDiscount(isMember, amount > 100, hasCoupon)
   - 8 种条件组合 (2^3)，每种一个测试行

Qt Test 实现 (数据驱动):
  ```cpp
  void testDivide_data() {
      QTest::addColumn<int>("a");
      QTest::addColumn<int>("b");
      QTest::addColumn<int>("expected");
      QTest::newRow("normal") << 10 << 2 << 5;
      QTest::newRow("zero_divisor") << 10 << 0 << -1;
      QTest::newRow("negative") << -10 << 2 << -5;
  }
  void testDivide() {
      QFETCH(int, a); QFETCH(int, b); QFETCH(int, expected);
      QCOMPARE(calc.divide(a, b), expected);
  }
  ```

覆盖目标: 分支覆盖 (Branch Coverage) + 边界覆盖

### Level 2 — 结构测试 (Structure-Based)

定义: 基于函数内部控制流结构设计测试，覆盖所有执行路径。

适用对象:
  - P1 级别 (Risk Score >= 40)
  - P0 级别 (Risk Score >= 70) 的非交互函数

设计技术:

1. 分支覆盖 (Branch Coverage):
   每个条件分支的 True 和 False 路径各至少一次。
   ```cpp
   if (x > 0) { ... }  // 需要 x>0 和 x<=0 两个用例
   ```

2. 条件覆盖 (Condition Coverage):
   每个布尔子条件的 True 和 False 各至少一次。
   ```cpp
   if (a && b) { ... }  // 需要 (T,T)(F,*)(*,F) 至少覆盖 a=T,a=F,b=T,b=F
   ```

3. 基路径测试 (Basis Path Testing) — McCabe 1976:
   基于 McCabe 圈复杂度 V(G) 确定独立路径数量:
   V(G) = E - N + 2  (E=边数, N=节点数)
   或: V(G) = 判定节点数 + 1

   判定节点: if, for, while, do-while, switch-case, catch, &&, ||, ?:
   每个判定节点产生 2 条边 (True/False)。

   独立路径: 至少包含一条未被其他路径覆盖的新边。

   算法:
   a. 计算圈复杂度 V(G)
   b. 选择基路径集合 (数量 = V(G))
   c. 每条基路径一个测试用例

4. 路径覆盖 (Path Coverage, 限于可行路径):
   覆盖所有可行的执行路径。对于高复杂度函数，路径数可能爆炸，
   仅对低复杂度 (V(G) <= 5) 的函数使用。

Qt Test 实现:
  ```cpp
  // 基路径测试: V(G)=3, 需要 3 个测试用例
  void testClassify_branch1() {
      // 路径: x > 0 → return "positive"
      QCOMPARE(calc.classify(10), QString("positive"));
  }
  void testClassify_branch2() {
      // 路径: x < 0 → return "negative"
      QCOMPARE(calc.classify(-10), QString("negative"));
  }
  void testClassify_branch3() {
      // 路径: x == 0 → return "zero"
      QCOMPARE(calc.classify(0), QString("zero"));
  }
  ```

覆盖目标: 分支覆盖 >= 90%, 条件覆盖 >= 80%

### Level 3 — 交互测试 (Interaction Test)

定义: 验证函数与其调用链中其他函数的交互正确性。

适用对象:
  - P0 级别 (Risk Score >= 70)
  - 高入度函数 (被多个函数调用)
  - 信号槽连接点

设计技术:

1. 调用链路径测试:
   从调用图谱提取关键调用链 (入口 → ... → 目标函数)，
   对整条链设计测试，验证中间参数传递和返回值传播。

2. 信号验证 (QSignalSpy):
   对 Qt 信号槽机制，用 QSignalSpy 监听信号发射，验证:
   - 信号是否发射 (count)
   - 信号参数是否正确 (takeFirst)
   - 信号发射时机 (order)

3. Mock/Stub 下游依赖:
   对调用链中的下游依赖做 Mock，隔离测试目标:
   - 如果依赖是虚函数，创建子类覆盖
   - 如果依赖是函数指针/std::function，替换实现
   - 如果依赖通过 Q_INVOKABLE 调用，用 QSignalSpy 替代

Qt Test 实现:
  ```cpp
  // 信号验证
  void testValueChanged_signal() {
      QSignalSpy spy(&model, &Model::valueChanged);
      model.setValue(42);
      QCOMPARE(spy.count(), 1);
      QList<QVariant> args = spy.takeFirst();
      QCOMPARE(args.at(0).toInt(), 42);
  }

  // Mock 下游
  class MockStorage : public IStorage {
  public:
      bool save_called = false;
      bool save(const QString&) override { save_called = true; return true; }
  };
  void testSaveFlow_interaction() {
      MockStorage storage;
      Manager mgr(&storage);
      mgr.process("data");
      QVERIFY(storage.save_called);
  }
  ```

覆盖目标: 关键调用链路径覆盖

### Level 4 — 故障注入测试 (Fault Injection / Mutation-Guided)

定义: 通过注入故障验证测试集能否发现真实缺陷。

适用对象:
  - P0 级别的核心函数
  - 安全敏感函数 (认证、权限、数据处理)

设计技术:

1. 变异测试 (Mutation Testing):
   对源码做小修改 (变异)，运行测试集:
   - 如果测试集能发现变异 (杀死变异体) → 测试有效
   - 如果测试集不能发现变异 (变异体存活) → 测试有缺口

   变异算子 (Mutation Operators):
   - 算术替换: + → -, * → /, - → +
   - 逻辑替换: && → ||, || → &&, ! → (去掉)
   - 关系替换: < → <=, > → >=, == → !=
   - 常量替换: 0 → 1, 1 → 0
   - 语句删除: 删除一行赋值/调用语句
   - 返回值修改: return x → return x+1

   变异得分 (Mutation Score) = 杀死变异体数 / 总变异体数
   目标: >= 80%

2. 错误猜测 (Error Guessing):
   基于经验猜测可能的错误场景:
   - 空指针/空对象
   - 整数溢出
   - 字符串编码问题
   - 资源泄漏 (内存、文件句柄)
   - 并发竞争 (对非线程安全函数)

3. 边界故障注入:
   - 数组越界: index = -1, size, size+1
   - 缓冲区溢出: 超长字符串
   - 数值边界: INT_MAX, INT_MIN, NaN, Infinity

Qt Test 实现:
  变异测试由脚本 (mutation_score.py) 自动化执行，不直接写在测试代码中。
  测试代码中体现的是基于错误猜测的用例:
  ```cpp
  void testParse_nullInput() {
      QCOMPARE(parser.parse(QString()), -1);  // 空输入
  }
  void testParse_overflowInput() {
      QCOMPARE(parser.parse(QString("99999999999999999999")), -2);  // 溢出
  }
  ```

覆盖目标: 变异得分 >= 80%

## 优先级与级别映射

| 优先级 | Risk Score | 最低测试级别 | 覆盖目标 |
|--------|-----------|-------------|---------|
| P0 | >= 70 | Level 4 | 分支>=90%, 变异>=80% |
| P1 | >= 40 | Level 2 | 分支>=90%, 条件>=80% |
| P2 | >= 20 | Level 1 | 分支覆盖+边界 |
| P3 | < 20 | Level 0 | 语句覆盖 |

## 级别选择决策树

```
函数是否有分支/条件?
├─ 否 → Level 0 (Smoke)
└─ 是 → 函数是否有多个输入域?
        ├─ 是 → 函数是否在关键调用链上?
        │       ├─ 是 → Level 3 (Interaction)
        │       └─ 否 → Level 1 (Specification)
        └─ 否 → Level 2 (Structure)
                (按基路径覆盖所有分支)

对所有 P0 函数，追加 Level 4 (Fault Injection)
```
