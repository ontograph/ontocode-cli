#!/usr/bin/env python3
"""
build_call_graph.py — Stage 1: 构建 AST 级调用图谱、依赖图谱、复杂度报告

用法:
    python3 build_call_graph.py --state state.json [--source-dir src/] [--output-dir .]

输入: state.json (Stage 0 产出)
输出: call_graph.json, dependency_graph.json, complexity_report.json
"""

import argparse
import json
import os
import sys
import hashlib
import glob
import subprocess
from collections import defaultdict

# libclang 初始化
LIBCLANG_PATHS = [
    '/usr/lib/llvm-13/lib/libclang.so',
    '/usr/lib/llvm-12/lib/libclang.so',
    '/usr/lib/llvm-11/lib/libclang.so',
    '/usr/lib/llvm-7/lib/libclang.so',
    '/usr/lib/x86_64-linux-gnu/libclang.so',
]

def init_clang():
    import clang.cindex as cindex
    for path in LIBCLANG_PATHS:
        if os.path.exists(path):
            cindex.Config.set_library_file(path)
            return cindex
    # 尝试不设路径 (有些环境自动发现)
    return cindex

clang = init_clang()
# clang 在这里就是 clang.cindex 模块本身


# ── 节点 ID 生成 ──────────────────────────────────────────────

def make_node_id(name, file_path, line):
    """生成唯一节点 ID"""
    h = hashlib.md5(f"{name}@{file_path}:{line}".encode()).hexdigest()[:8]
    return f"{name}#{h}"


# ── 文件发现 ───────────────────────────────────────────────────

def find_source_files(source_dirs, extensions=None):
    """递归查找所有 C++ 源文件"""
    if extensions is None:
        extensions = ['.cpp', '.cc', '.cxx', '.c']
    files = []
    for d in source_dirs:
        if not os.path.isdir(d):
            d = os.path.join(os.getcwd(), d)
        for ext in extensions:
            files.extend(glob.glob(os.path.join(d, '**', '*' + ext), recursive=True))
    return sorted(set(files))


def find_header_files(header_dirs, extensions=None):
    if extensions is None:
        extensions = ['.h', '.hpp', '.hh', '.hxx']
    files = []
    for d in header_dirs:
        if not os.path.isdir(d):
            d = os.path.join(os.getcwd(), d)
        for ext in extensions:
            files.extend(glob.glob(os.path.join(d, '**', '*' + ext), recursive=True))
    return sorted(set(files))


# ── 编译参数提取 ───────────────────────────────────────────────

def extract_compile_args(state):
    """从 state.json 提取编译参数"""
    args = ['-x', 'c++', '-fPIC']

    # 标准
    std = state.get('cpp_standard', 'c++14')
    args.append('--std=' + std)

    # include 路径
    for inc in state.get('include_dirs', []):
        args.append('-I' + inc)

    # Qt include 路径 (自动检测)
    qt_version = state.get('qt_version', '5')
    qt_include = '/usr/include/x86_64-linux-gnu/qt{}'.format(qt_version)
    if os.path.isdir(qt_include):
        args.append('-I' + qt_include)
        for module in state.get('qt_modules', ['QtCore']):
            mod_path = os.path.join(qt_include, module)
            if os.path.isdir(mod_path):
                args.append('-I' + mod_path)

    # 编译器 flags
    for flag in state.get('compiler_flags', []):
        if flag and flag not in args:
            args.append(flag)

    # define 宏
    for define in state.get('defines', []):
        args.append('-D' + define)

    return args


def load_compile_commands(state):
    """从 compile_commands.json 提取每个文件的编译参数"""
    compile_db_path = state.get('compile_commands_path')
    if not compile_db_path:
        # 尝试在 build 目录查找
        build_dir = state.get('build_dir', os.path.join(state['project_dir'], 'build'))
        candidate = os.path.join(build_dir, 'compile_commands.json')
        if os.path.exists(candidate):
            compile_db_path = candidate

    if not compile_db_path or not os.path.exists(compile_db_path):
        return {}

    with open(compile_db_path) as f:
        entries = json.load(f)

    file_args = {}
    for entry in entries:
        filepath = entry['file']
        command = entry.get('command', '')
        # 解析 command 中的参数
        parts = command.split()
        # 找到 -I, -D, --std, -f 等参数
        file_args[filepath] = parts
    return file_args


# ── AST 遍历: 函数和方法 ─────────────────────────────────────

FUNCTION_KINDS = {
    clang.CursorKind.FUNCTION_DECL,
    clang.CursorKind.CXX_METHOD,
    clang.CursorKind.CONSTRUCTOR,
    clang.CursorKind.DESTRUCTOR,
    clang.CursorKind.FUNCTION_TEMPLATE,
}

CLASS_KINDS = {
    clang.CursorKind.CLASS_DECL,
    clang.CursorKind.STRUCT_DECL,
    clang.CursorKind.CLASS_TEMPLATE,
}

DECISION_KINDS = {
    clang.CursorKind.IF_STMT,
    clang.CursorKind.FOR_STMT,
    clang.CursorKind.WHILE_STMT,
    clang.CursorKind.DO_STMT,
    clang.CursorKind.SWITCH_STMT,
    clang.CursorKind.CXX_CATCH_STMT,
}


def get_qualified_name(cursor):
    """获取函数的限定名 (含类名)"""
    parts = []
    node = cursor
    while node is not None:
        if node.kind in FUNCTION_KINDS or node.kind in CLASS_KINDS:
            parts.append(node.spelling)
        if node.kind == clang.CursorKind.NAMESPACE and node.spelling:
            parts.append(node.spelling)
        node = node.semantic_parent
    return '::'.join(reversed(parts)) if parts else cursor.spelling


def get_access_modifier(cursor):
    """获取访问修饰符"""
    accessors = {
        clang.AccessSpecifier.PUBLIC: 'public',
        clang.AccessSpecifier.PROTECTED: 'protected',
        clang.AccessSpecifier.PRIVATE: 'private',
    }
    return accessors.get(cursor.access_specifier, 'public')


def extract_function_info(cursor, file_path):
    """提取函数信息"""
    name = cursor.spelling
    if not name:
        return None

    qualified = get_qualified_name(cursor)
    line = cursor.location.line if cursor.location.file else 0

    # 参数
    params = []
    for arg in cursor.get_arguments():
        param_type = arg.type.spelling if arg.type else 'unknown'
        params.append({'name': arg.spelling, 'type': param_type})

    # 返回类型
    return_type = cursor.result_type.spelling if cursor.result_type else 'void'

    # 访问修饰符
    access = get_access_modifier(cursor)

    # 是否是信号/槽
    is_signal = False
    is_slot = False
    # libclang 无法直接区分 Q_SLOTS/slots: 段和普通 public/private 方法,
    # 因为 moc 关键字 Q_SLOTS/Q_SIGNALS 被预处理后变成了访问修饰符。
    # 只有当 moc 生成的文件被解析时才能准确识别信号槽。
    # 这里用启发式: 信号 = 无定义体 + public + 返回 void (Qt 信号约定)
    # 槽 = 无法从源码可靠判断, 默认为 False, 需要人工或 moc 输出辅助
    node = cursor
    parent = node.semantic_parent
    if parent and parent.kind in CLASS_KINDS:
        if name and not name.startswith('m_'):
            if not cursor.is_definition() and access == 'public':
                # 可能是纯虚函数或信号
                if cursor.result_type and 'void' in cursor.result_type.spelling:
                    is_signal = True

    return {
        'id': make_node_id(qualified, file_path, line),
        'name': name,
        'qualified_name': qualified,
        'class': parent.spelling if parent and parent.kind in CLASS_KINDS else None,
        'file': file_path,
        'line': line,
        'params': params,
        'return_type': return_type,
        'access': access,
        'is_signal': is_signal,
        'is_slot': is_slot,
        'is_virtual': cursor.is_virtual_method(),
        'is_static': cursor.is_static_method(),
    }


def extract_calls(cursor):
    """从函数体中提取所有函数调用"""
    calls = []
    seen = set()
    for child in cursor.walk_preorder():
        if child.kind == clang.CursorKind.CALL_EXPR:
            callee = child.referenced
            if callee and callee.kind in FUNCTION_KINDS:
                callee_qualified = get_qualified_name(callee)
                # 优先使用 definition 的 location (定义位置)
                callee_def = callee.get_definition()
                if callee_def and callee_def.location and callee_def.location.file:
                    callee_file = callee_def.location.file.name
                    callee_line = callee_def.location.line
                else:
                    callee_file = callee.location.file.name if callee.location.file else 'unknown'
                    callee_line = callee.location.line if callee.location.file else 0
                callee_id = make_node_id(callee_qualified, callee_file, callee_line)
                # 去重 (同一函数中多次调用同一目标只记一次)
                key = callee_id
                if key not in seen:
                    seen.add(key)
                    calls.append({
                        'callee_id': callee_id,
                        'callee_name': callee_qualified,
                        'callee_file': callee_file,
                        'callee_line': callee_line,
                        'call_line': child.location.line if child.location.file else 0,
                    })
    return calls


def calculate_complexity(cursor):
    """计算 McCabe 圈复杂度"""
    decisions = 0
    for child in cursor.walk_preorder():
        if child.kind in DECISION_KINDS:
            if child.kind == clang.CursorKind.SWITCH_STMT:
                cases = sum(1 for c in child.get_children()
                           if c.kind == clang.CursorKind.CASE_STMT)
                decisions += max(cases, 1)
            else:
                decisions += 1
        elif child.kind == clang.CursorKind.BINARY_OPERATOR:
            # 检查是否是 && 或 ||
            for tok in child.get_tokens():
                if tok.spelling in ('&&', '||'):
                    decisions += 1
                    break
        elif child.kind == clang.CursorKind.CONDITIONAL_OPERATOR:
            decisions += 1
    return decisions + 1


def extract_inheritance(cursor):
    """提取类的继承关系"""
    parents = []
    if cursor.kind in CLASS_KINDS:
        for child in cursor.get_children():
            if child.kind == clang.CursorKind.CXX_BASE_SPECIFIER:
                # 获取基类名
                base_type = child.type
                if base_type:
                    parents.append({
                        'name': base_type.spelling,
                        'access': get_access_modifier(child),
                    })
    return parents


def extract_includes(tu):
    """提取 #include 依赖"""
    includes = []
    for child in tu.cursor.get_children():
        if child.kind == clang.CursorKind.INCLUSION_DIRECTIVE:
            # include 文件名
            include_name = ''
            for tok in child.get_tokens():
                if tok.spelling and ('.' in tok.spelling or '/' in tok.spelling):
                    include_name = tok.spelling.strip('<>"')
                    break
            if include_name:
                includes.append(include_name)
    return includes


# ── 主处理流程 ────────────────────────────────────────────────

def process_file(filepath, args, index):
    """解析单个文件，提取函数、调用、继承、复杂度"""
    try:
        tu = index.parse(filepath, args=args)
    except Exception as e:
        print("  WARNING: parse failed for {}: {}".format(filepath, e), file=sys.stderr)
        return [], [], [], []

    # 检查诊断信息
    diagnostics = list(tu.diagnostics)
    fatal_diags = [d for d in diagnostics if d.severity >= clang.Diagnostic.Error]
    if fatal_diags:
        print("  WARNING: {} has {} error diagnostics".format(
            os.path.basename(filepath), len(fatal_diags)), file=sys.stderr)

    functions = []
    calls = []
    inheritance = []
    includes = extract_includes(tu)

    for node in tu.cursor.walk_preorder():
        try:
            node_kind = node.kind
        except (ValueError, RuntimeError):
            continue  # 跳过无法识别的节点 (版本不兼容)

        # 函数/方法
        if node_kind in FUNCTION_KINDS and node.location.file:
            if os.path.abspath(node.location.file.name) != os.path.abspath(filepath):
                continue  # 只收集本文件定义的函数
            if not node.is_definition() and not node.is_pure_virtual_method():
                continue  # 跳过声明 (非定义)

            func_info = extract_function_info(node, filepath)
            if func_info:
                func_info['complexity'] = calculate_complexity(node)
                functions.append(func_info)

                # 提取调用
                func_calls = extract_calls(node)
                for call in func_calls:
                    calls.append({
                        'caller_id': func_info['id'],
                        'caller_name': func_info['qualified_name'],
                        **call,
                    })

        # 类继承
        if node_kind in CLASS_KINDS and node.location.file:
            if os.path.abspath(node.location.file.name) != os.path.abspath(filepath):
                continue
            parents = extract_inheritance(node)
            if parents:
                inheritance.append({
                    'class': node.spelling,
                    'file': filepath,
                    'parents': parents,
                })

    return functions, calls, inheritance, includes


def build_graphs(state, output_dir):
    """主函数: 构建调用图谱、依赖图谱、复杂度报告"""
    project_dir = state['project_dir']
    source_dirs = state.get('source_dirs', ['src'])
    source_dirs = [os.path.join(project_dir, d) if not os.path.isabs(d) else d
                   for d in source_dirs]
    header_dirs = state.get('header_dirs', source_dirs)
    header_dirs = [os.path.join(project_dir, d) if not os.path.isabs(d) else d
                   for d in header_dirs]

    print("[Stage 1] 扫描源文件...")
    source_files = find_source_files(source_dirs)
    header_files = find_header_files(header_dirs)
    print("  源文件: {} 个, 头文件: {} 个".format(len(source_files), len(header_files)))

    if not source_files and not header_files:
        print("  ERROR: 未找到任何源文件", file=sys.stderr)
        return False

    # 编译参数
    default_args = extract_compile_args(state)
    file_args_map = load_compile_commands(state)
    if file_args_map:
        print("  使用 compile_commands.json ({} 个文件)".format(len(file_args_map)))
    else:
        print("  使用默认编译参数")

    index = clang.Index.create()
    all_functions = []
    all_calls = []
    all_inheritance = []
    all_includes = defaultdict(list)

    # 解析所有文件
    all_files = source_files + header_files
    for i, filepath in enumerate(all_files):
        rel = os.path.relpath(filepath, project_dir)
        print("  [{}/{}] 解析 {}".format(i + 1, len(all_files), rel))

        # 优先使用 compile_commands.json 中的参数
        args = file_args_map.get(filepath, default_args)
        funcs, calls, inherit, includes = process_file(filepath, args, index)

        all_functions.extend(funcs)
        all_calls.extend(calls)
        all_inheritance.extend(inherit)
        for inc in includes:
            all_includes[filepath].append(inc)

    print("\n[Stage 1] 构建图谱...")
    print("  函数/方法: {} 个".format(len(all_functions)))
    print("  调用关系: {} 条".format(len(all_calls)))
    print("  继承关系: {} 条".format(len(all_inheritance)))

    # ── 调用图谱 (JSON 格式, 兼容 networkx node-link format) ──
    call_graph = {
        'directed': True,
        'graph': {'name': 'call_graph'},
        'nodes': [],
        'links': [],
    }

    # 函数 ID → 函数信息映射 (用于去重)
    func_map = {}
    for func in all_functions:
        if func['id'] not in func_map:
            func_map[func['id']] = func
            call_graph['nodes'].append({
                'id': func['id'],
                'name': func['qualified_name'],
                'file': func['file'],
                'line': func['line'],
                'complexity': func['complexity'],
                'access': func['access'],
                'class': func['class'],
                'is_virtual': func['is_virtual'],
                'is_static': func['is_static'],
                'is_signal': func['is_signal'],
                'is_slot': func['is_slot'],
                'params': func['params'],
                'return_type': func['return_type'],
            })

    # 添加调用边 (去重)
    seen_edges = set()
    for call in all_calls:
        edge_key = (call['caller_id'], call['callee_id'])
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            call_graph['links'].append({
                'source': call['caller_id'],
                'target': call['callee_id'],
                'caller_line': call.get('call_line', 0),
            })

    # ── 依赖图谱 ──
    dep_graph = {
        'directed': True,
        'graph': {'name': 'dependency_graph'},
        'nodes': [],
        'links': [],
    }

    # 继承边
    dep_nodes = set()
    for inherit in all_inheritance:
        child_id = "{}::{}".format(inherit['file'], inherit['class'])
        dep_nodes.add(child_id)
        for parent in inherit['parents']:
            parent_id = "parent::{}".format(parent['name'])
            dep_nodes.add(parent_id)
            dep_graph['links'].append({
                'source': child_id,
                'target': parent_id,
                'type': 'inheritance',
            })

    # include 依赖边
    for filepath, includes in all_includes.items():
        file_id = filepath
        dep_nodes.add(file_id)
        for inc in includes:
            inc_id = "include::{}".format(inc)
            dep_nodes.add(inc_id)
            dep_graph['links'].append({
                'source': file_id,
                'target': inc_id,
                'type': 'include',
            })

    for node_id in dep_nodes:
        dep_graph['nodes'].append({'id': node_id})

    # ── 复杂度报告 ──
    complexity_report = {
        'functions': [],
        'summary': {
            'total_functions': len(func_map),
            'max_complexity': 0,
            'avg_complexity': 0,
            'high_complexity_count': 0,  # >= 15
            'very_high_complexity_count': 0,  # >= 20
        }
    }

    total_complexity = 0
    for func_id, func in func_map.items():
        cx = func['complexity']
        total_complexity += cx
        complexity_report['functions'].append({
            'id': func_id,
            'name': func['qualified_name'],
            'file': func['file'],
            'line': func['line'],
            'complexity': cx,
            'access': func['access'],
            'class': func['class'],
            'params': func['params'],
            'return_type': func['return_type'],
        })
        if cx >= 20:
            complexity_report['summary']['very_high_complexity_count'] += 1
        if cx >= 15:
            complexity_report['summary']['high_complexity_count'] += 1

    if func_map:
        complexity_report['summary']['max_complexity'] = max(
            f['complexity'] for f in func_map.values())
        complexity_report['summary']['avg_complexity'] = round(
            total_complexity / len(func_map), 2)

    # ── 写入文件 ──
    call_graph_path = os.path.join(output_dir, 'call_graph.json')
    dep_graph_path = os.path.join(output_dir, 'dependency_graph.json')
    complexity_path = os.path.join(output_dir, 'complexity_report.json')

    with open(call_graph_path, 'w') as f:
        json.dump(call_graph, f, indent=2, ensure_ascii=False)
    with open(dep_graph_path, 'w') as f:
        json.dump(dep_graph, f, indent=2, ensure_ascii=False)
    with open(complexity_path, 'w') as f:
        json.dump(complexity_report, f, indent=2, ensure_ascii=False)

    print("\n[Stage 1] 输出:")
    print("  调用图谱: {} ({} 节点, {} 边)".format(
        call_graph_path, len(call_graph['nodes']), len(call_graph['links'])))
    print("  依赖图谱: {} ({} 节点, {} 边)".format(
        dep_graph_path, len(dep_graph['nodes']), len(dep_graph['links'])))
    print("  复杂度报告: {} ({} 函数, 最高复杂度 {}, 高复杂度 {} 个)".format(
        complexity_path, complexity_report['summary']['total_functions'],
        complexity_report['summary']['max_complexity'],
        complexity_report['summary']['high_complexity_count']))

    # 更新 state.json
    state['stage']['code_graph'] = {
        'completed': True,
        'call_graph': call_graph_path,
        'dependency_graph': dep_graph_path,
        'complexity_report': complexity_path,
        'node_count': len(call_graph['nodes']),
        'edge_count': len(call_graph['links']),
    }

    return True


def main():
    parser = argparse.ArgumentParser(description='Stage 1: 构建代码图谱')
    parser.add_argument('--state', required=True, help='state.json 路径')
    parser.add_argument('--source-dir', action='append', default=None,
                        help='源码目录 (可多次指定, 覆盖 state.json)')
    parser.add_argument('--output-dir', default=None,
                        help='输出目录 (默认与 state.json 同目录)')
    args = parser.parse_args()

    with open(args.state) as f:
        state = json.load(f)

    if args.source_dir:
        state['source_dirs'] = args.source_dir

    output_dir = args.output_dir or os.path.dirname(os.path.abspath(args.state))

    if 'stage' not in state:
        state['stage'] = {}

    success = build_graphs(state, output_dir)

    if success:
        with open(args.state, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print("\n[Stage 1] 完成, state.json 已更新")
    else:
        print("\n[Stage 1] 失败", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
