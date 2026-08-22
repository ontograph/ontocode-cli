# Routine Tool Envelope

Every cataloged operation returns this envelope. Domain owners may add fields
inside `data`, but the shared fields remain required.

```json
{
  "schema_version": "ontocode.routine-tool/1",
  "operation": "OPERATION_ID",
  "owner_skill": "owner-skill-name",
  "status": "ok | partial | denied | timeout | error",
  "data": {},
  "warnings": [],
  "errors": [],
  "evidence": {
    "commands": [],
    "artifacts": [],
    "truncated": false
  },
  "mutation": {
    "requested": false,
    "performed": false,
    "approval": null
  }
}
```

## Field Rules

- `operation` must exactly match the catalog ID.
- `status=partial` requires `warnings` to explain what was omitted and why.
- `errors` entries use stable uppercase snake-case `code`, a human-readable `message`, and optional `details`.
- `evidence.artifacts` entries include `path`, `sha256`, and `byte_size` when a file exists.
- `mutation.requested` is true only when the caller asked for a mutation.
- `mutation.performed` is false for dry runs. A non-dry-run mutation requires `approval` and before/after evidence.
- Secrets, credentials, full prompt bodies, and irrelevant user content must not appear in any field.
- A timeout or denial may return partial evidence, but must not synthesize a successful result.

## Implementation Gate

An operation is implemented only when its owner provides all of the following:

1. A runnable script, CLI, or MCP tool.
2. Success, partial, denied, timeout, and invalid-input fixture tests.
3. Documentation with trigger phrases, inputs, outputs, limits, and owner name.
4. A conformance check against this envelope.
