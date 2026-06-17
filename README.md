# CCRI Web Analytics — SQL Portfolio Project

A simulated higher education web analytics database built with **SQLite** and **Python**, inspired by real GA4/Search Console data patterns. Includes a standalone HTML dashboard.

> Built as a SQL learning project. Data is synthetic and CCRI-themed.

---

## What it demonstrates

- Relational database design (4 tables, foreign keys, normalized schema)
- Realistic seed data generation with weighted distributions
- Analytical SQL: JOINs, aggregates, window-adjacent patterns, subqueries
- Python + SQLite integration (`sqlite3` stdlib)
- Data export pipeline (DB → JSON → HTML dashboard)

---

## Schema / ERD

```
┌─────────────────┐        ┌──────────────────────┐
│     pages       │        │   traffic_sources     │
├─────────────────┤        ├──────────────────────┤
│ page_id (PK)    │        │ source_id (PK)        │
│ path            │        │ source  (google, etc) │
│ title           │        │ medium  (organic, cpc)│
│ section         │        └──────────┬───────────┘
└────────┬────────┘                   │
         │                            │
         │         ┌──────────────────▼───────────────┐
         └────────►│            sessions               │
                   ├──────────────────────────────────┤
                   │ session_id  (PK)                  │
                   │ session_date                      │
                   │ page_id     (FK → pages)          │
                   │ source_id   (FK → traffic_sources)│
                   │ campus                            │
                   │ device_type                       │
                   │ duration_sec                      │
                   │ bounced     (0/1)                 │
                   └──────────┬───────────────────────┘
                              │
                   ┌──────────▼───────────┐
                   │        events        │
                   ├──────────────────────┤
                   │ event_id   (PK)      │
                   │ session_id (FK)      │
                   │ event_name           │
                   │ event_date           │
                   └──────────────────────┘
```

---

## Project structure

```
ccri-web-analytics/
├── setup_db.py               # Create schema + seed 8,000 sessions
├── export_dashboard_data.py  # Export query results → dashboard/data.json
├── data/
│   └── analytics.db          # SQLite database (generated)
├── queries/
│   └── example_queries.sql   # 10 annotated analytical queries
└── dashboard/
    ├── index.html            # Standalone HTML dashboard
    └── data.json             # Pre-exported data (generated)
```

---

## Quickstart

**Requirements:** Python 3.8+ (no external packages — stdlib only)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ccri-web-analytics.git
cd ccri-web-analytics

# 2. Create and seed the database
python setup_db.py

# 3. Export data for the dashboard
python export_dashboard_data.py

# 4. Open the dashboard
open dashboard/index.html   # macOS
# or just double-click dashboard/index.html in your file explorer
```

---

## Example queries

See [`queries/example_queries.sql`](queries/example_queries.sql) for 10 queries including:

| # | Query |
|---|-------|
| 1 | Top 10 pages by sessions with bounce rate |
| 2 | Traffic by source / medium |
| 3 | Sessions by device type |
| 4 | Sessions by campus |
| 5 | Weekly session trend (last 12 weeks) |
| 6 | Top conversion events |
| 7 | Admissions funnel page analysis |
| 8 | Site section breakdown |
| 9 | Best organic search pages |
| 10 | High-bounce pages with significant traffic |

Run any query against the DB:

```bash
sqlite3 data/analytics.db < queries/example_queries.sql
```

Or open interactively:

```bash
sqlite3 data/analytics.db
sqlite> .mode column
sqlite> .headers on
sqlite> SELECT * FROM pages LIMIT 5;
```

---

## Dashboard preview

The `dashboard/index.html` file is a self-contained HTML file that reads `data.json` and renders:

- KPI summary cards (sessions, avg duration, bounce rate, events)
- Weekly session trend line chart
- Top pages table with bounce rate indicators
- Traffic source breakdown with medium badges
- Device type doughnut chart
- Campus comparison bar chart
- Top conversion events list
- Site section bar chart

---

## Simulated data details

| Entity | Count |
|--------|-------|
| Pages | 24 (across 7 site sections) |
| Traffic sources | 9 (organic, CPC, social, referral, direct, email) |
| Sessions | 8,000 (over 90 days) |
| Events | ~590 (apply clicks, downloads, form starts, etc.) |
| Campuses | 4 (Knight/Warwick, Flanagan/Lincoln, Liston/Providence, Newport) |

Data distributions are weighted to reflect realistic higher ed web traffic patterns (Google organic dominant, mobile majority, admissions pages high-traffic).

---

## Tools used

- **SQLite** — embedded relational database
- **Python** (`sqlite3`, `json`, `random`, `datetime`) — schema creation, seeding, export
- **Chart.js** — dashboard visualizations
- **HTML/CSS/JS** — dashboard frontend (no framework, no build step)

---

## Next steps / ideas

- Add a `campaigns` table and model UTM parameters
- Write a Python script that imports a real GA4 CSV export
- Add date range filtering to the dashboard with JS
- Try replicating the schema in PostgreSQL
- Connect to a BI tool like Metabase or Grafana

---

*This is a portfolio/learning project. All data is synthetic.*
