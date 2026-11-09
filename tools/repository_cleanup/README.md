# Immutable cleanup audit

Read the [issue #120 plan](../../docs/maintenance/issue-120-repository-cleanup.md)
for the conditional deletion schedule, consumers and retention prerequisites.
`audit.py` inventories ordinary Git files at a full commit SHA, reports checkout
bytes and large duplicate blobs, and fingerprints triaged numerical outputs.
It has no deletion operation and reads no private client stores.

```sh
python3 -B tools/repository_cleanup/audit.py \
  --revision 2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7 \
  --output docs/maintenance/issue-120-inventory.json --check
python3 -B -m unittest discover -s tools/repository_cleanup -p 'test_*.py' -v
```

For a new snapshot, choose a new `--output` without `--check`; an existing file
is never overwritten. Without `--output` the report goes to stdout. Output is
deterministic for the same source revision and rules. The original revision
must be present locally. The report is metadata retained for review, not raw
numerical evidence or a claim that runtime reproduction has passed. All byte
counts concern the selected tree; Git history and packfile size are separate.
