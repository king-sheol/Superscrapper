# XLSX Generation Instructions

Generate a Python script that creates a formatted Excel file using openpyxl.

## Requirements

The generated script must:
1. Read data from the normalized dataset (passed as CSV or in-memory)
2. Create two sheets: "Data" and "Metadata"
3. Apply formatting as described below

## Data Sheet

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule
import csv

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Data"

# Header styling
header_font = Font(bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="2B579A", end_color="2B579A", fill_type="solid")
header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# Write headers
for col_idx, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_idx, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_alignment

# Write data rows with alternating row colors
light_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        if row_idx % 2 == 0:
            cell.fill = light_fill

# Auto-width columns
for col_idx in range(1, len(headers) + 1):
    max_length = max(
        len(str(ws.cell(row=r, column=col_idx).value or ""))
        for r in range(1, ws.max_row + 1)
    )
    ws.column_dimensions[get_column_letter(col_idx)].width = min(max_length + 4, 50)

# Auto-filter on headers
ws.auto_filter.ref = ws.dimensions

# Color scale for numeric columns
for col_idx, header in enumerate(headers, 1):
    # Check if column is numeric
    values = [ws.cell(row=r, column=col_idx).value for r in range(2, ws.max_row + 1)]
    if all(isinstance(v, (int, float)) for v in values if v is not None):
        col_letter = get_column_letter(col_idx)
        ws.conditional_formatting.add(
            f"{col_letter}2:{col_letter}{ws.max_row}",
            ColorScaleRule(
                start_type="min", start_color="F8696B",
                mid_type="percentile", mid_value=50, mid_color="FFEB84",
                end_type="max", end_color="63BE7B"
            )
        )

# Freeze top row
ws.freeze_panes = "A2"
```

## Metadata Sheet

```python
ws_meta = wb.create_sheet("Metadata")
ws_meta.append(["Property", "Value"])
ws_meta.append(["Topic", topic])
ws_meta.append(["Collection Date", date_str])
ws_meta.append(["Total Records", len(data)])
ws_meta.append(["Sources Used", len(sources)])
ws_meta.append([])
ws_meta.append(["Source", "Reliability", "Justification"])
for source in sources:
    ws_meta.append([source["url"], source["reliability"], source["justification"]])

# Style metadata headers
for cell in ws_meta[1]:
    cell.font = Font(bold=True)
for cell in ws_meta[7]:
    cell.font = Font(bold=True)
```

## Save

```python
wb.save("data.xlsx")
```

## Also Generate CSV

```python
with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(data)
```
