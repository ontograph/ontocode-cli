# Chrome DevTools MCP - Tool Reference

Reference for the 28 tools on the mounted `chrome_devtools` MCP surface.
Verified 2026-08-22. If a parameter documented here is rejected at runtime,
trust the live tool schema; server versions drift. For long-form workflow
narratives, see WORKFLOWS.md.

**Stale-UID rule:** element UIDs change after every page mutation
(navigation, click, fill). Re-run `take_snapshot` after each mutation before
interacting again.

## Input Automation (9)

### click
Clicks or double-clicks the snapshot element with the given UID.
- `uid` (required), `dblClick` (optional, default false)

### drag
Drags one element onto another.
- `from_uid`, `to_uid` (both required)

### fill
Clears and types into an input, textarea, or select.
- `uid` (required), `value` (required); optional `includeSnapshot`

### fill_form
Fills multiple fields in one call. Prefer this over repeated fill calls.
- `elements: [{uid, value}, ...]`; optional `includeSnapshot`

### handle_dialog
Accepts or dismisses a browser dialog (alert/confirm/prompt).
- `action`: "accept" | "dismiss"; optional `promptText`

### hover
Hovers over an element.
- `uid` (required)

### press_key
Presses a key or combination at current focus ("Enter", "Control+A").
- `key` (required); optional `includeSnapshot`

### type_text
Types text at current focus without clearing existing content.
- `text` (required); optional `submitKey`

### upload_file
Sets a file into a file input or file-chooser trigger.
- `uid`, `filePath` (both required); optional `includeSnapshot`

## Navigation (6)

### navigate_page
Navigates by URL, back, forward, or reload.
- `type`: "url" | "back" | "forward" | "reload"; plus `url`, `timeout`,
  `ignoreCache`, `initScript` as applicable

### new_page
Opens a URL in a new tab.
- `url`; optional `background`, `timeout`, `isolatedContext`

### list_pages
Lists open tabs. Returns numeric page IDs used by select/close below.

### select_page
Switches tool context to a tab.
- `pageId` (required); optional `bringToFront`

### close_page
Closes a tab. The last open tab cannot be closed.
- `pageId` (required)

### wait_for
Waits until any of the given texts appears.
- `text`: non-empty string array; optional `timeout` (ms)

## Emulation (2)

### emulate
Emulates features on the selected page in one call.
- `colorScheme` ("dark"|"light"|"auto"), `networkConditions`
  ("Offline"|"Slow 3G"|"Fast 3G"|"Slow 4G"|"Fast 4G"), `cpuThrottlingRate`
  (1 disables), `userAgent`, `viewport` ("WxHxDPR[,mobile][,touch]"),
  `geolocation`, `extraHttpHeaders` (JSON string)

### resize_page
Resizes the window so the page has the given dimension.
- `width`, `height` (both required)

## Performance (3)

### performance_start_trace
Starts tracing on the selected page.
- `reload`, `autoStop`, `filePath` (.json.gz to persist raw trace)

### performance_stop_trace
Stops the active trace and returns results.
- `filePath` (save trace data)

### performance_analyze_insight
Detail for one insight from a finished trace.
- `insightName` (e.g. "LCPBreakdown", "DocumentLatency"), optional
  `insightSetId`

Note: Lighthouse excludes performance; use traces for that.

## Network (2)

### list_network_requests
Recent requests since last navigation.
- `pageSize`, `pageIdx`, `resourceTypes` filter,
  `includePreservedRequests` (last 3 navigations)

### get_network_request
Full request/response detail including timing.
- `reqid`; optional `requestFilePath` / `responseFilePath` to save bodies
  to disk instead of inline output

## Debugging (7)

### evaluate_script
Runs a JavaScript function in the page; JSON-serializable return values.
- `function`; optional `args` (element UIDs), `filePath` (save large
  output), `dialogAction`

### list_console_messages
Console messages since last navigation.
- `pageSize`, `pageIdx`, `types` filter, `includePreservedMessages`

### get_console_message
- `msgid`

### lighthouse_audit
Accessibility / SEO / best-practices / agentic audit. Excludes performance.
- `device` ("desktop"|"mobile"), `mode` ("navigation"|"snapshot"),
  optional `outputDirPath`

### take_heapsnapshot
Heap snapshot of the selected page for leak analysis.
- `filePath` to save .heapsnapshot

### take_screenshot
- `format` ("png"|"jpeg"|"webp"), `quality`, `fullPage`, `filePath`,
  or `uid` for element capture

### take_snapshot
Accessibility tree with stable-per-mutation element UIDs.
- `verbose`, optional `filePath`
