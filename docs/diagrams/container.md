# Lucerna C4 Container

```mermaid
C4Container
title Lucerna v0.1 Containers
System_Boundary(lucerna, "Lucerna") {
  Container(cli, "lucerna-cli", "Typer CLI", "Thin command layer")
  Container(core, "lucerna-core", "Python package", "Domain models, ports, artifacts, labels")
  Container(workflow, "lucerna-workflow", "Python package", "Market-gate compatible walking skeleton")
}
Rel(cli, workflow, "Calls services")
Rel(workflow, core, "Uses shared contracts")
```
