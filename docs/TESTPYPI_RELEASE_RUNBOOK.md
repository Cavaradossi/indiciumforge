# TestPyPI release runbook

Dry-run procedure for validating IndiciumForge wheels **before** production PyPI. Do not upload to `pypi.org` until the operator explicitly approves.

**Note:** v2.0.0 completed production PyPI publish. Keep this runbook for pre-release validation on future versions.

## Prerequisites

- Python 3.10+
- TestPyPI account: https://test.pypi.org/account/register/
- API token with upload scope (store in env var, never commit)
- Packages built and passing `twine check`

```bash
python -m pip install --upgrade build twine
```

## 1. Build packages (publish order)

Build from each package directory so `README.md` and `pyproject.toml` resolve correctly.

### indiciumforge-core

```bash
cd packages/indiciumforge-core
python -m build
twine check dist/*
```

### indiciumforge-workflow

```bash
cd packages/indiciumforge-workflow
python -m build
twine check dist/*
```

### indiciumforge-cli

```bash
cd packages/indiciumforge-cli
python -m build
twine check dist/*
```

Clean build artifacts after verification if not uploading immediately:

```bash
rm -rf dist build src/*.egg-info
```

## 2. Upload to TestPyPI

Set token (example — use your own, never commit):

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<testpypi-token>
```

Upload in dependency order:

```bash
twine upload --repository testpypi packages/indiciumforge-core/dist/*
twine upload --repository testpypi packages/indiciumforge-workflow/dist/*
twine upload --repository testpypi packages/indiciumforge-cli/dist/*
```

Or configure `~/.pypirc`:

```ini
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-<token>
```

## 3. Install from TestPyPI (clean venv)

```bash
python -m venv /tmp/iforge-testpypi
source /tmp/iforge-testpypi/bin/activate   # Windows: Scripts\activate
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  indiciumforge-cli==2.0.0
indiciumforge --help
```

`--extra-index-url https://pypi.org/simple/` pulls transitive deps (pandas, typer) from production PyPI.

## 4. Smoke commands

```bash
indiciumforge workflow synthetic-e2e --help
indiciumforge artifact audit --help
indiciumforge parity run --help
```

Full golden tests remain a monorepo `pytest` concern — not required for packaging smoke.

## 5. Production PyPI (operator gate)

Only after TestPyPI smoke passes and [PYPI_RELEASE_CHECKLIST.md](PYPI_RELEASE_CHECKLIST.md) is signed off:

```bash
twine upload packages/indiciumforge-core/dist/*
twine upload packages/indiciumforge-workflow/dist/*
twine upload packages/indiciumforge-cli/dist/*
```

## Rollback

TestPyPI allows yanking broken releases. Production PyPI: yank only if install breakage confirmed; prefer patch release `2.0.1` over yank when possible.

## Security

- Never commit `.pypirc`, tokens, or `TWINE_PASSWORD` to Git
- CI upload should use GitHub Actions `secrets.PYPI_API_TOKEN` when automated
- Review wheel contents: `unzip -l dist/*.whl` — no private paths or secrets
