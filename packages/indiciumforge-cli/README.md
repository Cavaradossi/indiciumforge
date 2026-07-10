# indiciumforge-cli

**IndiciumForge is an open-core toolkit for reproducible financial research workflows.**

This package provides the **`indiciumforge` CLI** for running workflow chains, checking output completeness, inspecting demo providers, and comparing runs against reference fixtures.

**Not a trading system, broker gateway, or investment advice.**

## Install

```bash
pip install indiciumforge-cli==2.0.1
```

This pulls `indiciumforge-workflow` and `indiciumforge-core` as dependencies.

Monorepo development:

```bash
pip install -e packages/indiciumforge-core -e packages/indiciumforge-workflow -e packages/indiciumforge-cli
```

## Quick smoke

```bash
indiciumforge --help
```

## More documentation

- [Repository README](https://github.com/Cavaradossi/indiciumforge/blob/master/README.md)
- [中文说明](https://github.com/Cavaradossi/indiciumforge/blob/master/README_CN.md)
- [Glossary](https://github.com/Cavaradossi/indiciumforge/blob/master/docs/GLOSSARY.md)
