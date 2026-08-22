# qt-unit-test-generate

Risk-driven + theory-graded + code-graph-guided Qt unit test generation skill.

## Core Philosophy

Not blind coverage chasing. Tests are prioritized by risk score (complexity, centrality, fan-out, change rate) and designed using classical test theory (equivalence partitioning, boundary value, basis path, mutation testing).

## Architecture

7-stage pipeline:

| Stage | Name | Script | Output |
|-------|------|--------|--------|
| 0 | Project Survey | — | state.json |
| 1 | Code Graph | build_call_graph.py | call_graph.json |
| 2 | Risk Ranking | prioritize_targets.py | priority_report.json |
| 3 | Test Design | — (AI) | test_design_doc.md |
| 4 | Code Gen | generate_test_skeleton.py | tests/test_*.cpp |
| 5 | Validation | validate_coverage.py | validation_report.md |
| 6 | Mutation | mutation_score.py | mutation_report.md |

## 5-Level Test Design

| Level | Theory | Target | Applies to |
|-------|--------|--------|-----------|
| 0 Smoke | Basic verification | Can call without crash | P3 |
| 1 Specification | Equivalence partitioning + BVA | Data-driven _data() | P2/P1 |
| 2 Structure | Basis path (McCabe V(G)) | Branch coverage | P1/P0 |
| 3 Interaction | Call chain + QSignalSpy | Integration paths | P0 |
| 4 Fault Injection | Mutation testing + error guessing | Mutation score >= 80% | P0 core |

## Example Results (Calculator)

```
52 tests passed, 0 failed
Line coverage: 100% (98/98)
Function coverage: 100% (11/11)
Mutation score: 92.9% (65/87 killed)
```

## Prerequisites

- libclang (LLVM 13) with Python binding
- networkx
- Qt5Test (5.11+) or Qt6Test
- cmake 3.16+ with ctest
- gcov + lcov

## Usage

```bash
# Stage 0: Survey project (manual or AI)
# Write state.json with project_dir, qt_version, source_dirs, etc.

# Stage 1-2: Build code graph and rank by risk
python3 scripts/build_call_graph.py --state state.json
python3 scripts/prioritize_targets.py --state state.json

# Stage 3: AI designs test levels (test_design_doc.md)

# Stage 4: Generate test skeleton
python3 scripts/generate_test_skeleton.py --state state.json --auto

# Stage 5: Build, run, coverage
python3 scripts/validate_coverage.py --state state.json

# Stage 6: Mutation testing
python3 scripts/mutation_score.py --state state.json --all-p0
```

## References

Test design theory grounded in:
- Myers, G.J. (1979). The Art of Software Testing. (equivalence partitioning, BVA)
- McCabe, T. (1976). A Complexity Measure. (basis path testing, cyclomatic complexity)
- Lipton, R. (1978). Mutation Testing. (mutation operators, mutation score)
- Offutt, A.J. & Untch, R.H. (2001). Mutation Testing in the Twentieth Century.

## License

Apache-2.0
