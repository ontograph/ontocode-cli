---
name: excel
description: Route Excel workbook inspection, formula analysis, reconciliation, export, and migration review through the live Excel tool namespace. Use for .xlsx, .xlsm, or .xlsb workspace tasks only when the current host exposes Excel tools.
---

# Excel

Use the live `excel` tools when they are available on the current host. If the
namespace is absent, say that Excel tooling is unavailable and use another path
only when it can satisfy the request without pretending to inspect a workbook.

## Route the task

1. Start with bounded workbook inspection when the workbook structure or sheet
   names are unknown.
2. Use a worksheet preview for values, a formula inspection or dependency tool
   for formula questions, and a specialized metadata tool for charts, tables,
   links, filters, protection, layout, or other package structure.
3. Use exact structural comparison or reconciliation only when the user supplies
   the required workbook sides, ranges, keys, mappings, and tolerances.
4. Export a sheet only when the whole worksheet must be materialized. Prefer a
   bounded preview for inspection.
5. Use the migration and translation tools for review evidence and generated
   previews. Keep unsupported operations explicit instead of filling gaps with
   inferred behavior.
6. For `named_range_rewrite_dry_run`, construct the mapping file from
   `references/named-range-rewrite-mapping.example.json`; validate version 1
   documents against `references/named-range-rewrite-mapping.schema.json`.

## Boundaries

- Treat stored package values and metadata as evidence. Do not claim formula
  recalculation, rendered appearance, live refresh, or semantic equivalence
  unless the selected tool explicitly proves it.
- Never execute workbook macros. Use extraction, analysis, and preview tools for
  VBA or Power Query migration work.
- Preserve the source workbook unless the user requests a tool that explicitly
  writes an output artifact. Report the output path and any truncation or partial
  result.
- Respect each tool's supported file formats and bounds. Do not silently convert
  unsupported formats or infer worksheet renames, fuzzy matches, or missing
  parameters.
- Prefer the narrowest tool that proves the requested claim, and surface
  warnings, blockers, unsupported sections, and fail-closed results.

## Routine Tool Ownership

This skill owns routine-tool operation 38, `EXCEL_WORKBOOK_INVENTORY`, in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Inventory
results must identify sheets, formulas, VBA, Power Query, protection, links,
pivots, migration blockers, truncation, and warnings through the coordinator's
shared envelope.
