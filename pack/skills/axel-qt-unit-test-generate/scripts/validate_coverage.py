#!/usr/bin/env python3
"""
validate_coverage.py — Stage 5: 构建验证与有效性度量

用法:
    python3 validate_coverage.py --state state.json [--build-dir build/]

功能:
    1. cmake 配置 + make 编译 (捕获编译错误)
    2. ctest 运行测试 (解析 ctest 输出 + 运行测试二进制获取子测试数)
    3. gcov + lcov 覆盖率分析 (被测库的覆盖率)
    4. 分级覆盖率检查 (P0>=90%, P1>=80%)
    5. 生成验证报告
"""

import argparse
import json
import os
import re
import sys
import subprocess
import shutil
from collections import defaultdict


def run_command(cmd, cwd=None, env=None, timeout=300):
    """运行命令，返回 (success, stdout, stderr)"""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=cwd, env=full_env, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, '', 'Timeout after {}s'.format(timeout)
    except Exception as e:
        return False, '', str(e)


def step1_configure(build_dir, project_dir, enable_coverage=True):
    """cmake 配置"""
    cmake_args = ['cmake', project_dir, '-DBUILD_TESTING=ON']
    if enable_coverage:
        cmake_args.append('-DENABLE_COVERAGE=ON')

    print("  cmake {}...".format(' '.join(cmake_args[1:])))
    ok, stdout, stderr = run_command(cmake_args, cwd=build_dir, timeout=120)
    if not ok:
        print("  cmake 配置失败:")
        print(stdout[-2000:])
        print(stderr)
    return ok


def step2_compile(build_dir):
    """make 编译"""
    print("  make -j{}...".format(os.cpu_count() or 4))
    ok, stdout, stderr = run_command(
        ['make', '-j{}'.format(os.cpu_count() or 4)],
        cwd=build_dir, timeout=300
    )
    if not ok:
        print("  编译失败:")
        lines = stdout.split('\n') + stderr.split('\n')
        error_lines = [l for l in lines if 'error:' in l or 'Error' in l]
        if error_lines:
            for line in error_lines[-20:]:
                print("    " + line)
        else:
            print(stderr[-2000:])
    return ok, stdout, stderr


def step3_run_tests(build_dir):
    """ctest 运行测试 + 直接运行测试二进制获取子测试数"""
    env = {'QT_QPA_PLATFORM': 'offscreen'}
    print("  ctest --output-on-failure...")
    ok, stdout, stderr = run_command(
        ['ctest', '--output-on-failure'],
        cwd=build_dir, env=env, timeout=300
    )

    # ── 解析 ctest 输出 ──
    # 格式: "100% tests passed, 0 tests failed out of 1"
    # 或: "Total Tests: N, Passed: N, Failed: N"
    total = 0
    passed = 0
    failed = 0

    # 方式1: "N% tests passed, M tests failed out of T"
    m = re.search(r'(\d+)% tests passed,\s*(\d+) tests? failed out of (\d+)', stdout)
    if m:
        total = int(m.group(3))
        passed = total - int(m.group(2))
        failed = int(m.group(2))
    else:
        # 方式2: "Total Tests: N, Passed: N, Failed: N"
        m = re.search(r'Total Tests?:\s*(\d+)[,.]\s*Passed:\s*(\d+)[,.]\s*Failed:\s*(\d+)', stdout)
        if m:
            total = int(m.group(1))
            passed = int(m.group(2))
            failed = int(m.group(3))

    # 方式3: 逐行解析 "  Test #N: name ... Passed/Failed"
    if total == 0:
        for line in stdout.split('\n'):
            line = line.strip()
            if re.match(r'\d+/\d+ Test #\d+:', line):
                total += 1
                if 'Passed' in line:
                    passed += 1
                elif 'Failed' in line:
                    failed += 1

    # ── 直接运行测试二进制，获取子测试数 ──
    sub_tests = 0
    sub_passed = 0
    sub_failed = 0
    test_details = []

    # 查找所有测试可执行文件
    test_executables = []
    for root, dirs, files in os.walk(build_dir):
        for f in files:
            filepath = os.path.join(root, f)
            if f.startswith('test_') and os.access(filepath, os.X_OK):
                # 确认是 ELF 可执行文件
                try:
                    with open(filepath, 'rb') as fh:
                        if fh.read(4) == b'\x7fELF':
                            test_executables.append(filepath)
                except Exception:
                    pass

    for test_exe in sorted(test_executables):
        test_name = os.path.basename(test_exe)
        print("  运行 {}...".format(test_name))
        tok, tstdout, tstderr = run_command(
            [test_exe], cwd=build_dir, env=env, timeout=60
        )

        # 解析 Qt Test 输出
        # 格式: "PASS   : TestClass::testFunction()"
        # 或: "FAIL! : TestClass::testFunction() ..."
        # 最后一行: "Totals: X passed, Y failed, Z skipped, ..."
        for line in tstdout.split('\n'):
            line = line.strip()
            if line.startswith('PASS'):
                sub_tests += 1
                sub_passed += 1
                m = re.match(r'PASS\s*:\s*(\S+)::(\w+)\(\)', line)
                if m:
                    test_details.append({
                        'test': m.group(1),
                        'function': m.group(2),
                        'result': 'PASS'
                    })
            elif line.startswith('FAIL'):
                sub_tests += 1
                sub_failed += 1
                m = re.match(r'FAIL!?\s*:\s*(\S+)::(\w+)\(\)', line)
                if m:
                    test_details.append({
                        'test': m.group(1),
                        'function': m.group(2),
                        'result': 'FAIL'
                    })

        # 解析 Totals 行
        totals_match = re.search(
            r'Totals:\s*(\d+) passed,\s*(\d+) failed,\s*(\d+) skipped', tstdout)
        if totals_match:
            sub_passed = int(totals_match.group(1))
            sub_failed = int(totals_match.group(2))
            sub_tests = sub_passed + sub_failed + int(totals_match.group(3))

    print("  ctest: {}/{} 测试模块通过".format(passed, max(total, 1)))
    print("  子测试: {} passed, {} failed (共 {})".format(
        sub_passed, sub_failed, sub_tests))

    return ok, passed, failed, total, stdout, stderr, sub_tests, sub_passed, sub_failed, test_details


def step4_coverage(build_dir, project_dir):
    """gcov + lcov 覆盖率分析 (被测库的覆盖率)"""
    print("  lcov --capture...")

    # lcov 捕获 (不加 --no-external, 保留外部文件再过滤)
    coverage_file = os.path.join(build_dir, 'coverage.info')
    ok, stdout, stderr = run_command(
        ['lcov', '--capture', '--directory', build_dir,
         '--output-file', coverage_file],
        cwd=build_dir, timeout=120
    )
    if not ok:
        print("  lcov 捕获失败: {}".format(stderr[:500]))
        return None

    # 过滤: 移除系统文件、测试文件自身、moc 生成文件
    # 保留被测库源码 (src/)
    filtered_file = os.path.join(build_dir, 'coverage.filtered.info')
    ok2, _, _ = run_command(
        ['lcov', '--remove', coverage_file,
         '/usr/*',
         '*/tests/*',
         '*/moc_*',
         '*/autogen/*',
         '*/mocs_compilation*',
         '--output-file', filtered_file],
        cwd=build_dir, timeout=60
    )

    # 检查过滤后是否有数据
    if not os.path.exists(filtered_file) or os.path.getsize(filtered_file) == 0:
        print("  覆盖率数据为空 (测试可能只含 placeholder 断言)")
        return None

    # 检查是否有有效记录
    has_data = False
    with open(filtered_file) as f:
        for line in f:
            if line.startswith('SF:') and '/src/' in line:
                has_data = True
                break

    if not has_data:
        print("  被测库源码无覆盖率数据 (测试可能只含 placeholder 断言)")
        # 仍然解析原始文件 (含测试文件的覆盖率)
        coverage_data = parse_lcov(coverage_file)
        if coverage_data and coverage_data['summary']['lines_total'] > 0:
            print("  (测试文件自身覆盖率: 行 {:.1%})".format(
                coverage_data['summary']['line_rate']))
        return coverage_data

    coverage_data = parse_lcov(filtered_file)
    return coverage_data


def parse_lcov(lcov_file):
    """解析 lcov 信息文件"""
    coverage = {
        'files': {},
        'summary': {'lines_total': 0, 'lines_hit': 0,
                    'branches_total': 0, 'branches_hit': 0,
                    'functions_total': 0, 'functions_hit': 0}
    }

    if not os.path.exists(lcov_file):
        return coverage

    current_file = None
    with open(lcov_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('SF:'):
                current_file = line[3:]
                coverage['files'][current_file] = {
                    'lines': {},
                    'branches': {},
                    'functions': {},
                    'line_rate': 0,
                    'branch_rate': 0,
                }
            elif line.startswith('FN:'):
                parts = line[3:].split(',')
                if len(parts) >= 2 and current_file:
                    func_line = int(parts[0])
                    func_name = parts[1]
                    coverage['files'][current_file]['functions'][func_name] = {
                        'line': func_line, 'hit': 0
                    }
            elif line.startswith('FNDA:'):
                parts = line[5:].split(',')
                if len(parts) >= 2 and current_file:
                    hits = int(parts[0])
                    func_name = parts[1]
                    if func_name in coverage['files'][current_file]['functions']:
                        coverage['files'][current_file]['functions'][func_name]['hit'] = hits
            elif line.startswith('DA:'):
                parts = line[3:].split(',')
                if len(parts) >= 2 and current_file:
                    line_num = int(parts[0])
                    hits = int(parts[1])
                    coverage['files'][current_file]['lines'][line_num] = hits
            elif line.startswith('BRDA:'):
                parts = line[5:].split(',')
                if len(parts) >= 3 and current_file:
                    line_num = int(parts[0])
                    taken = parts[2]
                    hit = 0 if taken == '-' or taken == '0' else int(taken)
                    coverage['files'][current_file]['branches'].setdefault(line_num, []).append(hit)
            elif line == 'end of record':
                current_file = None

    # 计算比率
    total_lines = 0
    hit_lines = 0
    total_branches = 0
    hit_branches = 0
    total_funcs = 0
    hit_funcs = 0

    for filepath, data in coverage['files'].items():
        lines = data['lines']
        total_l = len(lines)
        hit_l = sum(1 for v in lines.values() if v > 0)
        data['line_rate'] = round(hit_l / total_l, 4) if total_l > 0 else 0
        total_lines += total_l
        hit_lines += hit_l

        branches = data['branches']
        total_b = sum(len(v) for v in branches.values())
        hit_b = sum(sum(1 for x in v if x > 0) for v in branches.values())
        data['branch_rate'] = round(hit_b / total_b, 4) if total_b > 0 else 0
        total_branches += total_b
        hit_branches += hit_b

        funcs = data['functions']
        total_f = len(funcs)
        hit_f = sum(1 for fdata in funcs.values() if fdata['hit'] > 0)
        data['function_rate'] = round(hit_f / total_f, 4) if total_f > 0 else 0
        total_funcs += total_f
        hit_funcs += hit_f

    coverage['summary'] = {
        'lines_total': total_lines,
        'lines_hit': hit_lines,
        'line_rate': round(hit_lines / total_lines, 4) if total_lines > 0 else 0,
        'branches_total': total_branches,
        'branches_hit': hit_branches,
        'branch_rate': round(hit_branches / total_branches, 4) if total_branches > 0 else 0,
        'functions_total': total_funcs,
        'functions_hit': hit_funcs,
        'function_rate': round(hit_funcs / total_funcs, 4) if total_funcs > 0 else 0,
    }
    return coverage


def check_priority_coverage(coverage_data, priority_data, project_dir):
    """分级覆盖率检查"""
    results = {
        'P0': {'required_branch': 0.90, 'actual_branch': 0, 'pass': False, 'functions': []},
        'P1': {'required_branch': 0.80, 'actual_branch': 0, 'pass': False, 'functions': []},
        'P2': {'required_branch': 0.0, 'actual_branch': 0, 'pass': True, 'functions': []},
        'P3': {'required_branch': 0.0, 'actual_branch': 0, 'pass': True, 'functions': []},
    }

    if not coverage_data or not coverage_data.get('files'):
        return results

    for func in priority_data.get('functions', []):
        priority = func.get('priority', 'P3')
        func_file = func.get('file', '')
        func_name = func.get('name', '')
        func_line = func.get('line', 0)

        if not func_file:
            continue

        # 匹配覆盖率数据中的文件
        matched_file = None
        for cov_file in coverage_data['files']:
            if os.path.abspath(cov_file) == os.path.abspath(func_file):
                matched_file = cov_file
                break

        if not matched_file:
            continue

        file_cov = coverage_data['files'][matched_file]
        file_branch_rate = file_cov.get('branch_rate', 0)
        file_line_rate = file_cov.get('line_rate', 0)

        results[priority]['functions'].append({
            'name': func.get('qualified_name', func_name),
            'file': os.path.relpath(func_file, project_dir),
            'branch_rate': file_branch_rate,
            'line_rate': file_line_rate,
        })

    # 计算每个优先级的平均分支覆盖率
    for p in ['P0', 'P1']:
        funcs = results[p]['functions']
        if funcs:
            avg = sum(f['branch_rate'] for f in funcs) / len(funcs)
            results[p]['actual_branch'] = round(avg, 4)
            results[p]['pass'] = avg >= results[p]['required_branch']

    return results


def generate_validation_report(build_ok, test_ok, test_results, coverage_data,
                               priority_coverage, state):
    """生成验证报告"""
    lines = []
    lines.append("# 验证报告 (Stage 5)")
    lines.append("")

    # 构建结果
    lines.append("## 构建结果")
    lines.append("")
    lines.append("- cmake 配置: {}".format("通过" if build_ok else "失败"))
    lines.append("- 编译: {}".format("通过" if build_ok else "失败"))
    lines.append("")

    # 测试结果
    lines.append("## 测试运行")
    lines.append("")
    if test_results:
        _, ctest_passed, ctest_failed, ctest_total, _, _, sub_tests, sub_passed, sub_failed, details = test_results
        lines.append("- ctest 模块: {}/{} 通过".format(ctest_passed, max(ctest_total, 1)))
        lines.append("- 子测试: {} passed, {} failed (共 {})".format(
            sub_passed, sub_failed, sub_tests))
        if ctest_failed == 0 and sub_failed == 0:
            lines.append("- 状态: 全部通过")
        else:
            lines.append("- 状态: 有失败")

        # 失败详情
        failed_details = [d for d in details if d['result'] == 'FAIL']
        if failed_details:
            lines.append("")
            lines.append("### 失败的子测试")
            lines.append("")
            for d in failed_details:
                lines.append("- {}::{}".format(d['test'], d['function']))
    else:
        lines.append("- 未运行 (编译失败)")
    lines.append("")

    # 覆盖率
    if coverage_data and coverage_data.get('summary', {}).get('lines_total', 0) > 0:
        summary = coverage_data['summary']
        lines.append("## 覆盖率")
        lines.append("")
        lines.append("| 指标 | 总数 | 命中 | 比率 |")
        lines.append("|------|------|------|------|")
        lines.append("| 行覆盖 | {} | {} | {:.1%} |".format(
            summary['lines_total'], summary['lines_hit'], summary['line_rate']))
        lines.append("| 分支覆盖 | {} | {} | {:.1%} |".format(
            summary['branches_total'], summary['branches_hit'], summary['branch_rate']))
        lines.append("| 函数覆盖 | {} | {} | {:.1%} |".format(
            summary['functions_total'], summary['functions_hit'], summary['function_rate']))
        lines.append("")

        # 按文件覆盖率
        lines.append("### 按文件覆盖率")
        lines.append("")
        lines.append("| 文件 | 行覆盖 | 分支覆盖 | 函数覆盖 |")
        lines.append("|------|--------|---------|---------|")
        for filepath, data in sorted(coverage_data['files'].items()):
            rel = os.path.relpath(filepath, state['project_dir']) if filepath.startswith('/') else filepath
            lines.append("| {} | {:.1%} | {:.1%} | {:.1%} |".format(
                rel, data.get('line_rate', 0),
                data.get('branch_rate', 0),
                data.get('function_rate', 0)))
        lines.append("")
    else:
        lines.append("## 覆盖率")
        lines.append("")
        lines.append("- 无覆盖率数据 (测试可能只含 placeholder 断言，需补充真实断言)")
        lines.append("")

    # 分级覆盖率检查
    if priority_coverage:
        lines.append("## 分级覆盖率检查")
        lines.append("")
        lines.append("| 优先级 | 要求分支覆盖 | 实际 | 状态 |")
        lines.append("|--------|-------------|------|------|")
        for p in ['P0', 'P1', 'P2', 'P3']:
            pc = priority_coverage.get(p, {})
            required = pc.get('required_branch', 0)
            actual = pc.get('actual_branch', 0)
            status = "通过" if pc.get('pass', True) else "未达标"
            lines.append("| {} | {:.0%} | {:.1%} | {} |".format(
                p, required, actual, status))
        lines.append("")

    lines.append("## 建议")
    lines.append("")
    if not build_ok:
        lines.append("- 修复编译错误后再运行验证")
    if test_results and test_results[8] > 0:
        lines.append("- 修复失败的子测试用例")
    if coverage_data is None or coverage_data.get('summary', {}).get('lines_total', 0) == 0:
        lines.append("- 当前测试只含 placeholder (QVERIFY(true))，需补充真实断言")
        lines.append("- 补充断言后覆盖率数据才会有意义")
    if priority_coverage:
        if not priority_coverage['P0']['pass']:
            lines.append("- P0 函数分支覆盖未达 90%，需补充 Level 2 测试")
        if not priority_coverage['P1']['pass']:
            lines.append("- P1 函数分支覆盖未达 80%，需补充 Level 2 测试")
    lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Stage 5: 构建验证与有效性度量')
    parser.add_argument('--state', required=True, help='state.json 路径')
    parser.add_argument('--build-dir', default=None, help='构建目录')
    parser.add_argument('--no-coverage', action='store_true', help='跳过覆盖率分析')
    args = parser.parse_args()

    with open(args.state) as f:
        state = json.load(f)

    project_dir = state['project_dir']
    build_dir = args.build_dir or os.path.join(project_dir, 'build_tests')
    os.makedirs(build_dir, exist_ok=True)

    print("[Stage 5] 构建验证")

    # Step 1: cmake 配置
    print("\n[1/4] cmake 配置...")
    configure_ok = step1_configure(build_dir, project_dir, enable_coverage=not args.no_coverage)
    if not configure_ok:
        print("  重试 (不带 coverage)...")
        configure_ok = step1_configure(build_dir, project_dir, enable_coverage=False)
    if not configure_ok:
        print("\n[Stage 5] cmake 配置失败, 终止", file=sys.stderr)
        sys.exit(1)

    # Step 2: 编译
    print("\n[2/4] 编译...")
    compile_ok, compile_stdout, compile_stderr = step2_compile(build_dir)

    # Step 3: 运行测试
    test_results = None
    if compile_ok:
        print("\n[3/4] 运行测试...")
        results = step3_run_tests(build_dir)
        test_results = results
        test_ok = results[0]
    else:
        print("\n[3/4] 跳过测试 (编译失败)")
        test_ok = False

    # Step 4: 覆盖率
    coverage_data = None
    if compile_ok and test_ok and not args.no_coverage:
        print("\n[4/4] 覆盖率分析...")
        coverage_data = step4_coverage(build_dir, project_dir)
        if coverage_data and coverage_data['summary']['lines_total'] > 0:
            s = coverage_data['summary']
            print("  行覆盖: {}/{} ({:.1%})".format(
                s['lines_hit'], s['lines_total'], s['line_rate']))
            print("  分支覆盖: {}/{} ({:.1%})".format(
                s['branches_hit'], s['branches_total'], s['branch_rate']))
        else:
            print("  无有效覆盖率数据")
    else:
        print("\n[4/4] 跳过覆盖率分析")

    # 分级覆盖率检查
    priority_coverage = None
    if coverage_data:
        risk_state = state.get('stage', {}).get('risk', {})
        priority_path = risk_state.get('report', os.path.join(project_dir, 'priority_report.json'))
        if os.path.exists(priority_path):
            with open(priority_path) as f:
                priority_data = json.load(f)
            priority_coverage = check_priority_coverage(
                coverage_data, priority_data, project_dir)

    # 生成验证报告
    report = generate_validation_report(
        compile_ok, test_ok, test_results, coverage_data,
        priority_coverage, state)

    report_path = os.path.join(build_dir, 'validation_report.md')
    with open(report_path, 'w') as f:
        f.write(report)

    # JSON 格式结果
    sub_tests = test_results[6] if test_results else 0
    sub_passed = test_results[7] if test_results else 0
    sub_failed = test_results[8] if test_results else 0

    validation_json = {
        'build_ok': compile_ok,
        'test_ok': test_ok if test_results else False,
        'ctest_passed': test_results[1] if test_results else 0,
        'ctest_failed': test_results[2] if test_results else 0,
        'ctest_total': test_results[3] if test_results else 0,
        'sub_tests': sub_tests,
        'sub_passed': sub_passed,
        'sub_failed': sub_failed,
        'coverage': coverage_data['summary'] if coverage_data else None,
        'priority_coverage': priority_coverage,
        'report_path': report_path,
    }

    json_path = os.path.join(build_dir, 'validation_report.json')
    with open(json_path, 'w') as f:
        json.dump(validation_json, f, indent=2, ensure_ascii=False)

    print("\n[Stage 5] 输出:")
    print("  报告: {}".format(report_path))
    print("  JSON: {}".format(json_path))

    # 更新 state
    state['stage']['validation'] = {
        'completed': True,
        'build_ok': compile_ok,
        'test_ok': test_ok if test_results else False,
        'ctest_passed': test_results[1] if test_results else 0,
        'ctest_total': test_results[3] if test_results else 0,
        'sub_tests': sub_tests,
        'sub_passed': sub_passed,
        'sub_failed': sub_failed,
        'report': report_path,
        'json': json_path,
    }

    with open(args.state, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print("\n[Stage 5] 完成, state.json 已更新")

    if not compile_ok or (test_results and test_results[8] > 0):
        sys.exit(1)


if __name__ == '__main__':
    main()
