# 变异测试方法与算子定义

## 概述

本文件定义 Stage 5 的变异测试方法和 Stage 4 的 Level 4 故障注入测试设计。

## 变异测试原理

变异测试 (Mutation Testing) 由 Richard Lipton 提出 (1978)。
核心思想: 对源码做小修改 (变异)，运行测试集，看测试能否发现变异。

- 变异体 (Mutant): 修改后的代码副本
- 杀死 (Killed): 测试集在变异体上失败 → 测试有效
- 存活 (Survived): 测试集在变异体上通过 → 测试有缺口
- 等价变异体 (Equivalent): 变异不改变行为 → 无法杀死，需人工识别

变异得分 (Mutation Score) = 杀死变异体数 / (总变异体数 - 等价变异体数)

目标: >= 80%

## 变异算子 (Mutation Operators)

### 算术运算符替换 (AOR)

| 原始 | 变异 |
|------|------|
| + | -, * |
| - | +, / |
| * | /, + |
| / | *, - |
| % | *, / |

### 逻辑运算符替换 (LOR)

| 原始 | 变异 |
|------|------|
| && | \|\| |
| \|\| | && |
| ! | (去掉) |

### 关系运算符替换 (ROR)

| 原始 | 变异 |
|------|------|
| < | <=, >, >= |
| > | >=, <, <= |
| <= | <, >, >= |
| >= | >, <, <= |
| == | != |
| != | == |

### 常量替换 (CRC)

| 原始 | 变异 |
|------|------|
| 0 | 1, -1 |
| 1 | 0, 2 |
| -1 | 0, 1 |
| n (任意) | n+1, n-1 |

### 语句删除 (SDL)

删除一行赋值语句或函数调用语句。
适用: 无返回值的语句 (void 函数调用, 变量赋值)。

### 返回值修改 (RVF)

| 原始 | 变异 |
|------|------|
| return x | return x + 1 |
| return x | return x - 1 |
| return true | return false |
| return false | return true |
| return null | return new Object() (类型允许时) |

## 变异测试执行流程

```
1. 选择目标函数 (P0 级别)
2. 生成变异体 (对每个算子应用所有可能变异)
3. 编译每个变异体
4. 运行测试集 (对每个编译成功的变异体)
5. 记录杀死/存活
6. 计算变异得分
7. 对存活变异体分析: 等价变异体 or 测试缺口
8. 如果是测试缺口 → 补充测试用例
```

## 自动化脚本流程 (mutation_score.py)

```python
def run_mutation_testing(target_file, test_executable, function_name):
    # 1. 提取目标函数源码
    original_code = extract_function(target_file, function_name)

    # 2. 生成变异体
    mutants = generate_mutants(original_code)

    # 3. 对每个变异体
    results = []
    for mutant in mutants:
        # 替换源码中的函数
        patched = patch_function(target_file, function_name, mutant.code)

        # 编译变异体 (独立 build 目录)
        build_dir = f"build_mutant_{mutant.id}"
        compile_result = compile_project(patched, build_dir)

        if not compile_result.success:
            results.append({'mutant': mutant, 'status': 'compile_failed'})
            continue

        # 运行测试
        test_result = run_tests(build_dir, test_executable)

        if test_result.failed:
            results.append({'mutant': mutant, 'status': 'killed'})
        else:
            results.append({'mutant': mutant, 'status': 'survived'})

    # 4. 计算得分
    killed = sum(1 for r in results if r['status'] == 'killed')
    survived = sum(1 for r in results if r['status'] == 'survived')
    total = killed + survived

    score = (killed / total * 100) if total > 0 else 0

    return {'score': score, 'killed': killed, 'survived': survived,
            'details': results}
```

## 实用限制

1. 变异体爆炸: 一个函数可能产生几十到上百个变异体。
   限制: 只对 P0 函数做变异测试，且限制变异体数量 <= 50 个/函数。
2. 编译开销: 每个变异体需重新编译。使用独立 build 目录并行编译。
3. 等价变异体: 需要人工或启发式识别。当前实现标记为 survived，
   不自动识别等价变异体。
4. libclang AST 修改: 变异操作在源码文本级别进行，不修改 AST。
   用正则匹配或行级替换，保证修改精确。

## Level 4 测试设计 (错误猜测)

变异测试验证已有测试集的有效性。Level 4 的测试设计还包含错误猜测:

### 空值/无效输入
- 空字符串: ""
- 空容器: QList<int>(), QHash()
- null 指针: nullptr (对裸指针参数)
- 空对象: QObject() (对 QObject* 参数)

### 数值边界
- 整数: INT_MAX, INT_MIN, 0, -1
- 浮点: NaN, Infinity, -Infinity, 0.0, -0.0, DBL_MIN, DBL_MAX
- 枚举: 枚举值边界 + 无效枚举值

### 字符串边界
- 超长字符串: QString("a").repeated(10000)
- 特殊字符: \0, \n, \r, \t, Unicode, emoji
- 编码: UTF-8, Latin1, 混合编码

### 资源泄漏
- 重复调用: 连续两次调用同一函数，检查资源是否泄漏
- 异常路径: 函数在中途抛异常时是否正确释放资源
- 信号断开: 信号槽连接断开后调用是否安全

### 并发安全 (对非线程安全函数)
- 重复调用同一对象的方法 (非重入函数)
- 从不同线程调用 (对非线程安全类)
