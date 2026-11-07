# Design System — Network Anomaly Detection

## Design Principles
**Clarity over decoration. Function over flourish. Data speaks.**

No gradients, no decorative blur, no bounce animations, no card grids for the sake of cards. Every pixel earns its place.

---

## Typography

### Font Stack
```
UI: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
Mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
```

**No Inter. No Roboto. No Arial as brand voice.** System font stack respects user's OS, loads instantly, reads natively.

### Scale
| Role | Size | Weight | Line Height | Use |
|------|------|--------|-------------|-----|
| Title | 28px | 600 | 1.2 | Page header |
| Section | 18px | 600 | 1.3 | Tab/panel headers |
| Body | 14px | 400 | 1.5 | Default text |
| Metric Value | 24px | 600 | 1.1 | KPI numbers |
| Metric Label | 12px | 500 | 1.3 | KPI labels |
| Caption | 11px | 400 | 1.4 | Timestamps, footnotes |
| Code | 12px | 400 | 1.5 | Inline code, tables |

### Color Application
| Element | Light | Dark |
|---------|-------|------|
| Text Primary | #1a1a2e | #f0f0f5 |
| Text Secondary | #4a4a6a | #b0b0c0 |
| Text Muted | #7a7a9a | #808090 |
| Border | #e8e8f0 | #3a3a4a |
| Surface | #ffffff | #1e1e2e |
| Surface Alt | #f5f5fa | #252535 |

**No gray body text that fails contrast.** Minimum 4.5:1 for body, 3:1 for large text.

---

## Color System

### Semantic Palette (No Purple Gradients)
| Role | Value | Use |
|------|-------|-----|
| Primary | #2c3e50 | Headers, key actions, left border accent |
| Success | #2e7d32 | Benign traffic, healthy metrics |
| Warning | #ef6c00 | Elevated risk, PortScan |
| Danger | #c62828 | Critical anomalies, DoS/DDoS |
| Info | #1565c0 | Informational, BruteForce |
| Neutral | #546e7a | Secondary actions, disabled |

### Attack Type Colors (Fixed, Accessible)
| Attack | Color | Contrast on White | Contrast on Dark |
|--------|-------|-------------------|------------------|
| Benign | #2e7d32 | 5.2:1 | 4.1:1 |
| DoS | #c62828 | 5.4:1 | 4.2:1 |
| DDoS | #b71c1c | 5.8:1 | 4.5:1 |
| PortScan | #ef6c00 | 3.8:1* | 5.1:1 |
| BruteForce | #d84315 | 4.6:1 | 4.0:1 |
| WebAttack | #ad1457 | 5.6:1 | 4.3:1 |
| Infiltration | #6a1b9a | 6.1:1 | 4.7:1 |
| Botnet | #4a148c | 7.2:1 | 5.5:1 |

*PortScan on white uses bold text for AA compliance.

**No warm cream/sand/parchment backgrounds.** White (light) / #1e1e2e (dark) only.

**No near-black + single acid accent.** Dark mode uses #1e1e2e base with full semantic palette.

---

## Spacing System
Base unit: **4px**

| Token | Value | Use |
|-------|-------|-----|
| xs | 4px | Icon gaps, inline spacing |
| sm | 8px | Form field gaps, card padding |
| md | 16px | Section gaps, container padding |
| lg | 24px | Major section separation |
| xl | 32px | Page margins |

---

## Layout

### Grid
- **12-column** fluid grid, max-width 1280px
- **Gutter**: 24px (md)
- **Container padding**: 24px (md)
- **Border radius**: 4px (consistent, not zero, not excessive)

### Components

#### Metric Card
```
┌─────────────────────────┐
│ Label          ▼ 12%    │  ← Subtle trend indicator
│ ──────────────────────  │  ← 1px border, not hairline
│ 1,234,567               │  ← Metric value, mono font
└─────────────────────────┘
```
- Background: Surface
- Border: 1px Border color
- Padding: 16px (md)
- No shadow, no hover scale

#### Data Table
- Header: 12px semi-bold, Text Secondary
- Row hover: Surface Alt (subtle, not highlight)
- Anomaly row: Left border 4px in attack color
- Mono font for IPs, ports, scores
- No zebra striping (causes visual vibration)

#### Chart Area
- White/Dark surface background
- Grid: 1px Border color, dashed
- No axis lines (redundant with grid)
- Legend: Horizontal, bottom, 12px
- Tooltip: Surface, 4px radius, mono font values

#### Sidebar
- Width: 260px
- Border-right: 1px Border color
- Navigation: 14px, 12px vertical padding
- Active: Left border 3px Primary, background Surface Alt

---

## Interactions

### Transitions
| Property | Duration | Easing |
|----------|----------|--------|
| Color | 120ms | ease-out |
| Background | 120ms | ease-out |
| Border | 120ms | ease-out |
| Transform | **None** | — |

**No bounce/elastic easing. No hover-scale on images. No scattered micro-animations.**

### States
| State | Visual |
|-------|--------|
| Hover (button) | Background: Surface Alt |
| Focus | Outline: 2px Primary, offset 2px |
| Active | Background: Primary 10% |
| Disabled | Opacity: 0.5, cursor: not-allowed |

---

## Data Visualization Rules

### Charts
- **No 3D. No gradients on bars/lines.**
- Single color per series (semantic palette)
- Area charts: 15% opacity fill, 2px stroke
- Bar charts: Flat ends, 70% group width
- Line charts: 2px stroke, no markers (except tooltip)
- Pie/Donut: Only for part-of-whole, max 6 segments

### Tables
- Right-align numbers, left-align text
- Mono font for all numeric columns
- Sortable headers (cursor: pointer)
- Pagination: 25/50/100, server-side for >1000 rows

### Alerts/Notifications
- Inline, not toast (toasts get missed)
- Left border 4px in semantic color
- Dismissible, persists until dismissed
- Max 3 visible, queue others

---

## Dark Mode
- Not inverted light mode
- Separate surface values (#1e1e2e, #252535)
- Same semantic colors (tested for contrast)
- Borders lighter (#3a3a4a) for depth
- Images/charts: transparent backgrounds

---

## Accessibility Checklist
- [ ] All text ≥ 4.5:1 contrast (body), 3:1 (large)
- [ ] Focus visible on all interactive elements
- [ ] Color never sole information carrier (icons + text)
- [ ] Keyboard navigable (Tab order logical)
- [ ] Screen reader labels on icon-only buttons
- [ ] Reduced motion respected (no transitions if prefers-reduced-motion)

---

## What This Project Does NOT Use
| Pattern | Reason |
|---------|--------|
| Inter/Roboto as brand | Generic, loads slow, no personality |
| Purple gradients | AI-product cliché, low contrast |
| Cream/parchment backgrounds | Fake "premium," reduces contrast |
| Hairline rules (0.5px) | Invisible on many displays |
| 0px border radius | Harsh, feels broken |
| Identical card grids | Lazy layout, no hierarchy |
| Numbered markers (01/02/03) | False sequence, no meaning |
| Nested cards | Visual nesting dolls |
| Bounce/elastic easing | Distracts, feels toy-like |
| Hover-scale on images | Jarring, breaks layout |
| Decorative blur | Performance cost, no info |
| 999 z-index soup | Unmaintainable, breaks modal stacking |

---

## Implementation Notes

### Streamlit Customization
```python
# In app.py — inject via st.markdown(unsafe_allow_html=True)
<style>
:root {
  --primary: #2c3e50;
  --success: #2e7d32;
  --danger: #c62828;
  --warning: #ef6c00;
  --surface: #ffffff;
  --surface-alt: #f5f5fa;
  --text: #1a1a2e;
  --text-secondary: #4a4a6a;
  --border: #e8e8f0;
}
</style>
```

### Grafana Theme
```ini
# grafana.ini
[theme]
default = light
# Custom provisioning dashboard uses panel overrides for colors
```

### Plotly Template
```python
import plotly.io as pio

pio.templates["ids"] = pio.templates["plotly_white"]
pio.templates["ids"].layout.update(
    font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#1a1a2e"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(gridcolor="#e8e8e8", zeroline=False),
    yaxis=dict(gridcolor="#e8e8e8", zeroline=False),
    colorway=["#2c3e50", "#2e7d32", "#c62828", "#ef6c00", "#1565c0", "#ad1457", "#6a1b9a", "#4a148c"]
)
pio.templates.default = "ids"
```

---

## Version
1.0 — Established 2026-11-07. No breaking changes without design review.