---
name: code-review-change-size
description: Change size guidance (800 lines)
---

Unless the change is mechanical, prefer changes under 800 lines when that still satisfies the requested scope cleanly.
For complex logic changes, prefer changes under 500 lines when that still satisfies the requested scope cleanly.

If the change is larger, first check whether the full requested scope can still land safely as one coherent change. Split into stages only when staging is required by correctness, risk, dependency order, or reviewability, and make the stages map to the real requested end state rather than an arbitrarily smaller subset.
Base any staging suggestion on the actual diff, dependencies, affected call sites, and the user's requested outcome.
