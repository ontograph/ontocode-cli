# Axel Native Grid Qualification

Use correctness mode for Qt/native-grid behavior. Run only the proof surfaces
owned by the changed behavior.

## Workflow

1. Read Axel's Qt runtime evidence instructions and the task acceptance criteria.
2. Use `scripts/run-direct-webhost-final.sh` for the real launcher evidence.
3. Use `scripts/run-native-grid-xdotool-proof.sh` when selection, hit testing,
   navigation, editing, or scrolling changed.
4. Use the AT-SPI or IME proof scripts only when accessibility or IME behavior
   changed.
5. Validate the produced evidence with `scripts/verify-ui-evidence.py` when the
   task emits its supported manifest format.
6. Preserve the launcher log, nonblank capture, interaction artifact, exit
   status, and clean document release evidence in the task evidence directory.

## Fail Closed

Fail correctness qualification when the evidence contains any applicable
failure marker:

```text
result=fail
fallback=browser-grid
surface=QWebEngineView
Segmentation fault
terminate called
```

The browser chrome may legitimately be a `QWebEngineView`; fail only when that
surface is claimed for the spreadsheet grid or native-grid proof.

## Verdict

- `PASS`: real launcher completed, the capture is visible and nonblank, native
  grid ownership is proven, task-specific interaction passes, and document
  release is clean.
- `FAIL_TO_LAUNCH`: the real application did not reach the proof surface.
- `FAIL`: a required assertion or negative marker gate fails.
- `PARTIAL`: a source or performance smoke passed but required correctness
  evidence was not run.

Never promote performance sampling, source checks, mocked DOM output, or a log
string alone to a correctness pass.
