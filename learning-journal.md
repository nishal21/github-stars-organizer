# Learning Journal

## 2026-06-09 — graphify CLI not found on Windows

- **Cause:** `pip install graphifyy` put `graphify.exe` in `C:\Users\hp\AppData\Roaming\Python\Python313\Scripts\`, which is **not** on PATH. PATH only had `C:\Python313\Scripts\`.
- **Workaround:** Run `python -m graphify <command>` instead of `graphify <command>`.
- **Fix (optional):** Add user Scripts to PATH, or reinstall globally: `python -m pip install --force-reinstall graphifyy`.
- **Verified:** `python -m graphify install --platform cursor` wrote `.cursor/rules/graphify.mdc`.
- **Next:** Run `/graphify .` in Cursor to build the knowledge graph for this repo.
