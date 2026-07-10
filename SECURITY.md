# Security Policy

## Supported versions

Security fixes are considered for the current signed release line on `master`
(pyproject version `1.0.0`, documented as v1.0.0).

## Reporting a vulnerability

If you believe you have found a security issue in this repository:

1. **Do not** open a public issue for sensitive reports.
2. Contact the repository maintainers through your project's private security channel.
3. Include:
   - affected component (package, CLI command, file path),
   - reproduction steps,
   - impact assessment,
   - suggested fix if available.

## What to include in reports

- Minimal reproduction steps and relevant logs.
- Version/commit hash when possible.

## What not to report as security vulnerabilities

- **Trading performance**, market outcomes, or strategy quality.
- Missing features (live providers, production workflow chain, proprietary detectors).
- Research disagreements with demo/synthetic fixture behavior.
- Golden parity gaps unless they expose a concrete security defect.

## What not to include in reports

- API keys, tokens, passwords, or session cookies.
- Account identifiers, brokerage credentials, or personal financial data.
- Browser profiles, private source lists, or local `output/` / `.indiciumgrid/` artifacts.
- PDFs or raw cache dumps from private environments.

Lucerna is **alpha research software**. It is not a trading or execution system and does not
place orders. Security reports should focus on software defects (dependency issues, unsafe
defaults, secret leakage paths), not investment advice or P&L.

## Response expectations

Maintainers will acknowledge good-faith reports when possible. Public alpha may have best-effort
response times without a formal SLA.
