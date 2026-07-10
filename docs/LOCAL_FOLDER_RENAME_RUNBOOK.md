# Local folder rename runbook (Lucerna → IndiciumForge)

Operator procedure for renaming the local checkout directory after the GitHub repository was renamed to `Cavaradossi/indiciumforge`. **No feature changes** — paths and remotes only.

## Prerequisites

- All work committed or stashed
- No running processes using `D:\project\Lucerna` (IDE, terminals, file watchers)

## 1. Close IDE and terminals

1. Save all files in Cursor/VS Code
2. Close the workspace rooted at `D:\project\Lucerna`
3. Close any shells with `cd` into that directory
4. Optional: `Get-Process | Where-Object { $_.Path -like '*Lucerna*' }` — stop stray watchers

## 2. Rename directory

From PowerShell (run outside the repo):

```powershell
Rename-Item -Path "D:\project\Lucerna" -NewName "IndiciumForge"
```

If rename fails (file lock), reboot or close locking apps and retry. Alternative:

```powershell
robocopy "D:\project\Lucerna" "D:\project\IndiciumForge" /E /MOVE
```

## 3. Re-open and fix `origin`

```powershell
cd D:\project\IndiciumForge
git remote -v
git remote set-url origin https://github.com/Cavaradossi/indiciumforge.git
git remote -v
git fetch origin
```

Expected `origin` URL: `https://github.com/Cavaradossi/indiciumforge.git`

## 4. Reinstall editable packages

From repo root:

```powershell
python -m pip install -e packages/indiciumforge-core -e packages/indiciumforge-workflow -e packages/indiciumforge-cli -e ".[dev]"
```

## 5. Smoke test

```powershell
indiciumforge --help
python -m ruff check .
python -m pytest -q
```

## 6. Cursor workspace

Re-open `D:\project\IndiciumForge` as the workspace root. Update any user-local bookmarks or automation paths that still reference `D:\project\Lucerna`.

## Rollback

Rename `IndiciumForge` back to `Lucerna` if needed. `origin` redirect from GitHub still works for old clone URLs.

## Not in scope

- Private repo paths (`lucerna-private`, `indiciumforge-private`)
- PyPI upload (see [TESTPYPI_RELEASE_RUNBOOK.md](TESTPYPI_RELEASE_RUNBOOK.md))
- Renaming the `indiciumgrid` workspace
