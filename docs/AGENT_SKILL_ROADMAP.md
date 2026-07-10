# Agent skill roadmap

Planned Cursor Agent Skills for IndiciumForge. Skills live in-repo under `agent/skills/` for copy/install into `~/.cursor/skills/` or project `.cursor/skills/`.

## Shipped skills (v2.0.0+)

| Skill | Path | Purpose |
| --- | --- | --- |
| `indiciumforge-orientation` | [agent/skills/indiciumforge-orientation/SKILL.md](../agent/skills/indiciumforge-orientation/SKILL.md) | Onboard agents to repo docs and boundaries |
| `indiciumforge-extension-author` | [agent/skills/indiciumforge-extension-author/SKILL.md](../agent/skills/indiciumforge-extension-author/SKILL.md) | Guide private pack authoring |
| `indiciumforge-release-audit` | [agent/skills/indiciumforge-release-audit/SKILL.md](../agent/skills/indiciumforge-release-audit/SKILL.md) | Pre-release GitHub/PyPI/security checks |

## Installation

Copy a skill directory to your Cursor skills folder:

```text
cp -r agent/skills/indiciumforge-orientation ~/.cursor/skills/
```

On Windows:

```powershell
Copy-Item -Recurse agent\skills\indiciumforge-orientation $env:USERPROFILE\.cursor\skills\
```

Restart or reload Cursor so skills are discovered.

## Future skills (not in v2.0.0)

| Slug | Trigger | Notes |
| --- | --- | --- |
| `indiciumforge-parity-operator` | Parity harness debugging | Reference trees stay operator-local |
| `indiciumforge-golden-author` | New golden scenario design | Requires frozen reference discipline |
| `indiciumforge-adr-drafter` | Architecture decision drafts | Align with ADR template |

## Boundaries

Skills must not:

- Reference private repo paths, account data, or watchlists
- Embed API keys, tokens, or cookies
- Imply trading execution or investment advice
- Depend on MCP servers (future surface — see [mcp/INDICIUMFORGE_MCP_DESIGN.md](mcp/INDICIUMFORGE_MCP_DESIGN.md))

## Related docs

- [AGENT_QUICKSTART.md](AGENT_QUICKSTART.md)
- [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md)
- [FUTURE_SURFACES.md](FUTURE_SURFACES.md)
