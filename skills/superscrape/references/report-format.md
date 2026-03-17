# Analytical Report Format

Every report follows this exact structure. All sections are mandatory.

## Template

```markdown
# [Research Topic]
> Date: YYYY-MM-DD | Sources: N | Records: M

## Overview
- **WHAT IS THIS:** One sentence describing the table contents
- **HOW TO READ:** How to interpret columns, what units are used
- **KEY INSIGHT:** The single most important finding
- **CONCLUSION:** What to do with this information

## Data

| Name | [metric 1] | [metric 2] | ... | Source | Collection Date |
|------|------------|------------|-----|--------|-----------------|
| ...  | ...        | ...        | ... | [URL]  | YYYY-MM-DD      |

## Analysis

### Leaders
- Who leads and why (with specific numbers)
- What makes them stand out

### Patterns
- Common trends across the data
- Correlations between metrics

### Anomalies
- Outliers and why they exist
- Suspicious data points and their explanation

### Market Context
- How does this data compare to market averages
- Industry benchmarks where available

## Conclusions & Recommendations
- Actionable recommendations based on data
- Who benefits from what
- Risk factors to consider

## Confidence Map

| Source | Reliability | Justification |
|--------|------------|---------------|
| [URL]  | High       | Verified aggregator with 10k+ reviews |
| [URL]  | Medium     | Official site but data may be biased |
| [URL]  | Low        | Blog post, single author opinion |
```

## Rules for Report Writing

1. **Numbers need context**: "Rating 4.5 (top 10% in category)" not just "Rating 4.5"
2. **N/A must be explained**: "N/A — source does not publish pricing" not just "N/A"
3. **Insights must be specific**: "Product X leads because of 2x lower price at same quality" not "Product X is good"
4. **Recommendations must be actionable**: "For teams under 10, choose Y because..." not "Y is recommended"
5. **Sources must be linked**: every data point traceable to a URL
6. **Confidence map mandatory**: reader must know how much to trust each source
