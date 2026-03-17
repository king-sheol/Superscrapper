---
description: "Collect, analyze, and visualize data from the web on any topic"
argument-hint: "topic to research (e.g., 'CRM systems', 'laptops under $1000')"
---

# /superscrape

Launch the Superscrape data collection workflow.

**Usage:**
- `/superscrape CRM systems` — start collecting data on CRM systems
- `/superscrape ноутбуки до 100000 рублей` — compare laptops under 100k RUB
- `/superscrape` — start without a topic (will ask)

## Instructions

1. If `$ARGUMENTS` is provided, use it as the research topic.
2. If no arguments, use AskUserQuestion to ask: "What topic should I research?"
3. Load and follow the `superscrape` skill to execute the full data collection workflow.

The skill handles everything: source discovery, data collection, normalization, report generation, dashboard creation, and deployment.
