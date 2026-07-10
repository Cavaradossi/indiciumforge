# IndiciumForge C4 Context

```mermaid
C4Context
title IndiciumForge System Context
Person(operator, "Research Operator", "Reviews evidence and decides manually")
System(indiciumforge, "IndiciumForge", "Evidence-first financial research workspace")
System_Ext(indiciumgrid, "IndiciumGrid Frozen Reference", "Golden artifact producer")
System_Ext(providers, "External Providers", "Market data, fundamentals, capture, research engines")
System_Ext(localfs, "Local Artifact Store", "CSV, JSON, Markdown, manifests")
Rel(operator, indiciumforge, "Runs workflows and reviews artifacts")
Rel(indiciumforge, indiciumgrid, "Compares golden reference outputs")
Rel(indiciumforge, providers, "Consumes through governed ports")
Rel(indiciumforge, localfs, "Writes reproducible artifacts")
```
