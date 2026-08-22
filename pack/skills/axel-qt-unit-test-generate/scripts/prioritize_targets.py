#!/usr/bin/env python3
"""
prioritize_targets.py — Stage 2: 风险分析与优先级排序

用法:
    python3 prioritize_targets.py --state state.json

输入: state.json (Stage 1 产出: call_graph.json, complexity_report.json)
输出: priority_report.json, priority_report.md
"""

import argparse
import json
import os
import sys
import subprocess
from collections import defaultdict

try:
    import networkx as nx
    from networkx.readwrite import json_graph
except ImportError:
    print("ERROR: networkx 未安装, 请运行 pip install networkx", file=sys.stderr)
    sys.exit(1)


# ── 安全敏感关键词 (函数名/文件名匹配) ─────────────────────

SECURITY_KEYWORDS = [
    'auth', 'login', 'password', 'passwd', 'encrypt', 'decrypt',
    'parse', 'validate', 'check', 'verify', 'sanitize', 'escape',
    'permission', 'privilege', 'token', 'credential', 'hash',
    'sql', 'inject', 'xss', 'csrf',
]


def is_security_sensitive(func_info):
    """检测函数是否安全敏感"""
    text = (func_info.get('name', '') + ' ' + func_info.get('file', '')).lower()
    return any(kw in text for kw in SECURITY_KEYWORDS)


# ── 变更频率分析 (git log) ───────────────────────────────────

def get_change_rates(project_dir, func_map):
    """从 git log 获取每个函数所在文件的提交次数"""
    file_commits = {}

    # 获取所有源文件的提交次数
    all_files = set()
    for func in func_map.values():
        all_files.add(func.get('file', ''))

    for filepath in all_files:
        if not filepath or not os.path.exists(filepath):
            file_commits[filepath] = 0
            continue
        try:
            rel_path = os.path.relpath(filepath, project_dir)
            result = subprocess.run(
                ['git', 'log', '--oneline', '--', rel_path],
                capture_output=True, text=True, cwd=project_dir, timeout=10
            )
            file_commits[filepath] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except Exception:
            file_commits[filepath] = 0

    return file_commits


# ── 风险评分 ──────────────────────────────────────────────────

def calculate_risk_scores(G, func_map, complexity_map, state):
    """计算每个函数的风险评分"""
    weights = state.get('risk_weights', {
        'complexity': 0.30,
        'centrality': 0.20,
        'fan_out': 0.15,
        'branch_depth': 0.10,
        'change_rate': 0.15,
        'public_surface': 0.10,
    })

    mode = state.get('mode', 'existing')

    # 新项目无 git 历史，关闭 change_rate 权重
    if mode == 'new':
        weights['change_rate'] = 0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

    # ── 归一化各因子 ──

    max_complexity = max(complexity_map.values()) if complexity_map else 1
    in_degrees = dict(G.in_degree()) if G.number_of_nodes() > 0 else {}
    out_degrees = dict(G.out_degree()) if G.number_of_nodes() > 0 else {}
    max_in_degree = max(in_degrees.values()) if in_degrees else 1
    max_out_degree = max(out_degrees.values()) if out_degrees else 1

    # PageRank
    pagerank = {}
    if G.number_of_nodes() > 0:
        try:
            pagerank = nx.pagerank(G, max_iter=1000)
        except Exception:
            pagerank = {}

    pagerank_top5 = set()
    if pagerank:
        sorted_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        top5_count = max(1, int(len(sorted_pr) * 0.05))
        pagerank_top5 = set(n for n, _ in sorted_pr[:top5_count])

    # 调用链深度 (从入度为 0 的入口点出发的最长路径)
    # 使用 BFS 限制深度, 避免 all_simple_paths 在大图上的指数爆炸
    entry_points = [n for n in G.nodes() if G.in_degree(n) == 0]
    branch_depth = {}
    for node in G.nodes():
        max_depth = 0
        for entry in entry_points:
            if entry == node:
                continue
            try:
                # 用最短路径长度的 BFS 近似替代 all_simple_paths
                # 取所有路径中最长者; 用 cutoff 限制搜索深度
                paths = list(nx.all_simple_paths(G, entry, node, cutoff=20))
                for path in paths:
                    max_depth = max(max_depth, len(path) - 1)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                pass
            except Exception:
                pass
        branch_depth[node] = max_depth

    max_depth = max(branch_depth.values()) if branch_depth else 1

    # 变更频率
    change_rates = {}
    if mode == 'existing':
        file_commits = get_change_rates(state['project_dir'], func_map)
        max_commits = max(file_commits.values()) if file_commits else 1
        for func_id, func in func_map.items():
            filepath = func.get('file', '')
            change_rates[func_id] = file_commits.get(filepath, 0)
    else:
        max_commits = 1

    # ── 计算每个函数的评分 ──

    results = []
    for func_id in G.nodes():
        func = func_map.get(func_id, {})
        complexity = complexity_map.get(func_id, 1)

        # 因子归一化到 [0, 100]
        complexity_score = min(complexity / 20.0, 1.0) * 100
        centrality_score = (in_degrees.get(func_id, 0) / max_in_degree * 100) if max_in_degree > 0 else 0
        fanout_score = (out_degrees.get(func_id, 0) / max_out_degree * 100) if max_out_degree > 0 else 0
        depth_score = (branch_depth.get(func_id, 0) / max_depth * 100) if max_depth > 0 else 0
        change_score = (change_rates.get(func_id, 0) / max_commits * 100) if max_commits > 0 else 0

        # 公共接口权重
        access = func.get('access', 'private')
        is_signal = func.get('is_signal', False)
        is_slot = func.get('is_slot', False)
        if is_signal:
            public_score = 100
        elif access == 'public':
            public_score = 80
        elif access == 'protected':
            public_score = 40
        elif access == 'private':
            public_score = 20
        else:
            public_score = 10

        # 加权评分
        risk_score = (
            weights['complexity'] * complexity_score +
            weights['centrality'] * centrality_score +
            weights['fan_out'] * fanout_score +
            weights['branch_depth'] * depth_score +
            weights['change_rate'] * change_score +
            weights['public_surface'] * public_score
        )

        # 优先级判定
        priority = 'P3'
        if risk_score >= 70:
            priority = 'P0'
        elif risk_score >= 40:
            priority = 'P1'
        elif risk_score >= 20:
            priority = 'P2'

        # 特殊规则
        special_rules = []
        if complexity >= 15:
            priority = max(priority, 'P0', key=lambda p: ['P3', 'P2', 'P1', 'P0'].index(p))
            special_rules.append('complexity >= 15')
        if func_id in pagerank_top5 and risk_score < 40:
            priority = max(priority, 'P1', key=lambda p: ['P3', 'P2', 'P1', 'P0'].index(p))
            special_rules.append('pagerank top 5%')
        if is_security_sensitive(func):
            priority = max(priority, 'P0', key=lambda p: ['P3', 'P2', 'P1', 'P0'].index(p))
            special_rules.append('security sensitive')

        results.append({
            'id': func_id,
            'name': func.get('name', func_id),
            'qualified_name': func.get('name', func_id),
            'class': func.get('class'),
            'file': func.get('file', ''),
            'line': func.get('line', 0),
            'risk_score': round(risk_score, 2),
            'priority': priority,
            'factors': {
                'complexity': round(complexity_score, 2),
                'centrality': round(centrality_score, 2),
                'fan_out': round(fanout_score, 2),
                'branch_depth': round(depth_score, 2),
                'change_rate': round(change_score, 2),
                'public_surface': round(public_score, 2),
            },
            'complexity': complexity,
            'in_degree': in_degrees.get(func_id, 0),
            'out_degree': out_degrees.get(func_id, 0),
            'branch_depth': branch_depth.get(func_id, 0),
            'pagerank': round(pagerank.get(func_id, 0), 6),
            'special_rules': special_rules,
            'access': access,
        })

    # 排序 (风险评分降序)
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    return results


def generate_markdown_report(results, G, state):
    """生成人可读的风险分析报告"""
    lines = []
    lines.append("# 风险分析报告 (Stage 2)")
    lines.append("")
    lines.append("## 优先级分布")
    lines.append("")

    priority_counts = defaultdict(int)
    for r in results:
        priority_counts[r['priority']] += 1

    lines.append("| 优先级 | 数量 | 测试要求 | 覆盖目标 |")
    lines.append("|--------|------|---------|---------|")
    for p in ['P0', 'P1', 'P2', 'P3']:
        count = priority_counts.get(p, 0)
        if p == 'P0':
            req = "Level 4 (含变异测试)"
            cov = "分支>=90%, 变异>=80%"
        elif p == 'P1':
            req = "Level 2 (结构测试)"
            cov = "分支>=90%, 条件>=80%"
        elif p == 'P2':
            req = "Level 1 (规范测试)"
            cov = "分支覆盖+边界"
        else:
            req = "Level 0 (Smoke)"
            cov = "语句覆盖"
        lines.append("| {} | {} | {} | {} |".format(p, count, req, cov))

    lines.append("")
    lines.append("## Top 10 高风险函数")
    lines.append("")
    lines.append("| 排名 | 函数 | 风险分 | 优先级 | 复杂度 | 入度 | 出度 | 文件 |")
    lines.append("|------|------|--------|--------|--------|------|------|------|")
    for i, r in enumerate(results[:10]):
        rel_file = os.path.relpath(r['file'], state['project_dir']) if r['file'] else ''
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            i + 1, r['qualified_name'][:40], r['risk_score'], r['priority'],
            r['complexity'], r['in_degree'], r['out_degree'], rel_file))

    # 特殊规则触发
    special = [r for r in results if r['special_rules']]
    if special:
        lines.append("")
        lines.append("## 特殊规则触发")
        lines.append("")
        lines.append("| 函数 | 规则 | 优先级 |")
        lines.append("|------|------|--------|")
        for r in special:
            lines.append("| {} | {} | {} |".format(
                r['qualified_name'][:40], ', '.join(r['special_rules']), r['priority']))

    # 循环依赖
    if G.number_of_nodes() > 0:
        sccs = list(nx.strongly_connected_components(G))
        cyclic_sccs = [scc for scc in sccs if len(scc) > 1]
        if cyclic_sccs:
            lines.append("")
            lines.append("## 循环依赖 (SCC)")
            lines.append("")
            lines.append("发现 {} 个循环依赖集群:".format(len(cyclic_sccs)))
            for i, scc in enumerate(cyclic_sccs):
                lines.append("- SCC {}: {} 个函数".format(i + 1, len(scc)))
                for node_id in list(scc)[:5]:
                    func = next((r for r in results if r['id'] == node_id), None)
                    if func:
                        lines.append("  - {}".format(func['qualified_name']))

    lines.append("")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Stage 2: 风险分析与优先级排序')
    parser.add_argument('--state', required=True, help='state.json 路径')
    parser.add_argument('--output-dir', default=None, help='输出目录')
    args = parser.parse_args()

    with open(args.state) as f:
        state = json.load(f)

    output_dir = args.output_dir or os.path.dirname(os.path.abspath(args.state))

    # 加载调用图谱
    code_graph_state = state.get('stage', {}).get('code_graph', {})
    call_graph_path = code_graph_state.get('call_graph', os.path.join(output_dir, 'call_graph.json'))
    complexity_path = code_graph_state.get('complexity_report',
                                            os.path.join(output_dir, 'complexity_report.json'))

    print("[Stage 2] 加载代码图谱...")
    with open(call_graph_path) as f:
        graph_data = json.load(f)
    with open(complexity_path) as f:
        complexity_data = json.load(f)

    # 构建 networkx 图
    G = json_graph.node_link_graph(graph_data, directed=True)

    # 过滤: 移除 file 为空或不在项目目录中的节点 (Qt 内部函数)
    project_dir = state.get('project_dir', '')
    nodes_to_remove = []
    for node_id in list(G.nodes()):
        node_data = G.nodes[node_id]
        node_file = node_data.get('file', '')
        if not node_file or not os.path.abspath(node_file).startswith(os.path.abspath(project_dir)):
            nodes_to_remove.append(node_id)
    if nodes_to_remove:
        G.remove_nodes_from(nodes_to_remove)
        print("  过滤非项目函数: {} 个".format(len(nodes_to_remove)))

    # 函数映射
    func_map = {}
    for node in graph_data['nodes']:
        func_map[node['id']] = node

    complexity_map = {}
    for func in complexity_data['functions']:
        complexity_map[func['id']] = func['complexity']
        # 补充 func_map 中缺失的函数
        if func['id'] not in func_map:
            func_map[func['id']] = func

    print("  函数/方法: {} 个".format(len(func_map)))
    print("  调用边: {} 条".format(G.number_of_edges()))

    if G.number_of_nodes() == 0:
        print("  WARNING: 图谱为空, 无法做风险分析", file=sys.stderr)

    print("\n[Stage 2] 计算风险评分...")
    results = calculate_risk_scores(G, func_map, complexity_map, state)

    # 优先级统计
    p_counts = defaultdict(int)
    for r in results:
        p_counts[r['priority']] += 1

    print("  P0 (必须测试): {}".format(p_counts['P0']))
    print("  P1 (应该测试): {}".format(p_counts['P1']))
    print("  P2 (建议测试): {}".format(p_counts['P2']))
    print("  P3 (可选测试): {}".format(p_counts['P3']))

    # 输出 JSON
    priority_json = {
        'functions': results,
        'summary': {
            'total': len(results),
            'P0': p_counts['P0'],
            'P1': p_counts['P1'],
            'P2': p_counts['P2'],
            'P3': p_counts['P3'],
        },
    }

    json_path = os.path.join(output_dir, 'priority_report.json')
    with open(json_path, 'w') as f:
        json.dump(priority_json, f, indent=2, ensure_ascii=False)

    # 输出 Markdown
    md_path = os.path.join(output_dir, 'priority_report.md')
    md_content = generate_markdown_report(results, G, state)
    with open(md_path, 'w') as f:
        f.write(md_content)

    print("\n[Stage 2] 输出:")
    print("  JSON: {}".format(json_path))
    print("  Markdown: {}".format(md_path))

    # 更新 state
    state['stage']['risk'] = {
        'completed': True,
        'report': json_path,
        'markdown': md_path,
        'P0_count': p_counts['P0'],
        'P1_count': p_counts['P1'],
        'P2_count': p_counts['P2'],
        'P3_count': p_counts['P3'],
    }

    with open(args.state, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print("\n[Stage 2] 完成, state.json 已更新")


if __name__ == '__main__':
    main()
