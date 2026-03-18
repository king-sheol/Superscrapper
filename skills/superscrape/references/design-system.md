# Dashboard Design System — Concrete Design Tokens

> Compiled from: Tremor.so, shadcn/ui, and modern dashboard design patterns (2025-2026).
> Sources: tremor.so, ui.shadcn.com/docs/theming, shadcn design brief (GitHub gist by eonist)

---

## 1. Typography Scale

| Element          | Size     | Weight | Line-Height | Letter-Spacing | Font Family |
|------------------|----------|--------|-------------|----------------|-------------|
| Page title       | 30px / 1.875rem | 700 (bold) | 1.2 | -0.025em | Inter, system-ui, sans-serif |
| Section header   | 20px / 1.25rem  | 600 (semibold) | 1.2 | -0.025em | Inter |
| Card label       | 14px / 0.875rem | 500 (medium) | 1.4 | normal | Inter |
| Card value       | 30px / 1.875rem | 700 (bold) | 1.2 | -0.025em | Inter |
| Card subtitle    | 12px / 0.75rem  | 400 (regular) | 1.4 | normal | Inter |
| Table header     | 12px / 0.75rem  | 500 (medium) | 1.5 | 0.05em (uppercase) | Inter |
| Table cell       | 14px / 0.875rem | 400 (regular) | 1.5 | normal | Inter |
| Badge text       | 12px / 0.75rem  | 500 (medium) | 1.0 | normal | Inter |
| Small/caption    | 12px / 0.75rem  | 400 (regular) | 1.4 | normal | Inter |
| KPI delta        | 14px / 0.875rem | 500 (medium) | 1.4 | normal | Inter, tabular-nums |

### Full Type Scale (reference)
```
h1: 36px / 2.25rem   — weight 700, line-height 1.2
h2: 30px / 1.875rem  — weight 700, line-height 1.2
h3: 24px / 1.5rem    — weight 600, line-height 1.2
h4: 20px / 1.25rem   — weight 600, line-height 1.2
h5: 18px / 1.125rem  — weight 600, line-height 1.2
h6: 16px / 1rem      — weight 600, line-height 1.2
body: 14px / 0.875rem — weight 400, line-height 1.5
small: 12px / 0.75rem — weight 400, line-height 1.4
```

---

## 2. Spacing Scale

### Base Unit: 4px (0.25rem)

| Token | Value   | Rem     | Usage |
|-------|---------|---------|-------|
| sp-0  | 0px     | 0       | — |
| sp-1  | 4px     | 0.25rem | Tight gaps (icon-to-text) |
| sp-2  | 8px     | 0.5rem  | Component internal gaps, button group gaps |
| sp-3  | 12px    | 0.75rem | Small card padding (compact) |
| sp-4  | 16px    | 1rem    | Standard gap, form field spacing |
| sp-5  | 20px    | 1.25rem | Medium padding |
| sp-6  | 24px    | 1.5rem  | Card padding (standard), container padding |
| sp-8  | 32px    | 2rem    | Section vertical margin |
| sp-10 | 40px    | 2.5rem  | Large section gap |
| sp-12 | 48px    | 3rem    | Page section spacing |
| sp-16 | 64px    | 4rem    | Hero/page-level spacing |

### Dashboard-Specific Spacing

| Element             | Value  |
|---------------------|--------|
| Card padding        | 24px (p-6) |
| Card padding compact | 16px (p-4) |
| Card internal gap   | 8px (gap-2) |
| Section gap (between card groups) | 32px (gap-8) |
| Grid gap (between cards) | 16px (gap-4) or 24px (gap-6) |
| Sidebar width       | 240px (collapsed: 64px) |
| Sidebar padding     | 16px |
| Topbar height       | 56px or 64px |
| Button padding      | 16px horizontal, 8px vertical (px-4 py-2) |
| Button padding sm   | 12px horizontal, 8px vertical (px-3 py-2) |
| Button padding lg   | 32px horizontal, 8px vertical (px-8 py-2) |
| Container max-width | 1280px (xl) |
| Content max-width   | 600px (prose/readability) |
| Table cell padding  | 12px horizontal, 8px vertical |

---

## 3. Color System

### 3A. Background Levels (Dark Theme)

| Token                | Hex       | HSL                  | Usage |
|----------------------|-----------|----------------------|-------|
| bg-primary (page)    | #020617   | 222.2 84% 4.9%      | Main page background |
| bg-secondary (card)  | #0f172a   | 217.2 32.6% 17.5%   | Cards, elevated surfaces |
| bg-tertiary (hover)  | #1e293b   | 215.3 25% 17.3%     | Hover states, active sidebar items |
| bg-input             | #1e293b   | 215.3 25% 17.3%     | Input fields background |
| bg-popover           | #0f172a   | 217.2 32.6% 17.5%   | Dropdowns, tooltips, dialogs |

### 3B. Background Levels (Light Theme)

| Token                | Hex       | HSL                  | Usage |
|----------------------|-----------|----------------------|-------|
| bg-primary (page)    | #ffffff   | 0 0% 100%           | Main page background |
| bg-secondary (card)  | #f8fafc   | 210 40% 98%         | Cards, elevated surfaces |
| bg-tertiary (hover)  | #f1f5f9   | 210 40% 96.1%       | Hover states |
| bg-muted             | #f1f5f9   | 210 40% 96.1%       | Muted/inactive areas |

### 3C. Text Levels (Dark Theme)

| Token              | Hex       | HSL                    | Usage |
|--------------------|-----------|------------------------|-------|
| text-primary       | #f8fafc   | 210 40% 98%           | Headings, card values, primary text |
| text-secondary     | #e2e8f0   | 214.3 31.8% 91.4%    | Body text, descriptions |
| text-tertiary      | #94a3b8   | 215.4 16.3% 65.1%    | Labels, captions, subtitles |
| text-muted         | #64748b   | 215.4 16.3% 46.9%    | Placeholder text, disabled |

### 3D. Text Levels (Light Theme)

| Token              | Hex       | HSL                    | Usage |
|--------------------|-----------|------------------------|-------|
| text-primary       | #020617   | 222.2 84% 4.9%       | Headings, card values |
| text-secondary     | #334155   | 215.3 25% 26.7%      | Body text |
| text-tertiary      | #64748b   | 215.4 16.3% 46.9%    | Labels, captions |
| text-muted         | #94a3b8   | 215.4 16.3% 65.1%    | Placeholder, disabled |

### 3E. Accent / Primary Colors

| Token          | Hex       | HSL                  | Usage |
|----------------|-----------|----------------------|-------|
| primary        | #3b82f6   | 221.2 83.2% 53.3%   | Primary buttons, links, active states |
| primary-hover  | #2563eb   | 221.2 83.2% 53.3%/90% | Hover state (90% opacity) |
| primary-foreground | #f8fafc | 210 40% 98%        | Text on primary background |

### 3F. Semantic Colors

| Token      | Hex       | Tailwind Equivalent | Usage |
|------------|-----------|---------------------|-------|
| success    | #22c55e   | green-500           | Positive metrics, up trends, completed |
| success-bg | #052e16   | green-950           | Success badge background (dark) |
| success-bg-light | #f0fdf4 | green-50          | Success badge background (light) |
| warning    | #f59e0b   | amber-500           | Caution, pending states |
| warning-bg | #451a03   | amber-950           | Warning badge background (dark) |
| warning-bg-light | #fffbeb | amber-50          | Warning badge background (light) |
| error      | #ef4444   | red-500             | Errors, destructive, down trends |
| error-bg   | #450a0a   | red-950             | Error badge background (dark) |
| error-bg-light | #fef2f2 | red-50             | Error badge background (light) |
| info       | #3b82f6   | blue-500            | Informational, neutral states |

### 3G. Chart Palette (Tremor-derived, 8 colors)

```
Chart color 1:  #3b82f6  (blue-500)
Chart color 2:  #06b6d4  (cyan-500)
Chart color 3:  #6366f1  (indigo-500)
Chart color 4:  #8b5cf6  (violet-500)
Chart color 5:  #d946ef  (fuchsia-500)
Chart color 6:  #f43f5e  (rose-500)
Chart color 7:  #f97316  (orange-500)
Chart color 8:  #eab308  (yellow-500)
```

Extended palette (for many-category charts):
```
blue-500:    #3b82f6
cyan-500:    #06b6d4
indigo-500:  #6366f1
violet-500:  #8b5cf6
fuchsia-500: #d946ef
rose-500:    #f43f5e
orange-500:  #f97316
yellow-500:  #eab308
emerald-500: #10b981
teal-500:    #14b8a6
sky-500:     #0ea5e9
pink-500:    #ec4899
```

---

## 4. Border & Radius

### Border Radius Scale

| Token        | Value   | Usage |
|--------------|---------|-------|
| radius-none  | 0px     | — |
| radius-sm    | 2px     | Nested inner elements, button groups |
| radius-default | 4px   | Alert banners, small elements |
| radius-md    | 6px     | Buttons, input fields, select |
| radius-lg    | 8px     | Cards, dialogs, modals, dropdowns |
| radius-xl    | 12px    | Large containers, hero cards |
| radius-full  | 9999px  | Pills, tags, badges, avatars |

### Dashboard Component Radius

| Component     | Radius |
|---------------|--------|
| Card          | 8px (radius-lg) |
| Badge         | 9999px (radius-full) or 6px (radius-md) |
| Input         | 6px (radius-md) |
| Button        | 6px (radius-md) |
| Dialog/Modal  | 8px (radius-lg) |
| Tooltip       | 6px (radius-md) |
| Table container | 8px (radius-lg) |
| Avatar        | 9999px (radius-full) |

### Border Colors & Widths

| Token               | Value (Dark)       | Value (Light)      |
|----------------------|--------------------|--------------------|
| border-default       | #1e293b (slate-800) | #e2e8f0 (slate-200) |
| border-subtle        | #334155 (slate-700) | #f1f5f9 (slate-100) |
| border-input         | #334155 (slate-700) | #e2e8f0 (slate-200) |
| border-focus         | #3b82f6 (blue-500)  | #3b82f6 (blue-500) |
| border-width-default | 1px                | 1px                |
| border-width-focus   | 2px                | 2px                |

---

## 5. Shadows & Effects

### Shadow Scale (Light Theme)

```css
--shadow-xs:  0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-sm:  0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
--shadow-md:  0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg:  0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl:  0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

### Shadow Scale (Dark Theme)

In dark themes, shadows are less effective. Use border + subtle background shifts instead:
```css
--shadow-card-dark: 0 1px 2px rgba(0, 0, 0, 0.3);
/* Or simply: no shadow, use border-default (1px solid #1e293b) */
```

### Overlay / Backdrop

```css
--overlay-bg: rgba(0, 0, 0, 0.50);    /* dialog overlay dark */
--overlay-bg-light: rgba(0, 0, 0, 0.40); /* dialog overlay light */
--backdrop-blur: 8px;                  /* blur behind overlays */
```

### Opacity Levels

| Token           | Value | Usage |
|-----------------|-------|-------|
| opacity-disabled | 0.4  | Disabled elements |
| opacity-hover   | 0.9   | Primary button hover (90%) |
| opacity-inactive | 0.3  | Inactive chart segments |
| opacity-overlay | 0.5   | Modal/dialog backdrop |
| opacity-muted   | 0.6   | Muted/secondary elements |

---

## 6. Chart Styling

### Axis & Grid

| Token               | Value (Dark)        | Value (Light)       |
|----------------------|---------------------|---------------------|
| axis-line-color      | #334155 (slate-700) | #e2e8f0 (slate-200) |
| axis-tick-color      | #64748b (slate-500) | #94a3b8 (slate-400) |
| axis-label-color     | #94a3b8 (slate-400) | #64748b (slate-500) |
| axis-label-size      | 12px                | 12px                |
| grid-line-color      | #1e293b (slate-800) | #f1f5f9 (slate-100) |
| grid-line-style      | dashed or solid     | dashed or solid     |
| grid-line-width      | 1px                 | 1px                 |
| grid-line-opacity    | 0.5                 | 1.0                 |

### Tooltip (Tremor-style)

```css
/* Dark theme tooltip */
.chart-tooltip {
  background: #0f172a;          /* slate-900 */
  border: 1px solid #1e293b;    /* slate-800 */
  border-radius: 6px;           /* radius-md */
  padding: 8px 16px;            /* py-2 px-4 */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  font-size: 14px;
}

/* Light theme tooltip */
.chart-tooltip-light {
  background: #ffffff;
  border: 1px solid #e2e8f0;    /* slate-200 */
  border-radius: 6px;
  padding: 8px 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  font-size: 14px;
}

/* Tooltip category label */
.tooltip-label {
  color: #94a3b8;               /* slate-400 (dark) / slate-500 (light) */
  font-size: 12px;
  font-weight: 400;
}

/* Tooltip value */
.tooltip-value {
  color: #f8fafc;               /* slate-50 (dark) / slate-900 (light) */
  font-size: 14px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

/* Tooltip color dot */
.tooltip-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
}
```

### Animation Durations

| Token                   | Value  | Usage |
|-------------------------|--------|-------|
| chart-animation-enter   | 300ms  | Initial chart render |
| chart-animation-update  | 200ms  | Data update transitions |
| tooltip-animation       | 150ms  | Tooltip show/hide |
| hover-transition        | 150ms  | Element hover states |
| expand-collapse         | 200ms-250ms | Accordion, dropdown |
| page-transition         | 300ms  | Route/page transitions |

### Cursor & Interaction

```css
.chart-cursor-line {
  stroke: #64748b;              /* slate-500 */
  stroke-width: 1px;
  stroke-dasharray: 4 4;
}

.chart-active-dot {
  stroke: #ffffff;              /* white ring around active dot */
  stroke-width: 2px;
  r: 5px;                      /* dot radius */
}
```

---

## 7. Component Patterns

### 7A. KPI Card Layout

```
+---------------------------------------+
|  [icon]   Label text          [badge]  |   <- row: items-center justify-between
|                                        |
|  $45,100                               |   <- value: text-3xl font-bold
|                                        |
|  +9.1% vs last period                  |   <- delta: text-sm, color semantic
+---------------------------------------+

Card: bg-secondary, border-default, radius-lg, p-6
Label: text-tertiary, 14px, font-medium
Value: text-primary, 30px, font-bold, tabular-nums
Delta positive: text-success (#22c55e)
Delta negative: text-error (#ef4444)
Delta neutral: text-tertiary (#94a3b8)
Badge: radius-full, px-2.5 py-0.5, text-xs font-medium
```

### 7B. Table Styling

```css
/* Table container */
.table-container {
  border: 1px solid var(--border-default);
  border-radius: 8px;
  overflow: hidden;
}

/* Table header */
.table-header {
  background: #0f172a;         /* dark: slate-900 */
  /* light: #f8fafc (slate-50) */
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;              /* slate-400 */
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-default);
  text-align: left;
}

/* Table row */
.table-row {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-default);
  font-size: 14px;
  color: var(--text-secondary);
  transition: background 150ms ease;
}

.table-row:hover {
  background: #1e293b;         /* dark: slate-800 */
  /* light: #f8fafc (slate-50) */
}

.table-row:last-child {
  border-bottom: none;
}

/* Numeric cells */
.table-cell-numeric {
  font-variant-numeric: tabular-nums;
  text-align: right;
}
```

### 7C. Filter / Toolbar Styling

```css
/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;                    /* gap-2 */
  padding: 0 0 24px 0;        /* pb-6 */
  border-bottom: 1px solid var(--border-default);
  margin-bottom: 24px;
}

/* Filter chip / select */
.filter-select {
  height: 36px;
  padding: 0 12px;
  font-size: 14px;
  border: 1px solid var(--border-input);
  border-radius: 6px;
  background: var(--bg-input);
  color: var(--text-secondary);
  transition: border-color 150ms ease;
}

.filter-select:focus {
  border-color: var(--primary);
  outline: 2px solid rgba(59, 130, 246, 0.5);  /* blue-500 at 50% */
  outline-offset: 2px;
}

/* Search input */
.search-input {
  height: 40px;
  padding: 0 12px 0 36px;     /* left padding for icon */
  font-size: 14px;
  border: 1px solid var(--border-input);
  border-radius: 6px;
  background: var(--bg-input);
  width: 240px;
}
```

### 7D. Sidebar Navigation

```css
.sidebar {
  width: 240px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-default);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 400;
  color: var(--text-tertiary);
  transition: all 150ms ease;
  cursor: pointer;
}

.sidebar-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.sidebar-item.active {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-weight: 500;
}

.sidebar-icon {
  width: 20px;
  height: 20px;
  opacity: 0.7;
}

.sidebar-section-label {
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: 16px 12px 4px;
}
```

---

## 8. CSS Variables Summary (Dark Theme)

```css
:root[data-theme="dark"] {
  /* Backgrounds */
  --bg-primary:     #020617;
  --bg-secondary:   #0f172a;
  --bg-tertiary:    #1e293b;
  --bg-input:       #1e293b;

  /* Text */
  --text-primary:   #f8fafc;
  --text-secondary: #e2e8f0;
  --text-tertiary:  #94a3b8;
  --text-muted:     #64748b;

  /* Borders */
  --border-default: #1e293b;
  --border-subtle:  #334155;
  --border-input:   #334155;

  /* Primary */
  --primary:        #3b82f6;
  --primary-fg:     #f8fafc;

  /* Semantic */
  --success:        #22c55e;
  --warning:        #f59e0b;
  --error:          #ef4444;
  --info:           #3b82f6;

  /* Charts */
  --chart-1:        #3b82f6;
  --chart-2:        #06b6d4;
  --chart-3:        #6366f1;
  --chart-4:        #8b5cf6;
  --chart-5:        #d946ef;
  --chart-6:        #f43f5e;
  --chart-7:        #f97316;
  --chart-8:        #eab308;

  /* Radius */
  --radius-sm:      2px;
  --radius-default: 4px;
  --radius-md:      6px;
  --radius-lg:      8px;
  --radius-xl:      12px;

  /* Shadows */
  --shadow-sm:      0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
  --shadow-md:      0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -1px rgba(0,0,0,0.2);
}
```

## 9. CSS Variables Summary (Light Theme)

```css
:root {
  /* Backgrounds */
  --bg-primary:     #ffffff;
  --bg-secondary:   #f8fafc;
  --bg-tertiary:    #f1f5f9;
  --bg-input:       #ffffff;

  /* Text */
  --text-primary:   #020617;
  --text-secondary: #334155;
  --text-tertiary:  #64748b;
  --text-muted:     #94a3b8;

  /* Borders */
  --border-default: #e2e8f0;
  --border-subtle:  #f1f5f9;
  --border-input:   #e2e8f0;

  /* Primary */
  --primary:        #3b82f6;
  --primary-fg:     #ffffff;

  /* Semantic */
  --success:        #22c55e;
  --warning:        #f59e0b;
  --error:          #ef4444;
  --info:           #3b82f6;

  /* Charts (same for both themes) */
  --chart-1:        #3b82f6;
  --chart-2:        #06b6d4;
  --chart-3:        #6366f1;
  --chart-4:        #8b5cf6;
  --chart-5:        #d946ef;
  --chart-6:        #f43f5e;
  --chart-7:        #f97316;
  --chart-8:        #eab308;

  /* Radius */
  --radius-sm:      2px;
  --radius-default: 4px;
  --radius-md:      6px;
  --radius-lg:      8px;
  --radius-xl:      12px;

  /* Shadows */
  --shadow-sm:      0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md:      0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  --shadow-lg:      0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
}
```

---

## 10. Responsive Breakpoints

| Token | Width   | Usage |
|-------|---------|-------|
| sm    | 640px   | Mobile landscape |
| md    | 768px   | Tablet portrait |
| lg    | 1024px  | Tablet landscape / small desktop |
| xl    | 1280px  | Desktop |
| 2xl   | 1536px  | Large desktop |

### Dashboard Grid Patterns

```
Mobile (<768px):     1 column, cards stack vertically
Tablet (768-1024):   2 columns for KPI cards, full-width charts
Desktop (1024-1280): Sidebar(240px) + 3-col KPI grid + 2-col chart grid
Large (>1280):       Sidebar(240px) + 4-col KPI grid + 2-col chart grid
```

### Grid Column Configuration

```css
/* KPI cards grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

/* Chart grid */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);  /* 2 columns at desktop */
  gap: 24px;
}

/* Full-width chart */
.chart-full {
  grid-column: 1 / -1;
}
```
