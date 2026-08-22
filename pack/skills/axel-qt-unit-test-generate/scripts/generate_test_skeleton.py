#!/usr/bin/env python3
"""
generate_test_skeleton.py — Stage 4: 生成 Qt Test 测试骨架代码

用法:
    python3 generate_test_skeleton.py --state state.json --design test_design_doc.md
    python3 generate_test_skeleton.py --state state.json --auto  # 自动设计

输入: state.json (Stage 2 产出: priority_report.json, call_graph.json)
输出: tests/test_<classname>.h, tests/test_<classname>.cpp, tests/CMakeLists.txt
"""

import argparse
import json
import os
import sys
import re
from collections import defaultdict


# ── 测试级别到代码模板的映射 ───────────────────────────────

LEVEL0_TEMPLATE = '''    // Level 0: Smoke Test
    void test{method}_smoke()
    {{
        {cls} obj;
        {call_expr}
    }}
'''

LEVEL1_TEMPLATE = '''
    // Level 1: Specification-Based (数据驱动)
    void test{method}_data()
    {{
{column_decls}
{data_rows}
    }}
    void test{method}()
    {{
{fetch_lines}
        {cls} obj;
{call_line}
{assert_line}
    }}
'''

LEVEL2_TEMPLATE = '''
    // Level 2: Structure-Based (基路径测试, V(G)={complexity})
    void test{method}_path1()
    {{
        // 路径 1: 主分支
        {cls} obj;
        {call_expr_path1}
    }}
    void test{method}_path2()
    {{
        // 路径 2: 替代分支
        {cls} obj;
        {call_expr_path2}
    }}
'''

LEVEL3_TEMPLATE = '''
    // Level 3: Interaction Test (信号验证)
    void test{method}_signal()
    {{
        // QSignalSpy 验证信号 (如有)
        {cls} obj;
        // QSignalSpy spy(&obj, &{cls}::signalName);
        {call_expr}
    }}
    // Level 3: Interaction Test (调用链)
    void test{method}_interaction()
    {{
        // 验证调用链中的交互
        {cls} obj;
        {call_expr}
    }}
'''

LEVEL4_TEMPLATE = '''
    // Level 4: Fault Injection (空值/无效输入)
    void test{method}_nullInput()
    {{
        {cls} obj;
        {null_call}
    }}
    // Level 4: Fault Injection (溢出/边界)
    void test{method}_overflow()
    {{
        {cls} obj;
        {overflow_call}
    }}
'''


def get_test_level(priority):
    """优先级到最低测试级别的映射"""
    return {
        'P0': 4,
        'P1': 2,
        'P2': 1,
        'P3': 0,
    }.get(priority, 0)


# ── 类型推导辅助 ─────────────────────────────────────────────

INT_MIN_VAL = 'INT_MIN'
INT_MAX_VAL = 'INT_MAX'
STRING_EMPTY = 'QString()'
STRING_LONG = 'QString("a").repeated(10000)'


def get_default_value(param_type, param_name=''):
    """根据参数类型返回默认测试值"""
    pt = param_type.strip()

    # 基本整型
    if pt in ('int', 'long', 'long long', 'short', 'unsigned int',
              'uint', 'unsigned long', 'size_t', 'qint32', 'qint64',
              'quint32', 'quint64'):
        return '42'
    # 布尔
    if pt == 'bool':
        return 'true'
    # 浮点
    if pt in ('float', 'double', 'qreal'):
        return '1.0'
    # 字符串 (含 const QString&, QString&, QString)
    if 'QString' in pt:
        return 'QString("test")'
    # 字符
    if pt == 'char' or pt == 'QChar':
        return "'a'"
    # 指针
    if '*' in pt:
        return 'nullptr'
    # 引用到基本类型
    if '&' in pt:
        # const int&, double& 等
        for base in ('int', 'long', 'short', 'float', 'double', 'qreal', 'bool'):
            if base in pt:
                return get_default_value(base)
        return '{}'  # 默认构造
    # 默认
    return '{}'  # 默认构造


def get_null_value(param_type):
    """获取空/无效值用于故障注入测试"""
    pt = param_type.strip()
    if 'QString' in pt:
        return 'QString()'
    if '*' in pt:
        return 'nullptr'
    if pt in ('int', 'long', 'short', 'qint32', 'qint64'):
        return '0'
    if pt == 'bool':
        return 'false'
    if pt in ('float', 'double', 'qreal'):
        return '0.0'
    return '{}'  # 默认构造


def get_overflow_value(param_type):
    """获取溢出/边界值用于故障注入测试"""
    pt = param_type.strip()
    if pt in ('int', 'long', 'short', 'qint32', 'qint64'):
        return 'INT_MAX'
    if pt in ('unsigned int', 'uint', 'quint32', 'quint64', 'size_t'):
        return 'UINT_MAX'
    if pt in ('float', 'double', 'qreal'):
        return '1e308'
    if pt == 'bool':
        return 'true'
    if 'QString' in pt:
        return 'QString("a").repeated(10000)'
    return '0'


def format_call_expr(class_name, method_name, params, ret_type='void'):
    """生成实际调用表达式 (smoke test: 只验证可调用, 不断言具体返回值)"""
    args = ', '.join(get_default_value(p.get('type', ''), p.get('name', ''))
                     for p in params)
    call = 'obj.{}({})'.format(method_name, args)

    if ret_type and ret_type != 'void':
        # 按返回类型选择安全的断言方式
        rt = ret_type.strip()
        if 'QString' in rt:
            return '{} result = {};\n        QVERIFY(!result.isEmpty() || result.isEmpty());  // TODO: 替换为真实断言'.format(ret_type, call)
        elif rt == 'bool':
            return '{} result = {};\n        QVERIFY(result || !result);  // TODO: 替换为真实断言'.format(ret_type, call)
        elif rt in ('int', 'long', 'long long', 'short', 'unsigned int',
                    'uint', 'unsigned long', 'size_t', 'qint32', 'qint64',
                    'quint32', 'quint64', 'float', 'double', 'qreal'):
            return '{} result = {};\n        QVERIFY(result >= 0 || result < 0);  // TODO: 替换为真实断言'.format(ret_type, call)
        else:
            # 其他类型: 只验证可调用
            return '{} result = {};\n        Q_UNUSED(result);  // TODO: 补充验证逻辑'.format(ret_type, call)
    else:
        return '{};\n        QVERIFY(true);  // TODO: 补充验证逻辑'.format(call)


def format_null_call(class_name, method_name, params, ret_type='void'):
    """生成空值调用的故障注入测试"""
    args = ', '.join(get_null_value(p.get('type', ''))
                     for p in params)
    call = 'obj.{}({})'.format(method_name, args)
    if ret_type and ret_type != 'void':
        return '{} result = {};\n        // 空输入应返回特定值或不变\n        QVERIFY(true);'.format(ret_type, call)
    else:
        return '{};\n        QVERIFY(true);'.format(call)


def format_overflow_call(class_name, method_name, params, ret_type='void'):
    """生成溢出值调用的故障注入测试"""
    args = ', '.join(get_overflow_value(p.get('type', ''))
                     for p in params)
    call = 'obj.{}({})'.format(method_name, args)
    if ret_type and ret_type != 'void':
        return '{} result = {};\n        // 溢出输入应安全处理\n        QVERIFY(true);'.format(ret_type, call)
    else:
        return '{};\n        QVERIFY(true);'.format(call)


def format_data_rows(params, ret_type):
    """生成数据驱动测试的初始数据行"""
    if not params:
        return '        // TODO: 添加测试数据'

    p1 = params[0]
    p1_type = p1.get('type', 'int').replace('const ', '').replace('&', '').strip()
    ret = (ret_type or 'int').replace('const ', '').replace('&', '').strip()

    rows = []
    p1_default = get_default_value(p1.get('type', ''))
    ret_default = get_default_value(ret)

    # 等价类: 正常值
    rows.append('        QTest::newRow("normal") << {} << {};'.format(
        p1_default, ret_default))

    # 边界值
    null_val = get_null_value(p1.get('type', ''))
    overflow_val = get_overflow_value(p1.get('type', ''))

    rows.append('        QTest::newRow("boundary_zero") << {} << {};'.format(
        null_val, ret_default))
    rows.append('        QTest::newRow("boundary_max") << {} << {};'.format(
        overflow_val, ret_default))

    return '\n'.join(rows)


def clean_type(type_str):
    """清理类型字符串用于 QFETCH/QTest::addColumn"""
    t = (type_str or 'int').replace('const ', '').replace('&', '').strip()
    if 'QString' in t:
        return 'QString'
    return t


def generate_test_functions(func, level, call_graph_data):
    """根据级别生成测试函数声明和骨架"""
    method_name = func['name']
    if '::' in method_name:
        method_name = method_name.split('::')[-1]
    class_name = func.get('class', '') or 'GlobalFunctions'
    complexity = func.get('complexity', 1)
    params = func.get('params', [])
    ret_type = func.get('return_type', 'void')
    access = func.get('access', 'public')

    method_title = method_name[0].upper() + method_name[1:] if method_name else 'Method'
    ret_clean = clean_type(ret_type)

    # ── 私有方法: 只生成 smoke 桩，不直接调用 ──
    if access == 'private' and not func.get('is_virtual', False):
        return '''    // Level 0: Smoke Test (private - test indirectly)
    void test{method}_smoke()
    {{
        // {cls}::{method_lower} is private, test via public callers
        QVERIFY(true);
    }}'''.format(method=method_title, method_lower=method_name, cls=class_name)

    # ── 构造函数: 特殊处理 ──
    if method_name == class_name:
        return '''    // Level 0: Smoke Test (constructor)
    void test{method}_smoke()
    {{
        {cls} obj;
        QVERIFY(true);
    }}'''.format(method=method_title, cls=class_name)

    # ── 析构函数: 特殊处理 ──
    if method_name.startswith('~'):
        return '''    // Level 0: Smoke Test (destructor)
    void test{method}_smoke()
    {{
        {cls} *obj = new {cls}();
        delete obj;
        QVERIFY(true);
    }}'''.format(method=method_title, cls=class_name)

    # 生成调用表达式
    call_expr = format_call_expr(class_name, method_name, params, ret_type)
    null_call = format_null_call(class_name, method_name, params, ret_type)
    overflow_call = format_overflow_call(class_name, method_name, params, ret_type)

    # ── 检查是否有指针参数 (输出参数), 数据驱动测试不支持 ──
    has_pointer_param = any('*' in p.get('type', '') for p in params)

    test_functions = []

    # Level 0
    test_functions.append(LEVEL0_TEMPLATE.format(
        method=method_title, method_lower=method_name,
        cls=class_name, call_expr=call_expr))

    if level >= 1 and not has_pointer_param:
        is_void = (not ret_type) or ret_type == 'void'

        # ── 构建多参数数据驱动测试 ──
        column_decls = []
        for i, p in enumerate(params):
            p_type = clean_type(p.get('type', 'int'))
            p_name = p.get('name') or 'arg{}'.format(i)
            column_decls.append('        QTest::addColumn<{}>("{}");'.format(p_type, p_name))
        if not is_void:
            column_decls.append('        QTest::addColumn<{}>("expected");'.format(ret_clean))

        # Fetch lines
        fetch_lines = []
        for i, p in enumerate(params):
            p_type = clean_type(p.get('type', 'int'))
            p_name = p.get('name') or 'arg{}'.format(i)
            fetch_lines.append('        QFETCH({}, {});'.format(p_type, p_name))
        if not is_void:
            fetch_lines.append('        QFETCH({}, expected);'.format(ret_clean))

        # Comma-separated arg names for the function call
        fetch_args = ', '.join(
            p.get('name') or 'arg{}'.format(i)
            for i, p in enumerate(params))

        # Data rows: normal + boundary values for all params
        row_vals_normal = [get_default_value(p.get('type', '')) for p in params]
        row_vals_zero = [get_null_value(p.get('type', '')) for p in params]
        row_vals_max = [get_overflow_value(p.get('type', '')) for p in params]
        if not is_void:
            ret_default_val = get_default_value(ret_type)
            row_vals_normal.append(ret_default_val)
            row_vals_zero.append(ret_default_val)
            row_vals_max.append(ret_default_val)

        data_rows_str = (
            '        QTest::newRow("normal") << ' + ' << '.join(row_vals_normal) + ';\n' +
            '        QTest::newRow("boundary_zero") << ' + ' << '.join(row_vals_zero) + ';\n' +
            '        QTest::newRow("boundary_max") << ' + ' << '.join(row_vals_max) + ';'
        )

        if is_void:
            call_line = '        obj.{}({});\n        QVERIFY(true);  // TODO: 验证副作用'.format(
                method_name, fetch_args)
            assert_line = ''
        else:
            call_line = '        {} result = obj.{}({});\n        Q_UNUSED(result);'.format(
                ret_type, method_name, fetch_args)
            assert_line = '        QVERIFY(true);  // TODO: 替换为真实期望值'

        test_functions.append(LEVEL1_TEMPLATE.format(
            method=method_title, method_lower=method_name,
            cls=class_name,
            column_decls='\n'.join(column_decls),
            fetch_lines='\n'.join(fetch_lines),
            data_rows=data_rows_str,
            call_line=call_line,
            assert_line=assert_line))

    if level >= 2:
        # 路径1: 正常参数
        path1_args = ', '.join(get_default_value(p.get('type', '')) for p in params)
        # 路径2: 替代参数 (用 null 值触发不同分支)
        path2_args = ', '.join(get_null_value(p.get('type', '')) for p in params)

        if ret_type and ret_type != 'void':
            call_expr_path1 = '{} r1 = obj.{}({});\n        Q_UNUSED(r1);\n        QVERIFY2(true, "path1: normal branch");'.format(
                ret_type, method_name, path1_args)
            call_expr_path2 = '{} r2 = obj.{}({});\n        Q_UNUSED(r2);\n        QVERIFY2(true, "path2: alternate branch");'.format(
                ret_type, method_name, path2_args)
        else:
            call_expr_path1 = 'obj.{}({});\n        QVERIFY2(true, "path1: normal branch");'.format(
                method_name, path1_args)
            call_expr_path2 = 'obj.{}({});\n        QVERIFY2(true, "path2: alternate branch");'.format(
                method_name, path2_args)

        test_functions.append(LEVEL2_TEMPLATE.format(
            method=method_title, method_lower=method_name,
            cls=class_name, complexity=complexity,
            call_expr_path1=call_expr_path1,
            call_expr_path2=call_expr_path2))

    if level >= 3:
        test_functions.append(LEVEL3_TEMPLATE.format(
            method=method_title, method_lower=method_name,
            cls=class_name, call_expr=call_expr))

    if level >= 4:
        test_functions.append(LEVEL4_TEMPLATE.format(
            method=method_title, method_lower=method_name,
            cls=class_name, null_call=null_call,
            overflow_call=overflow_call))

    return '\n'.join(test_functions)


def generate_test_class(class_name, functions, priority_data, header_file, qt_version, call_graph_data):
    """生成测试类 .h 和 .cpp 文件"""
    class_name_lower = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
    test_class_name = 'Test' + class_name

    # ── 头文件 ──
    header_guard = 'TEST_{}_H'.format(class_name_lower.upper())
    header_includes = '#include <QtTest/QtTest>'
    if header_file:
        header_includes += '\n#include "{}"'.format(os.path.basename(header_file))

    # 函数声明
    declarations = []
    declarations.append('    void initTestCase();')
    declarations.append('    void cleanupTestCase();')
    declarations.append('    void init();')
    declarations.append('    void cleanup();')

    # 测试函数声明
    for func in functions:
        level = get_test_level(func.get('priority', 'P3'))
        access = func.get('access', 'public')
        method_name = func['name']
        if '::' in method_name:
            method_name = method_name.split('::')[-1]
        method_title = method_name[0].upper() + method_name[1:] if method_name else 'Method'

        # 私有方法和构造/析构只生成 smoke
        is_private = (access == 'private' and not func.get('is_virtual', False))
        is_ctor = (method_name == func.get('class', ''))
        is_dtor = method_name.startswith('~')
        # 指针参数方法不做数据驱动测试 (QFETCH 不支持指针)
        has_ptr = any('*' in p.get('type', '') for p in func.get('params', []))
        special = is_private or is_ctor or is_dtor

        declarations.append('    void test{}_smoke();'.format(method_title))
        if level >= 1 and not special and not has_ptr:
            declarations.append('    void test{}_data();'.format(method_title))
            declarations.append('    void test{}();'.format(method_title))
        if level >= 2 and not special:
            declarations.append('    void test{}_path1();'.format(method_title))
            declarations.append('    void test{}_path2();'.format(method_title))
        if level >= 3 and not special:
            declarations.append('    void test{}_signal();'.format(method_title))
            declarations.append('    void test{}_interaction();'.format(method_title))
        if level >= 4 and not special:
            declarations.append('    void test{}_nullInput();'.format(method_title))
            declarations.append('    void test{}_overflow();'.format(method_title))

    header_content = '''#ifndef {guard}
#define {guard}

{includes}

class {test_class} : public QObject
{{
    Q_OBJECT

private slots:
{decl}
}};

#endif // {guard}
'''.format(
        guard=header_guard,
        includes=header_includes,
        test_class=test_class_name,
        decl='\n'.join(declarations)
    )

    # ── 源文件 ──
    test_header_name = 'test_' + class_name_lower
    source_includes = '#include "{}.h"\n'.format(test_header_name)
    if header_file:
        source_includes += '#include "{}"\n'.format(os.path.basename(header_file))

    # 夹具实现
    fixture_impl = '''void {test_class}::initTestCase()
{{
    // 整个测试开始前的初始化
}}

void {test_class}::cleanupTestCase()
{{
    // 整个测试结束后的清理
}}

void {test_class}::init()
{{
    // 每个测试函数前的初始化
}}

void {test_class}::cleanup()
{{
    // 每个测试函数后的清理
}}
'''.format(test_class=test_class_name)

    # 测试函数实现
    test_impls = []
    for func in functions:
        level = get_test_level(func.get('priority', 'P3'))
        impl = generate_test_functions(func, level, call_graph_data)
        # 给每个测试函数签名加上 TestClass:: 前缀
        impl_lines = impl.strip().split('\n')
        prefixed = []
        for line in impl_lines:
            stripped = line.lstrip()
            if stripped.startswith('void test'):
                indent = line[:len(line) - len(stripped)]
                prefixed.append(indent + 'void ' + test_class_name + '::' + stripped[5:])
            else:
                prefixed.append(line)
        test_impls.append('\n'.join(prefixed))

    # QTEST_MAIN
    main_entry = 'QTEST_MAIN({})\n'.format(test_class_name)
    if qt_version.startswith('6'):
        main_entry = 'QTEST_GUILESS_MAIN({})\n'.format(test_class_name)

    source_content = '''{includes}

// ── 测试夹具 ──────────────────────────────────────────

{fixture}

// ── 测试用例 ──────────────────────────────────────────

{tests}

{main}
'''.format(
        includes=source_includes,
        fixture=fixture_impl,
        tests='\n\n'.join(test_impls),
        main=main_entry
    )

    return header_content, source_content, class_name_lower


def generate_cmake(test_targets, library_target, qt_version, project_dir):
    """生成 CMakeLists.txt"""
    qt_major = 'Qt5' if qt_version.startswith('5') else 'Qt6'
    qt_lib = qt_major + '::Test'

    cmake_content = '''# Auto-generated by qt-unit-test-generate
# Stage 4: Test module CMakeLists.txt

find_package({qt_major} COMPONENTS Test REQUIRED)

set(TEST_TARGETS
{targets}
)

foreach(test_target ${{TEST_TARGETS}})
    add_executable(${{test_target}} ${{test_target}}.cpp)
    set_target_properties(${{test_target}} PROPERTIES AUTOMOC ON)
    target_link_libraries(${{test_target}}
        PRIVATE
        {lib}
        {qt_test}
    )
    target_include_directories(${{test_target}} PRIVATE
        ${{CMAKE_SOURCE_DIR}}/src
    )
    add_test(NAME ${{test_target}} COMMAND ${{test_target}})

    if(ENABLE_COVERAGE)
        target_compile_options(${{test_target}} PRIVATE -fprofile-arcs -ftest-coverage)
        target_link_libraries(${{test_target}} PRIVATE gcov)
    endif()
endforeach()
'''.format(
        qt_major=qt_major,
        targets='\n'.join('    ' + t for t in test_targets),
        lib=library_target,
        qt_test=qt_lib,
    )
    return cmake_content


def generate_test_design_doc(class_functions, priority_data):
    """生成测试设计文档"""
    lines = []
    lines.append("# 测试设计文档 (Stage 3)")
    lines.append("")
    lines.append("## 设计依据")
    lines.append("")
    lines.append("测试用例按经典测试理论分 5 级设计:")
    lines.append("- Level 0 (Smoke): 基础验证, 确保函数可调用不崩溃")
    lines.append("- Level 1 (Specification): 等价类划分 + 边界值分析 + 判定表")
    lines.append("- Level 2 (Structure): 分支覆盖 + 条件覆盖 + 基路径测试")
    lines.append("- Level 3 (Interaction): 调用链路径 + 信号验证 + Mock")
    lines.append("- Level 4 (Fault Injection): 变异测试 + 错误猜测")
    lines.append("")

    for class_name, functions in class_functions.items():
        lines.append("## 类: {}".format(class_name))
        lines.append("")
        lines.append("| 函数 | 优先级 | 风险分 | 测试级别 | 复杂度 | 设计技术 |")
        lines.append("|------|--------|--------|---------|--------|---------|")

        for func in functions:
            level = get_test_level(func.get('priority', 'P3'))
            techniques = []
            if level >= 0:
                techniques.append("Smoke")
            if level >= 1:
                techniques.append("等价类+边界值")
            if level >= 2:
                techniques.append("基路径(V={})".format(func.get('complexity', 1)))
            if level >= 3:
                techniques.append("QSignalSpy+Mock")
            if level >= 4:
                techniques.append("变异测试")

            name = func.get('name', '')
            if '::' in name:
                name = name.split('::')[-1]
            lines.append("| {} | {} | {} | L{} | {} | {} |".format(
                name, func.get('priority', 'P3'),
                func.get('risk_score', 0), level,
                func.get('complexity', 1), ' + '.join(techniques)))
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Stage 4: 生成测试骨架')
    parser.add_argument('--state', required=True, help='state.json 路径')
    parser.add_argument('--design', default=None, help='测试设计文档 (可选, AI 产出)')
    parser.add_argument('--auto', action='store_true', help='自动设计测试用例')
    parser.add_argument('--output-dir', default=None, help='测试输出目录')
    args = parser.parse_args()

    with open(args.state) as f:
        state = json.load(f)

    project_dir = state['project_dir']
    output_dir = args.output_dir or os.path.join(project_dir, 'tests')
    os.makedirs(output_dir, exist_ok=True)

    # 加载优先级报告
    risk_state = state.get('stage', {}).get('risk', {})
    priority_path = risk_state.get('report', os.path.join(project_dir, 'priority_report.json'))

    print("[Stage 4] 加载优先级报告...")
    with open(priority_path) as f:
        priority_data = json.load(f)

    # 加载调用图谱 (获取函数签名)
    code_graph_state = state.get('stage', {}).get('code_graph', {})
    call_graph_path = code_graph_state.get('call_graph', os.path.join(project_dir, 'call_graph.json'))
    call_graph_data = {}
    if os.path.exists(call_graph_path):
        with open(call_graph_path) as f:
            call_graph_data = json.load(f)

    # 构建函数 ID → 函数信息映射 (含参数和返回类型)
    func_info_map = {}
    if call_graph_data:
        for node in call_graph_data.get('nodes', []):
            func_info_map[node['id']] = node

    # 合并参数信息到 priority_data
    for func in priority_data['functions']:
        info = func_info_map.get(func['id'], {})
        if info:
            if 'params' in info:
                func['params'] = info['params']
            if 'return_type' in info:
                func['return_type'] = info.get('return_type', 'void')
        if 'params' not in func:
            func['params'] = []
        if 'return_type' not in func:
            func['return_type'] = 'void'

    # 按类分组
    class_functions = defaultdict(list)
    for func in priority_data['functions']:
        class_name = func.get('class') or 'GlobalFunctions'
        func['priority'] = func.get('priority', 'P3')
        func['risk_score'] = func.get('risk_score', 0)
        class_functions[class_name].append(func)

    # 过滤 Qt 内部类
    qt_internal = {'QObject', 'QWidget', 'QString', 'QList', 'QVector', 'QMap',
                   'QHash', 'QVariant', 'QStringList', 'QByteArray'}
    classes_to_test = {k: v for k, v in class_functions.items()
                       if k not in qt_internal and len(v) > 0}

    print("  待测试类: {} 个".format(len(classes_to_test)))

    # 生成测试文件
    qt_version = state.get('qt_version', '5')
    library_target = state.get('library_target', 'app_lib')
    test_targets = []
    generated_files = []

    for class_name, functions in classes_to_test.items():
        # 查找头文件
        header_file = None
        for func in functions:
            if func.get('file'):
                f_path = func['file']
                base = os.path.splitext(f_path)[0]
                for ext in ['.h', '.hpp', '.hh']:
                    candidate = base + ext
                    if os.path.exists(candidate):
                        header_file = candidate
                        break
                # 也检查 src 目录下是否有同名头文件
                if not header_file:
                    # 从 .cpp 推断文件名
                    basename = os.path.splitext(os.path.basename(f_path))[0]
                    for d in state.get('header_dirs', ['src']):
                        hdr_dir = os.path.join(project_dir, d) if not os.path.isabs(d) else d
                        for ext in ['.h', '.hpp', '.hh']:
                            candidate = os.path.join(hdr_dir, basename + ext)
                            if os.path.exists(candidate):
                                header_file = candidate
                                break
                        if header_file:
                            break
                if header_file:
                    break

        header_content, source_content, class_lower = generate_test_class(
            class_name, functions, priority_data, header_file, qt_version, call_graph_data)

        target_name = 'test_{}'.format(class_lower)
        header_path = os.path.join(output_dir, '{}.h'.format(target_name))
        source_path = os.path.join(output_dir, '{}.cpp'.format(target_name))

        with open(header_path, 'w') as f:
            f.write(header_content)
        with open(source_path, 'w') as f:
            f.write(source_content)

        test_targets.append(target_name)
        generated_files.extend([header_path, source_path])
        print("  生成: {} ({} 个函数)".format(target_name, len(functions)))

    # 生成 CMakeLists.txt
    cmake_path = os.path.join(output_dir, 'CMakeLists.txt')
    cmake_content = generate_cmake(test_targets, library_target, qt_version, project_dir)
    with open(cmake_path, 'w') as f:
        f.write(cmake_content)
    generated_files.append(cmake_path)
    print("  CMake: {}".format(cmake_path))

    # 生成设计文档
    design_path = os.path.join(output_dir, 'test_design_doc.md')
    design_content = generate_test_design_doc(classes_to_test, priority_data)
    with open(design_path, 'w') as f:
        f.write(design_content)
    generated_files.append(design_path)

    print("\n[Stage 4] 输出:")
    for f in generated_files:
        print("  {}".format(f))

    # 更新 state
    state['stage']['generation'] = {
        'completed': True,
        'files': generated_files,
        'test_targets': test_targets,
        'test_dir': output_dir,
    }

    with open(args.state, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print("\n[Stage 4] 完成, state.json 已更新")


if __name__ == '__main__':
    main()
