"""
export_dashboard_data.py
Queries the analytics DB and writes JSON for the HTML dashboard.
Run: python export_dashboard_data.py
"""

import sqlite3
import json
import os

DB_PATH   = "data/analytics.db"
OUT_PATH  = "dashboard/data.json"


def query(conn, sql):
    c = conn.cursor()
    c.execute(sql)
    cols = [d[0] for d in c.description]
    return [dict(zip(cols, row)) for row in c.fetchall()]


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}. Run setup_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)

    data = {}

    # KPI totals
    kpis = conn.execute("""
        SELECT
            COUNT(*)                                        AS total_sessions,
            ROUND(AVG(duration_sec))                        AS avg_duration_sec,
            ROUND(100.0 * SUM(bounced) / COUNT(*), 1)       AS bounce_rate_pct,
            (SELECT COUNT(*) FROM events)                   AS total_events
        FROM sessions
    """).fetchone()
    data["kpis"] = {
        "total_sessions":   kpis[0],
        "avg_duration_sec": kpis[1],
        "bounce_rate_pct":  kpis[2],
        "total_events":     kpis[3],
    }

    # Top pages
    data["top_pages"] = query(conn, """
        SELECT p.title, p.path, p.section,
               COUNT(s.session_id) AS sessions,
               ROUND(100.0 * SUM(s.bounced) / COUNT(*), 1) AS bounce_rate_pct
        FROM sessions s JOIN pages p ON s.page_id = p.page_id
        GROUP BY p.page_id ORDER BY sessions DESC LIMIT 8
    """)

    # Traffic sources
    data["sources"] = query(conn, """
        SELECT ts.source, ts.medium, COUNT(s.session_id) AS sessions
        FROM sessions s JOIN traffic_sources ts ON s.source_id = ts.source_id
        GROUP BY ts.source_id ORDER BY sessions DESC
    """)

    # Device split
    data["devices"] = query(conn, """
        SELECT device_type, COUNT(*) AS sessions
        FROM sessions GROUP BY device_type ORDER BY sessions DESC
    """)

    # Campus split
    data["campuses"] = query(conn, """
        SELECT campus, COUNT(*) AS sessions,
               ROUND(AVG(duration_sec)) AS avg_duration_sec
        FROM sessions GROUP BY campus ORDER BY sessions DESC
    """)

    # Weekly trend (last 12 weeks)
    data["weekly_trend"] = query(conn, """
        SELECT strftime('%Y-W%W', session_date) AS week, COUNT(*) AS sessions
        FROM sessions WHERE session_date >= date('now', '-84 days')
        GROUP BY week ORDER BY week
    """)

    # Top events
    data["events"] = query(conn, """
        SELECT event_name, COUNT(*) AS total_fires
        FROM events GROUP BY event_name ORDER BY total_fires DESC
    """)

    # Section breakdown
    data["sections"] = query(conn, """
        SELECT p.section, COUNT(s.session_id) AS sessions,
               ROUND(100.0 * SUM(s.bounced) / COUNT(*), 1) AS bounce_rate_pct
        FROM sessions s JOIN pages p ON s.page_id = p.page_id
        GROUP BY p.section ORDER BY sessions DESC
    """)

    conn.close()

    os.makedirs("dashboard", exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Dashboard data exported to {OUT_PATH}")


if __name__ == "__main__":
    main()
