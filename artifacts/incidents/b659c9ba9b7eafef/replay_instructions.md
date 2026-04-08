# Replay instructions

1. Load `config_snapshot.json` as the run configuration.
2. Re-run the pipeline stored in `manifest.json` under `pipeline`.
3. Use `context.json` and `traceback.txt` to reproduce failure conditions.
4. Validate that the same `error_code` is emitted in fail-closed mode.
