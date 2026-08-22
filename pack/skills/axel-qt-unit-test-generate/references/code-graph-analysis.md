# 代码图谱构建与分析方法

## 概述

本文件描述如何用 libclang 构建 AST 级代码图谱，以及用 networkx 做图分析。
这是 Stage 1 和 Stage 2 的技术基础。

## libclang AST 解析

### 初始化

```python
import clang.cindex
clang.cindex.Config.set_library_file('/usr/lib/llvm-13/lib/libclang.so')
index = clang.cindex.Index.create()
```

### 解析源文件

```python
tu = index.parse(filepath, args=[
    '-x', 'c++',
    '--std=c++14',
    '-fPIC',
    '-I/usr/include/x86_64-linux-gnu/qt5',
    '-I/usr/include/x86_64-linux-gnu/qt5/QtCore',
    # ... 更多 -I 路径
])
```

### 提取调用图谱

遍历 AST，对每个 FunctionDecl/CXXMethod 节点，递归查找 CALL_EXPR 子节点:

```python
def extract_calls(cursor):
    """从函数体中提取所有函数调用"""
    calls = []
    for child in cursor.walk_preorder():
        if child.kind == clang.cindex.CursorKind.CALL_EXPR:
            callee = child.referenced
            if callee and callee.kind in (clang.cindex.CursorKind.FUNCTION_DECL,
                                           clang.cindex.CursorKind.CXX_METHOD):
                calls.append({
                    'callee': callee.spelling,
                    'callee_location': f"{callee.location.file.name}:{callee.location.line}"
                                      if callee.location.file else 'unknown',
                    'call_location': f"{cursor.location.file.name}:{child.location.line}"
                })
    return calls
```

### 提取继承图谱

```python
def extract_inheritance(cursor):
    """提取类的继承关系"""
    parents = []
    if cursor.kind in (clang.cindex.CursorKind.CLASS_DECL,
                       clang.cindex.CursorKind.CLASS_TEMPLATE,
                       clang.cindex.CursorKind.STRUCT_DECL):
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
                parents.append(child.spelling)
    return parents
```

### 提取 #include 依赖

```python
def extract_includes(tu):
    """提取预处理指令中的 #include"""
    includes = []
    for child in tu.cursor.get_children():
        if child.kind == clang.cindex.CursorKind.INCLUSION_DIRECTIVE:
            includes.append(child.spelling)  # 文件名
    return includes
```

## 圈复杂度计算

McCabe 圈复杂度 V(G) = 判定节点数 + 1

判定节点 (AST 中增加控制流分支的节点):

| AST 节点 | CursorKind | 分支数 |
|---------|-----------|--------|
| if | IF_STMT | 2 |
| for | FOR_STMT | 2 |
| while | WHILE_STMT | 2 |
| do-while | DO_STMT | 2 |
| switch | SWITCH_STMT | N (case 数) |
| case | CASE_STMT | 1 (计入 switch) |
| catch | CATCH_STMT | 2 |
| && | BINARY_OPERATOR (op=&&) | 2 |
| || | BINARY_OPERATOR (op=||) | 2 |
| ?: | CONDITIONAL_OPERATOR | 2 |

```python
DECISION_KINDS = {
    clang.cindex.CursorKind.IF_STMT,
    clang.cindex.CursorKind.FOR_STMT,
    clang.cindex.CursorKind.WHILE_STMT,
    clang.cindex.CursorKind.DO_STMT,
    clang.cindex.CursorKind.SWITCH_STMT,
}

def calculate_complexity(cursor):
    """计算函数的 McCabe 圈复杂度"""
    decisions = 0
    for child in cursor.walk_preorder():
        if child.kind in DECISION_KINDS:
            if child.kind == clang.cindex.CursorKind.SWITCH_STMT:
                # switch 的复杂度 = case 数
                cases = sum(1 for c in child.get_children()
                           if c.kind == clang.cindex.CursorKind.CASE_STMT)
                decisions += max(cases, 1)
            else:
                decisions += 1
        elif child.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
            # 检查是否是 && 或 ||
            tokens = list(child.get_tokens())
            for t in tokens:
                if t.spelling in ('&&', '||'):
                    decisions += 1
                    break
        elif child.kind == clang.cindex.CursorKind.CONDITIONAL_OPERATOR:
            decisions += 1
    return decisions + 1
```

## networkx 图谱分析

### 构建有向图

```python
import networkx as nx

G = nx.DiGraph()
# 添加节点 (函数)
for func in functions:
    G.add_node(func['id'],
               name=func['name'],
               file=func['file'],
               line=func['line'],
               complexity=func['complexity'],
               is_public=func['is_public'])

# 添加边 (调用关系)
for caller, callee in call_pairs:
    G.add_edge(caller, callee)
```

### 中心性分析

```python
# 入度: 被多少函数调用 → 核心性
in_degree = dict(G.in_degree())

# PageRank: 关键节点
pagerank = nx.pagerank(G)

# 介数中心性: 多少最短路径经过此节点
betweenness = nx.betweenness_centrality(G)
```

### 关键路径分析

```python
# 入口点: 入度为 0 的节点 (不被任何函数调用)
entry_points = [n for n in G.nodes() if G.in_degree(n) == 0]

# 从入口点到高风险函数的最短路径
for entry in entry_points:
    for target in high_risk_targets:
        if nx.has_path(G, entry, target):
            path = nx.shortest_path(G, entry, target)
            # path 是调用链
```

### 强连通分量 (SCC)

```python
sccs = list(nx.strongly_connected_components(G))
# 大于 1 的 SCC 是循环依赖集群，高风险
cyclic_sccs = [scc for scc in sccs if len(scc) > 1]
```

### 桥边分析

```python
# 桥边: 移除后图变为不连通的边 → 高耦合连接
bridges = list(nx.bridges(G))
```

## 图谱序列化

networkx 图谱序列化为 JSON (node-link format):

```python
from networkx.readwrite import json_graph

graph_data = json_graph.node_link_data(G)
with open('call_graph.json', 'w') as f:
    json.dump(graph_data, f, indent=2)
```

反序列化:

```python
with open('call_graph.json') as f:
    data = json.load(f)
G = json_graph.node_link_graph(data)
```

## 编译参数提取

### 优先级 1: compile_commands.json

```json
[
  {
    "directory": "/path/to/build",
    "command": "g++ -std=c++14 -fPIC -I/usr/include/... -c main.cpp",
    "file": "src/main.cpp"
  }
]
```

### 优先级 2: 从 CMakeLists.txt 解析

关键变量:
- CMAKE_CXX_FLAGS
- target_include_directories
- find_package(Qt5 COMPONENTS ...)
- add_compile_options

### 优先级 3: 默认参数

```python
default_args = [
    '-x', 'c++',
    '--std=c++14',
    '-fPIC',
    '-I/usr/include/x86_64-linux-gnu/qt5',
    '-I/usr/include/x86_64-linux-gnu/qt5/QtCore',
    '-I/usr/include/x86_64-linux-gnu/qt5/QtWidgets',
    '-I/usr/include/x86_64-linux-gnu/qt5/QtNetwork',
]
```

## 已知限制

1. Qt 信号槽: Q_OBJECT 的信号声明在 moc 生成的文件中，libclang 解析
   源文件时可能看不到信号定义。需要额外处理 moc 输出文件。
2. 模板函数: libclang 对模板的实例化分析有限。对模板函数只记录声明，
   不追踪实例化后的调用。
3. 宏展开: Q_PROPERTY, Q_DECLARE_METATYPE 等宏展开后的 AST 复杂，
   可能产生噪声节点。需过滤。
4. 大项目性能: libclang 逐文件解析大项目 (100+ 文件) 可能较慢。
   建议先做文件级过滤 (只解析包含 P0/P1 函数的文件)。
5. Python 3.7 限制: 不能用 := (walrus operator), 不能用 dict 的 3.9+ 操作。
