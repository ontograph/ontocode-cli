---
name: axel-qt-visual-testing
description: Capture and visually inspect PySide6 widgets during exploratory GUI testing. Use when asked to verify rendering, widget appearance, or layouts for Python Qt tools; use the C++ Qt Test workflow for the production qt/ client. Captures offscreen screenshots for vision review.
license: BSD-3-Clause-Clear
metadata:
  author: talmolab
  version: "sleap @ 6967e049"
  vendored_from: https://github.com/talmolab/sleap
  vendored_ref: 6967e049debfe9a14818c5708c6c0dca1743e698
  vendored_on: "2026-08-22"
---

# Qt GUI Testing

Capture screenshots of Qt widgets for visual inspection without displaying windows on screen.

## Axel Scope

- Applies to Python/PySide6 widgets and standalone diagnostic tools. It does not
  replace C++ Qt Test coverage for the production client under `qt/`.
- Screenshots are exploratory evidence, not a substitute for committed behavior
  tests. Store them under `build-scratch/evidence/qt-visual` by default so they
  remain outside source control unless a task explicitly requests evidence.
- Headless runs use the offscreen platform. Limit builds to eight parallel jobs.
- Direct `click()` and `toggle()` calls cover only controls exposing those
  methods; menus, drag paths, native dialogs, and window-manager behavior need a
  real display or a C++/native test harness.

## Quick Start

```python
# Capture any widget
from scripts.qt_capture import capture_widget
path = capture_widget(my_widget, "description_here")
# Then read the screenshot with the Read tool
```

## Core Script

Run `scripts/qt_capture.py` or import `capture_widget` from it:

```bash
# Standalone test
uv run --with PySide6 python .claude/skills/axel-qt-visual-testing/scripts/qt_capture.py
```

## Output Location

All screenshots save to: `build-scratch/evidence/qt-visual/`, unless
`AXEL_QT_SCREENSHOT_DIR` is set.

Naming: `{YYYY-MM-DD.HH-MM-SS}_{description}.png`

## Workflow

1. Create/obtain the widget to test
2. Call `capture_widget(widget, "description")`
3. Read the saved screenshot with the Read tool
4. Analyze with vision to verify correctness

## Interaction Pattern

To interact with widgets (click buttons, etc.):

```python
# Find widget at coordinates (from vision analysis)
target = widget.childAt(x, y)

# Trigger it directly (not mouse events)
if hasattr(target, 'click'):
    target.click()
    QApplication.processEvents()

# Capture result
capture_widget(widget, "after_click")
```

## Example: Test a Dialog

```python
import sys
from PySide6.QtWidgets import QApplication
from sleap.gui.learning.dialog import TrainingEditorDialog

# Add skill scripts to path
sys.path.insert(0, ".claude/skills/qt-testing")
from scripts.qt_capture import capture_widget, init_qt

app = init_qt()
dialog = TrainingEditorDialog()
path = capture_widget(dialog, "training_dialog")
dialog.close()
print(f"Inspect: {path}")
```

## Key Points

- Uses `Qt.WA_DontShowOnScreen` - no window popup
- Renders identically to on-screen display (verified)
- Call `processEvents()` after interactions before capture
- Use `childAt(x, y)` to map vision coordinates to widgets
- Direct method calls (`.click()`) work; simulated mouse events don't
