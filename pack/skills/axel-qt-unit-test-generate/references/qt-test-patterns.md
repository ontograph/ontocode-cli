# Qt Test 框架模式与最佳实践

## 概述

本文件定义 Stage 4 测试代码生成时遵循的 Qt Test 规范。

## 测试类结构

每个被测类生成一个测试类:

```cpp
#include <QtTest>
#include "<被测类头文件>"

class Test<ClassName> : public QObject
{
    Q_OBJECT

private slots:
    // 整体夹具
    void initTestCase();      // 整个测试开始前调用一次
    void cleanupTestCase();   // 整个测试结束后调用一次

    // 单次夹具
    void init();              // 每个测试函数前调用
    void cleanup();           // 每个测试函数后调用

    // Level 0: Smoke
    void test<Method>_smoke();

    // Level 1: Specification (数据驱动)
    void test<Method>_data();
    void test<Method>();

    // Level 2: Structure (基路径)
    void test<Method>_path1();
    void test<Method>_path2();

    // Level 3: Interaction
    void test<Method>_signal();
    void test<Method>_interaction();

    // Level 4: Fault Injection
    void test<Method>_nullInput();
    void test<Method>_overflow();
};
```

## 断言宏使用规范

| 宏 | 用途 | 使用场景 |
|----|------|---------|
| QVERIFY(cond) | 布尔条件 | 验证状态/标志 |
| QVERIFY2(cond, msg) | 带消息的布尔条件 | 失败时提供诊断信息 |
| QCOMPARE(actual, expected) | 值比较 | 验证返回值 (必须是最精确比较) |
| QCOMPARE_EQ(actual, expected) | 纯值比较 | Qt 6.4+, 不走 qCompare |
| QVERIFY_EXCEPTION_THROWN(expr, type) | 异常验证 | 验证抛出指定异常 |

规则:
- 优先用 QCOMPARE 而非 QVERIFY(x == y)，因为 QCOMPARE 在失败时
  输出实际值和期望值，诊断信息更充分
- QCOMPARE 的两个参数类型必须一致，否则模板推导失败
- 对浮点数: QCOMPARE(actual, expected) 内部用 qFuzzyCompare，
  但对 0 值不适用，需用 QVERIFY(qAbs(actual - expected) < epsilon)
- 自定义类型需注册 Q_DECLARE_METATYPE 才能在数据驱动测试中使用

## 数据驱动测试模式

适用于 Level 1 (规范测试):

```cpp
void testDivide_data()
{
    QTest::addColumn<int>("a");
    QTest::addColumn<int>("b");
    QTest::addColumn<int>("expected");

    // 等价类划分
    QTest::newRow("positive_normal") << 10 << 2 << 5;
    QTest::newRow("negative_normal") << -10 << 2 << -5;
    QTest::newRow("both_negative") << -10 << -2 << 5;

    // 边界值
    QTest::newRow("divisor_one") << 10 << 1 << 10;
    QTest::newRow("dividend_zero") << 0 << 5 << 0;

    // 异常等价类
    QTest::newRow("divisor_zero") << 10 << 0 << -1;
}

void testDivide()
{
    QFETCH(int, a);
    QFETCH(int, b);
    QFETCH(int, expected);
    QCOMPARE(m_calc->divide(a, b), expected);
}
```

## 信号测试模式

适用于 Level 3 (交互测试):

```cpp
void testModel_valueChanged()
{
    Model model;
    QSignalSpy spy(&model, &Model::valueChanged);

    model.setValue(42);
    QVERIFY(spy.count() == 1);
    QList<QVariant> args = spy.takeFirst();
    QCOMPARE(args.at(0).toInt(), 42);
}
```

多信号验证:
```cpp
void testStateMachine_transitions()
{
    StateMachine sm;
    QSignalSpy enterSpy(&sm, &StateMachine::stateEntered);
    QSignalSpy exitSpy(&sm, &StateMachine::stateExited);

    sm.transitionTo("RUNNING");

    QCOMPARE(enterSpy.count(), 1);
    QCOMPARE(exitSpy.count(), 1);
    QCOMPARE(enterSpy.takeFirst().at(0).toString(), QString("RUNNING"));
}
```

## Mock 模式

### 虚函数 Mock

```cpp
class MockStorage : public IStorage {
public:
    bool m_saveCalled = false;
    QString m_lastData;

    bool save(const QString& data) override {
        m_saveCalled = true;
        m_lastData = data;
        return true;
    }
};

void testManager_savesData()
{
    MockStorage storage;
    Manager manager(&storage);
    manager.process("test_data");
    QVERIFY(storage.m_saveCalled);
    QCOMPARE(storage.m_lastData, QString("test_data"));
}
```

### Qt 信号槽 Mock (无虚函数接口时)

如果下游依赖通过信号槽通信，用 QSignalSpy 替代 Mock 对象:
```cpp
void testController_emitsFinished()
{
    Controller controller;
    QSignalSpy spy(&controller, &Controller::finished);
    controller.execute();
    QVERIFY(spy.wait(5000));  // 等待信号，最多 5 秒
}
```

## GUI 测试模式

对 QWidget 子类:

```cpp
void testLineEdit_maxLength()
{
    QLineEdit edit;
    edit.setMaxLength(5);

    // 模拟键盘输入
    QTest::keyClicks(&edit, "12345678");
    QCOMPARE(edit.text(), QString("12345"));  // 被截断为 5

    // 模拟鼠标点击
    QTest::mouseClick(&edit, Qt::LeftButton);
    QVERIFY(edit.hasFocus());
}
```

对异步/事件循环:
```cpp
void testLoader_asyncLoad()
{
    DataLoader loader;
    QSignalSpy spy(&loader, &DataLoader::loaded);
    loader.loadAsync("file.dat");

    // 等待信号，超时 5 秒
    QVERIFY(spy.wait(5000));
}
```

## CMake 集成

```cmake
# tests/CMakeLists.txt

enable_testing()

# 自动处理 Q_OBJECT (moc)
set_target_properties(test_calculator PROPERTIES
    AUTOMOC ON
)

# 链接 Qt Test + 被测库
target_link_libraries(test_calculator
    Qt5::Test
    calculator_lib     # 被测目标
)

# 注册 CTest
add_test(NAME test_calculator
    COMMAND test_calculator
)

# 覆盖率编译参数 (可选)
if(ENABLE_COVERAGE)
    target_compile_options(test_calculator PRIVATE
        -fprofile-arcs -ftest-coverage
    )
    target_link_libraries(test_calculator
        -fprofile-arcs -ftest-coverage
    )
endif()
```

## 运行测试

```bash
# 无头环境
QT_QPA_PLATFORM=offscreen ctest --output-on-failure

# 带详细输出
QT_QPA_PLATFORM=offscreen ctest -V

# 运行单个测试
QT_QPA_PLATFORM=offscreen ./test_calculator

# 运行特定测试函数
QT_QPA_PLATFORM=offscreen ./test_calculator testDivide

# 输出 JSON 格式结果
QT_QPA_PLATFORM=offscreen ./test_calculator -o results.json,json
```

## 命名规范

测试类: Test<被测类名>
测试函数: test<被测方法名>_<场景/级别>
数据函数: test<被测方法名>_data()
测试文件: test_<小写类名>.h + test_<小写类名>.cpp
测试目标: test_<小写类名> (CMake target)

示例:
- 被测类: Calculator
- 测试类: TestCalculator
- 测试文件: test_calculator.h, test_calculator.cpp
- 测试目标: test_calculator
- 测试函数: testAdd_smoke, testDivide_data, testDivide, testCompute_path1
