#!/usr/bin/env python3
"""
mutation_score.py — Stage 6: 变异测试 (Mutation Testing)

用法:
    python3 mutation_score.py --state state.json [--function Calculator::add]
    python3 mutation_score.py --state state.json --all-p0

功能:
    1. 从 priority_report.json 选择 P0 函数 (或指定函数)
    2. 对源码应用变异算子 (AOR/ROR/LOR/CRC/RVF)
    3. 编译每个变异体 (独立 build 目录)
    4. 运行测试集，判断杀死/存活
    5. 计算变异得分 (Mutation Score)
    6. 生成报告

变异算子:
    AOR: 算术运算符替换 (+ → -, *, /)
    ROR: 关系运算符替换 (< → <=, >, >=, ==, !=)
    LOR: 逻辑运算符替换 (&& → ||, ! → 去掉)
    CRC: 常量替换 (0 → 1, 1 → 0, n → n+1)
    RVF: 返回值修改 (return true → return false)
    SDL: 语句删除 (删除赋值语句)

参考: Lipton (1978), Offutt & Untch (2001)
"""

import argparse
import json
import os
import re
import sys
import shutil
import atexit
import signal
import subprocess
import tempfile
from collections import defaultdict


# ── 全局: 变异测试源码恢复 (atexit + signal) ───────────────────
# 如果进程被 kill/中断, 确保源码从 .mutation_backup 恢复
_PENDING_RESTORES = []  # [(backup_path, source_file), ...]

def _restore_on_exit():
    for backup_path, source_file in _PENDING_RESTORES:
        if os.path.exists(backup_path):
            try:
                shutil.move(backup_path, source_file)
            except Exception:
                pass

atexit.register(_restore_on_exit)

def _signal_handler(signum, frame):
    _restore_on_exit()
    sys.exit(128 + signum)

signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


# ── 变异算子定义 ─────────────────────────────────────────────

# AOR: 算术运算符替换
AOR_MAP = {
    '+': ['-', '*', '/'],
    '-': ['+', '*', '/'],
    '*': ['/', '+', '-'],
    '/': ['*', '+', '-'],
    '%': ['*', '/', '+'],
}

# ROR: 关系运算符替换
ROR_MAP = {
    '<':  ['<=', '>', '>=', '==', '!='],
    '>':  ['>=', '<', '<=', '==', '!='],
    '<=': ['<', '>', '>=', '==', '!='],
    '>=': ['>', '<', '<=', '==', '!='],
    '==': ['!=', '<', '>', '<=', '>='],
    '!=': ['==', '<', '>', '<=', '>='],
}

# LOR: 逻辑运算符替换
LOR_MAP = {
    '&&': ['||'],
    '||': ['&&'],
}

# RVF: 返回值修改
RVF_BOOL_MAP = {
    'return true':  ['return false'],
    'return false': ['return true'],
}


def generate_aor_mutants(lines, func_start, func_end):
    """算术运算符替换变异体"""
    mutants = []
    for i in range(func_start, func_end):
        line = lines[i]
        for op, replacements in AOR_MAP.items():
            if op not in line:
                continue
            # 跳过注释行
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue
            if in_string(line, op):
                continue
            # 找到 op 的位置
            op_idx = line.find(op)
            if op_idx >= 0:
                # 跳过一元运算符 (如 -1, +a)
                if _is_unary_op(line, op_idx, op):
                    continue
                # 检查是否是复合运算符 (如 +=, -=, *=, /=, ++, --)
                after = line[op_idx + 1:op_idx + 2] if op_idx + 1 < len(line) else ''
                before_char = line[op_idx - 1] if op_idx > 0 else ''
                if after == '=' or before_char in ('+', '-', '*', '/'):
                    continue  # 复合赋值或自增自减, 跳过
            for repl in replacements:
                new_line = line.replace(op, repl, 1)
                if new_line != line:
                    mutants.append({
                        'id': 'AOR_{}_{}_{}'.format(i, op, repl),
                        'line': i + 1,  # 1-indexed
                        'operator': 'AOR',
                        'original': op,
                        'replacement': repl,
                        'description': 'L{}: {} → {}'.format(i + 1, op, repl),
                    })
    return mutants


def generate_ror_mutants(lines, func_start, func_end):
    """关系运算符替换变异体"""
    mutants = []
    for i in range(func_start, func_end):
        line = lines[i]
        for op, replacements in ROR_MAP.items():
            if op in line and not in_string(line, op):
                # 确保是关系运算符 (不是赋值 == 的情况)
                for repl in replacements:
                    new_line = line.replace(op, repl, 1)
                    if new_line != line:
                        mutants.append({
                            'id': 'ROR_{}_{}_{}'.format(i, op, repl),
                            'line': i + 1,
                            'operator': 'ROR',
                            'original': op,
                            'replacement': repl,
                            'description': 'L{}: {} → {}'.format(i + 1, op, repl),
                        })
    return mutants


def generate_lor_mutants(lines, func_start, func_end):
    """逻辑运算符替换变异体"""
    mutants = []
    for i in range(func_start, func_end):
        line = lines[i]
        for op, replacements in LOR_MAP.items():
            if op in line and not in_string(line, op):
                for repl in replacements:
                    new_line = line.replace(op, repl, 1)
                    if new_line != line:
                        mutants.append({
                            'id': 'LOR_{}_{}_{}'.format(i, op, repl),
                            'line': i + 1,
                            'operator': 'LOR',
                            'original': op,
                            'replacement': repl,
                            'description': 'L{}: {} → {}'.format(i + 1, op, repl),
                        })
    return mutants


def generate_crc_mutants(lines, func_start, func_end):
    """常量替换变异体"""
    mutants = []
    # 匹配整数常量
    int_pattern = re.compile(r'\b(\d+)\b')
    for i in range(func_start, func_end):
        line = lines[i]
        for m in int_pattern.finditer(line):
            val = int(m.group(1))
            pos = m.start()
            # 检查不在字符串中
            prefix = line[:pos]
            if prefix.count('"') % 2 == 1:
                continue
            # 生成变异
            if val == 0:
                replacements = [1, -1]
            elif val == 1:
                replacements = [0, 2]
            elif val == -1:
                replacements = [0, 1]
            else:
                replacements = [val + 1, val - 1]

            for repl in replacements:
                mutants.append({
                    'id': 'CRC_{}_{}_{}'.format(i, val, repl),
                    'line': i + 1,
                    'operator': 'CRC',
                    'original': str(val),
                    'replacement': str(repl),
                    'description': 'L{}: {} → {}'.format(i + 1, val, repl),
                })
    return mutants


def generate_rvf_mutants(lines, func_start, func_end):
    """返回值修改变异体"""
    mutants = []
    for i in range(func_start, func_end):
        line = lines[i]
        stripped = line.strip()

        for original, replacements in RVF_BOOL_MAP.items():
            if original in stripped:
                for repl in replacements:
                    mutants.append({
                        'id': 'RVF_{}_{}_{}'.format(i, original, repl),
                        'line': i + 1,
                        'operator': 'RVF',
                        'original': original,
                        'replacement': repl,
                        'description': 'L{}: {} → {}'.format(i + 1, original, repl),
                    })

        # return N → return N+1, return N-1
        return_int = re.search(r'return\s+(-?\d+)\s*;', stripped)
        if return_int:
            val = int(return_int.group(1))
            for repl in [val + 1, val - 1]:
                if repl != val:
                    mutants.append({
                        'id': 'RVF_int_{}_{}_{}'.format(i, val, repl),
                        'line': i + 1,
                        'operator': 'RVF',
                        'original': 'return {}'.format(val),
                        'replacement': 'return {}'.format(repl),
                        'description': 'L{}: return {} → return {}'.format(i + 1, val, repl),
                    })

    return mutants


def in_string(line, token):
    """检查 token 在该行中首次出现是否在字符串/字符字面量或注释中"""
    idx = line.find(token)
    if idx < 0:
        return False
    before = line[:idx]
    in_str = False
    in_char = False
    escape = False
    i = 0
    while i < len(before):
        c = before[i]
        if escape:
            escape = False
        elif c == '\\':
            escape = True
        elif in_str and c == '"':
            in_str = False
        elif in_char and c == "'":
            in_char = False
        elif not in_str and not in_char and c == '"':
            in_str = True
        elif not in_str and not in_char and c == "'":
            in_char = True
        elif not in_str and not in_char and c == '/' and i + 1 < len(before):
            if before[i + 1] == '/' or before[i + 1] == '*':
                return True  # 在注释中
        i += 1
    return in_str or in_char


def _is_unary_op(line, idx, op):
    """检查 idx 处的运算符是否是一元运算符 (符号), 而非二元算术运算符。
    例如: -1 中的 '-' 是一元, a - b 中的 '-' 是二元。
    +1, +a 同理。"""
    if op not in ('+', '-'):
        return False
    # 检查前一个非空白字符
    before = line[:idx].rstrip()
    if not before:
        return True  # 行首, 一元
    last = before[-1]
    # 如果前面是运算符/括号/逗号/等号等, 说明是一元
    if last in '([{,;=>&|!?:*+-%~^':
        return True
    # 如果前面是数字或标识符, 说明是二元
    return False


# ── 函数提取 ─────────────────────────────────────────────────

def find_function_range(lines, function_name):
    """在源码中找到函数的行范围 (0-indexed)"""
    # 函数名匹配: 可能是 ClassName::methodName 或 methodName
    short_name = function_name.split('::')[-1] if '::' in function_name else function_name
    class_name = function_name.split('::')[0] if '::' in function_name else None

    in_func = False
    brace_depth = 0
    func_start = -1
    func_end = -1

    for i, line in enumerate(lines):
        # 检测函数定义行: 包含函数名和 (
        if not in_func and re.search(r'\b' + re.escape(short_name) + r'\s*\(', line):
            # 如果有类名, 也检查类名
            if class_name and class_name not in line and i > 0:
                # 检查前一行是否有类名 (多行定义)
                if class_name not in lines[max(0, i - 1)]:
                    continue
            in_func = True
            func_start = i
            brace_depth = 0

        if in_func:
            brace_depth += line.count('{') - line.count('}')
            if brace_depth <= 0 and '{' in ''.join(lines[func_start:i + 1]):
                func_end = i + 1
                break

    return func_start, func_end


def apply_mutation(lines, mutant, func_start, func_end):
    """应用变异到源码行, 返回新行列表"""
    new_lines = lines[:]
    line_idx = mutant['line'] - 1  # 转回 0-indexed

    if line_idx < func_start or line_idx >= func_end:
        return None

    original = mutant['original']
    replacement = mutant['replacement']

    if mutant['operator'] == 'RVF':
        # 返回值修改: 替换整行中的 return X → return Y
        new_lines[line_idx] = new_lines[line_idx].replace(original, replacement, 1)
    else:
        # 其他: 替换第一个匹配
        new_lines[line_idx] = new_lines[line_idx].replace(original, replacement, 1)

    return new_lines


# ── 编译和测试 ───────────────────────────────────────────────

def run_command(cmd, cwd=None, env=None, timeout=120):
    """运行命令"""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=cwd, env=full_env, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, '', 'Timeout'
    except Exception as e:
        return -2, '', str(e)


def compile_and_test(source_file, mutant_lines, build_dir, project_dir,
                     test_target='test_calculator', timeout=120):
    """
    应用变异, 编译, 运行测试, 返回:
      ('killed', output) - 测试失败 (变异体被杀死)
      ('survived', output) - 测试通过 (变异体存活)
      ('compile_failed', error) - 编译失败
    """
    # 1. 备份原始文件
    backup_path = source_file + '.mutation_backup'
    shutil.copy2(source_file, backup_path)
    restore_entry = (backup_path, source_file)
    _PENDING_RESTORES.append(restore_entry)

    try:
        # 2. 写入变异后的源码
        with open(source_file, 'w') as f:
            f.writelines(mutant_lines)

        # 3. 编译 (在现有 build 目录)
        rc, stdout, stderr = run_command(
            ['make', '-j{}'.format(os.cpu_count() or 4)],
            cwd=build_dir, timeout=timeout
        )

        if rc != 0:
            return 'compile_failed', stderr[:500]

        # 4. 运行测试
        test_exe = os.path.join(build_dir, 'tests', test_target)
        if not os.path.exists(test_exe):
            return 'compile_failed', 'Test executable not found'

        env = {'QT_QPA_PLATFORM': 'offscreen'}
        rc, stdout, stderr = run_command(
            [test_exe], cwd=build_dir, env=env, timeout=60
        )

        # 5. 判断测试结果
        # Qt Test: 非0退出码 或输出含 "FAIL!" → 被杀死
        if rc != 0 or 'FAIL!' in stdout:
            return 'killed', stdout[:500]
        else:
            return 'survived', stdout[:500]

    finally:
        # 恢复原始文件
        shutil.move(backup_path, source_file)
        # 从全局恢复列表中移除 (已恢复)
        if restore_entry in _PENDING_RESTORES:
            _PENDING_RESTORES.remove(restore_entry)
        # 重新编译恢复原始状态 (clean + make 确保完全重建)
        run_command(['make', 'clean'],
                    cwd=build_dir, timeout=timeout)
        run_command(['make', '-j{}'.format(os.cpu_count() or 4)],
                    cwd=build_dir, timeout=timeout)


# ── 主流程 ───────────────────────────────────────────────────

def run_mutation_testing(source_file, function_name, func_start, func_end,
                         build_dir, project_dir, test_target, max_mutants=50):
    """对单个函数运行变异测试"""
    print("\n  变异测试: {} (L{}-L{})".format(function_name, func_start + 1, func_end))

    with open(source_file) as f:
        lines = f.readlines()

    # 生成所有变异体
    all_mutants = []
    all_mutants.extend(generate_aor_mutants(lines, func_start, func_end))
    all_mutants.extend(generate_ror_mutants(lines, func_start, func_end))
    all_mutants.extend(generate_lor_mutants(lines, func_start, func_end))
    all_mutants.extend(generate_crc_mutants(lines, func_start, func_end))
    all_mutants.extend(generate_rvf_mutants(lines, func_start, func_end))

    # 去重
    seen_ids = set()
    unique_mutants = []
    for m in all_mutants:
        if m['id'] not in seen_ids:
            seen_ids.add(m['id'])
            unique_mutants.append(m)

    # 限制数量
    if len(unique_mutants) > max_mutants:
        print("  变异体 {} 个, 截断为 {} 个".format(len(unique_mutants), max_mutants))
        unique_mutants = unique_mutants[:max_mutants]
    else:
        print("  变异体: {} 个".format(len(unique_mutants)))

    # 按算子统计
    by_operator = defaultdict(int)
    for m in unique_mutants:
        by_operator[m['operator']] += 1
    for op, count in sorted(by_operator.items()):
        print("    {}: {} 个".format(op, count))

    # 逐个测试
    results = []
    killed = 0
    survived = 0
    compile_failed = 0

    for i, mutant in enumerate(unique_mutants):
        # 应用变异
        mutated_lines = apply_mutation(lines, mutant, func_start, func_end)
        if mutated_lines is None:
            continue

        status, output = compile_and_test(
            source_file, mutated_lines, build_dir,
            project_dir, test_target
        )

        results.append({
            'id': mutant['id'],
            'operator': mutant['operator'],
            'line': mutant['line'],
            'description': mutant['description'],
            'status': status,
            'output_snippet': output[:200] if status != 'survived' else '',
        })

        if status == 'killed':
            killed += 1
            marker = 'KILLED'
        elif status == 'survived':
            survived += 1
            marker = 'SURVIVED'
        else:
            compile_failed += 1
            marker = 'COMPILE_FAIL'

        if (i + 1) % 10 == 0 or i == len(unique_mutants) - 1:
            print("  [{}/{}] {} — {}".format(
                i + 1, len(unique_mutants), marker, mutant['description']))

    # 计算得分
    total_valid = killed + survived
    score = round(killed / total_valid * 100, 1) if total_valid > 0 else 0

    print("\n  结果: killed={}, survived={}, compile_failed={}".format(
        killed, survived, compile_failed))
    print("  变异得分: {}/{} = {:.1f}%".format(killed, total_valid, score))

    return {
        'function': function_name,
        'file': source_file,
        'line_range': [func_start + 1, func_end],
        'total_mutants': len(unique_mutants),
        'killed': killed,
        'survived': survived,
        'compile_failed': compile_failed,
        'mutation_score': score,
        'details': results,
    }


def generate_report(results, output_path):
    """生成变异测试报告"""
    lines = []
    lines.append("# 变异测试报告 (Stage 6)")
    lines.append("")
    lines.append("## 概述")
    lines.append("")

    total_killed = sum(r['killed'] for r in results)
    total_survived = sum(r['survived'] for r in results)
    total_valid = total_killed + total_survived
    overall_score = round(total_killed / total_valid * 100, 1) if total_valid > 0 else 0

    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append("| 测试函数 | {} |".format(len(results)))
    lines.append("| 变异体总数 | {} |".format(sum(r['total_mutants'] for r in results)))
    lines.append("| 编译成功 | {} |".format(total_killed + total_survived))
    lines.append("| 编译失败 | {} |".format(sum(r['compile_failed'] for r in results)))
    lines.append("| 杀死 (Killed) | {} |".format(total_killed))
    lines.append("| 存活 (Survived) | {} |".format(total_survived))
    lines.append("| **变异得分** | **{:.1f}%** |".format(overall_score))
    lines.append("")

    lines.append("## 按函数详情")
    lines.append("")
    lines.append("| 函数 | 变异体 | 杀死 | 存活 | 得分 |")
    lines.append("|------|--------|------|------|------|")
    for r in results:
        lines.append("| {} | {} | {} | {} | {:.1f}% |".format(
            r['function'], r['total_mutants'],
            r['killed'], r['survived'], r['mutation_score']))
    lines.append("")

    # 存活变异体详情
    survived_details = []
    for r in results:
        for d in r['details']:
            if d['status'] == 'survived':
                survived_details.append({
                    'function': r['function'],
                    **d
                })

    if survived_details:
        lines.append("## 存活变异体 (测试缺口)")
        lines.append("")
        lines.append("| 函数 | 算子 | 行 | 变异描述 |")
        lines.append("|------|------|----|---------|")
        for d in survived_details:
            lines.append("| {} | {} | L{} | {} |".format(
                d['function'], d['operator'], d['line'], d['description']))
        lines.append("")
        lines.append("**建议**: 对存活的变异体补充测试用例, 使测试能检测到这些变异。")
        lines.append("")

    # 按算子统计
    lines.append("## 按算子统计")
    lines.append("")
    by_op = defaultdict(lambda: {'killed': 0, 'survived': 0, 'compile_failed': 0})
    for r in results:
        for d in r['details']:
            by_op[d['operator']][d['status']] += 1

    lines.append("| 算子 | 杀死 | 存活 | 编译失败 | 杀死率 |")
    lines.append("|------|------|------|---------|--------|")
    for op in sorted(by_op.keys()):
        stats = by_op[op]
        total = stats['killed'] + stats['survived']
        rate = '{:.1f}%'.format(stats['killed'] / total * 100) if total > 0 else 'N/A'
        lines.append("| {} | {} | {} | {} | {} |".format(
            op, stats['killed'], stats['survived'],
            stats['compile_failed'], rate))
    lines.append("")

    lines.append("## 参考")
    lines.append("")
    lines.append("- Lipton, R. (1978). Mutation Testing.")
    lines.append("- Offutt, A. J. & Untch, R. H. (2001). Mutation Testing in the Twentieth Century.")
    lines.append("- 变异得分 = 杀死数 / (杀死 + 存活), 目标 >= 80%")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Stage 6: 变异测试')
    parser.add_argument('--state', required=True, help='state.json 路径')
    parser.add_argument('--function', default=None,
                        help='指定函数 (ClassName::methodName)')
    parser.add_argument('--all-p0', action='store_true',
                        help='对所有 P0 函数运行变异测试')
    parser.add_argument('--max-mutants', type=int, default=50,
                        help='每函数最大变异体数 (默认 50)')
    parser.add_argument('--build-dir', default=None,
                        help='构建目录 (需已编译)')
    args = parser.parse_args()

    with open(args.state) as f:
        state = json.load(f)

    project_dir = state['project_dir']
    build_dir = args.build_dir or os.path.join(project_dir, 'build_tests')

    # 检查 build 目录存在
    if not os.path.isdir(build_dir):
        print("[Stage 6] 错误: 构建目录不存在: {}".format(build_dir))
        print("  请先运行 validate_coverage.py")
        sys.exit(1)

    # 加载优先级报告
    risk_state = state.get('stage', {}).get('risk', {})
    priority_path = risk_state.get('report',
                                   os.path.join(project_dir, 'priority_report.json'))
    with open(priority_path) as f:
        priority_data = json.load(f)

    # 选择目标函数
    target_functions = []
    if args.function:
        for func in priority_data['functions']:
            if func['qualified_name'] == args.function:
                target_functions.append(func)
        if not target_functions:
            print("[Stage 6] 错误: 函数未找到: {}".format(args.function))
            sys.exit(1)
    elif args.all_p0:
        target_functions = [f for f in priority_data['functions']
                            if f.get('priority') == 'P0']
    else:
        # 默认: 第一个 P0 函数
        p0_funcs = [f for f in priority_data['functions']
                    if f.get('priority') == 'P0']
        if p0_funcs:
            target_functions = [p0_funcs[0]]
            print("[Stage 6] 默认测试第一个 P0 函数: {}".format(
                p0_funcs[0]['qualified_name']))
            print("  使用 --all-p0 测试全部 P0 函数")
        else:
            print("[Stage 6] 无 P0 函数")
            sys.exit(0)

    if not target_functions:
        print("[Stage 6] 无目标函数")
        sys.exit(0)

    # 查找测试目标名
    gen_state = state.get('stage', {}).get('generation', {})
    test_targets = gen_state.get('test_targets', ['test_calculator'])
    test_target = test_targets[0] if test_targets else 'test_calculator'

    print("[Stage 6] 变异测试")
    print("  目标函数: {} 个".format(len(target_functions)))
    print("  构建目录: {}".format(build_dir))
    print("  测试目标: {}".format(test_target))
    print("  最大变异体/函数: {}".format(args.max_mutants))

    all_results = []

    for func in target_functions:
        source_file = func.get('file', '')
        func_name = func.get('qualified_name', func.get('name', ''))

        if not source_file or not os.path.exists(source_file):
            print("  跳过: 源文件不存在: {}".format(source_file))
            continue

        # 读取源码, 找到函数范围
        with open(source_file) as f:
            lines = f.readlines()

        func_start, func_end = find_function_range(lines, func_name)

        if func_start < 0 or func_end < 0:
            print("  跳过: 未找到函数 {} 在 {}".format(func_name, source_file))
            continue

        # 跳过私有方法
        if func.get('access') == 'private':
            print("  跳过: {} 是私有方法".format(func_name))
            continue

        result = run_mutation_testing(
            source_file, func_name, func_start, func_end,
            build_dir, project_dir, test_target, args.max_mutants
        )
        all_results.append(result)

    if not all_results:
        print("\n[Stage 6] 无有效结果")
        sys.exit(0)

    # 生成报告
    report_path = os.path.join(build_dir, 'mutation_report.md')
    generate_report(all_results, report_path)

    # JSON 输出
    json_path = os.path.join(build_dir, 'mutation_report.json')
    with open(json_path, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # 总结
    total_killed = sum(r['killed'] for r in all_results)
    total_survived = sum(r['survived'] for r in all_results)
    total_valid = total_killed + total_survived
    overall_score = round(total_killed / total_valid * 100, 1) if total_valid > 0 else 0

    print("\n[Stage 6] 变异测试完成")
    print("  变异体: {} 个".format(sum(r['total_mutants'] for r in all_results)))
    print("  杀死: {}, 存活: {}".format(total_killed, total_survived))
    print("  变异得分: {:.1f}%".format(overall_score))
    print("  报告: {}".format(report_path))
    print("  JSON: {}".format(json_path))

    # 更新 state
    state['stage']['mutation'] = {
        'completed': True,
        'functions_tested': len(all_results),
        'total_mutants': sum(r['total_mutants'] for r in all_results),
        'killed': total_killed,
        'survived': total_survived,
        'mutation_score': overall_score,
        'report': report_path,
        'json': json_path,
    }

    with open(args.state, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
