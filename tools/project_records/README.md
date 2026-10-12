# Project record validation

The project and review registers remain canonical scientific records. The former
progress-dashboard rendering and deployment were retired on 2026-10-12; the
new [token dashboard](../token_usage/README.md) does not infer design sign-off.

```sh
python3 -B tools/project_records/fetch_evidence.py
python3 -B tools/project_records/validate.py
python3 -B -m unittest discover -s tools/project_records -p 'test_*.py' -v
```

The first command fetches missing public historical Git commits when needed;
validation itself is offline. Record schema, stable IDs, dependency, revision,
review/approval checks and the existing PR naming/tracking gate are retained.
Scientific prototype and logging checks run in the independent
[validation workflow](../../.github/workflows/validation.yml). Pages deployment
no longer waits for the legacy progress-site renderer or packages its evidence.
