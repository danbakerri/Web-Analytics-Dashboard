"""
setup_db.py
Creates and seeds the CCRI Web Analytics SQLite database.
Run this first: python setup_db.py
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "data/analytics.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    page_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    path        TEXT NOT NULL UNIQUE,
    title       TEXT NOT NULL,
    section     TEXT NOT NULL  -- e.g. Academics, Admissions, Financial Aid
);

CREATE TABLE IF NOT EXISTS traffic_sources (
    source_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,  -- e.g. google, direct, bing
    medium      TEXT NOT NULL   -- e.g. organic, cpc, referral, none
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date    TEXT NOT NULL,          -- YYYY-MM-DD
    page_id         INTEGER NOT NULL,
    source_id       INTEGER NOT NULL,
    campus          TEXT NOT NULL,          -- Knight, Flanagan, Liston, Newport
    device_type     TEXT NOT NULL,          -- desktop, mobile, tablet
    duration_sec    INTEGER NOT NULL,       -- session duration in seconds
    bounced         INTEGER NOT NULL,       -- 0 or 1
    FOREIGN KEY (page_id)   REFERENCES pages(page_id),
    FOREIGN KEY (source_id) REFERENCES traffic_sources(source_id)
);

CREATE TABLE IF NOT EXISTS events (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL,
    event_name      TEXT NOT NULL,  -- e.g. apply_click, form_submit, pdf_download
    event_date      TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""

PAGES = [
    ("/",                               "Home",                         "Home"),
    ("/admissions/",                    "Admissions",                   "Admissions"),
    ("/admissions/apply/",              "Apply Now",                    "Admissions"),
    ("/admissions/tuition/",            "Tuition & Fees",               "Admissions"),
    ("/financial-aid/",                 "Financial Aid Overview",       "Financial Aid"),
    ("/financial-aid/fafsa/",           "FAFSA Information",            "Financial Aid"),
    ("/financial-aid/scholarships/",    "Scholarships",                 "Financial Aid"),
    ("/academics/programs/",            "Programs of Study",            "Academics"),
    ("/academics/programs/nursing/",    "Nursing Program",              "Academics"),
    ("/academics/programs/business/",   "Business Administration",      "Academics"),
    ("/academics/programs/it/",         "Information Technology",       "Academics"),
    ("/academics/programs/liberal-arts/","Liberal Arts",                "Academics"),
    ("/academics/programs/culinary/",   "Culinary Arts",                "Academics"),
    ("/academics/schedules/",           "Course Schedules",             "Academics"),
    ("/student-services/",              "Student Services",             "Student Services"),
    ("/student-services/advising/",     "Academic Advising",            "Student Services"),
    ("/student-services/tutoring/",     "Tutoring Center",              "Student Services"),
    ("/about/campuses/",                "Our Campuses",                 "About"),
    ("/about/campuses/knight/",         "Knight Campus – Warwick",      "About"),
    ("/about/campuses/flanagan/",       "Flanagan Campus – Lincoln",    "About"),
    ("/about/campuses/liston/",         "Liston Campus – Providence",   "About"),
    ("/about/campuses/newport/",        "Newport County Campus",        "About"),
    ("/workforce-development/",         "Workforce Development",        "Workforce"),
    ("/contact/",                       "Contact Us",                   "About"),
]

SOURCES = [
    ("google",      "organic"),
    ("google",      "cpc"),
    ("bing",        "organic"),
    ("direct",      "none"),
    ("facebook",    "social"),
    ("ri.gov",      "referral"),
    ("niche.com",   "referral"),
    ("collegeboard","referral"),
    ("email",       "email"),
]

CAMPUSES     = ["Knight", "Flanagan", "Liston", "Newport"]
DEVICES      = ["desktop", "mobile", "tablet"]
DEVICE_WEIGHTS = [0.45, 0.48, 0.07]

EVENTS_BY_PAGE = {
    "/admissions/apply/":           ["apply_click", "apply_click", "form_start"],
    "/financial-aid/fafsa/":        ["pdf_download", "external_link_click"],
    "/financial-aid/scholarships/": ["pdf_download", "apply_click"],
    "/academics/programs/nursing/": ["apply_click", "pdf_download", "info_request"],
    "/academics/programs/it/":      ["apply_click", "pdf_download"],
    "/student-services/advising/":  ["appointment_click", "phone_click"],
    "/contact/":                    ["phone_click", "email_click", "map_click"],
}

SOURCE_WEIGHTS = [0.38, 0.08, 0.10, 0.22, 0.07, 0.05, 0.04, 0.03, 0.03]

PAGE_WEIGHTS = [
    0.14, 0.09, 0.08, 0.06,
    0.07, 0.05, 0.03,
    0.06, 0.06, 0.04, 0.03, 0.02, 0.02, 0.03,
    0.04, 0.03, 0.02,
    0.02, 0.02, 0.01, 0.01, 0.01,
    0.02, 0.03,
]


def seed(conn, num_sessions=8000, days=90):
    c = conn.cursor()

    # Insert pages
    for path, title, section in PAGES:
        c.execute("INSERT OR IGNORE INTO pages (path, title, section) VALUES (?,?,?)",
                  (path, title, section))

    # Insert sources
    for source, medium in SOURCES:
        c.execute("INSERT OR IGNORE INTO traffic_sources (source, medium) VALUES (?,?)",
                  (source, medium))

    conn.commit()

    page_ids   = [r[0] for r in c.execute("SELECT page_id FROM pages ORDER BY page_id").fetchall()]
    source_ids = [r[0] for r in c.execute("SELECT source_id FROM traffic_sources ORDER BY source_id").fetchall()]
    page_paths = [r[0] for r in c.execute("SELECT path FROM pages ORDER BY page_id").fetchall()]

    end_date   = datetime.today()
    start_date = end_date - timedelta(days=days)

    sessions_data = []
    events_data   = []

    for _ in range(num_sessions):
        delta      = random.random() * days
        sess_date  = (start_date + timedelta(days=delta)).strftime("%Y-%m-%d")
        page_idx   = random.choices(range(len(page_ids)), weights=PAGE_WEIGHTS)[0]
        page_id    = page_ids[page_idx]
        page_path  = page_paths[page_idx]
        source_id  = random.choices(source_ids, weights=SOURCE_WEIGHTS)[0]
        campus     = random.choice(CAMPUSES)
        device     = random.choices(DEVICES, weights=DEVICE_WEIGHTS)[0]
        duration   = max(5, int(random.gauss(180, 120)))
        bounced    = 1 if duration < 30 or random.random() < 0.35 else 0

        sessions_data.append((sess_date, page_id, source_id, campus, device, duration, bounced))

        # Maybe fire an event
        if page_path in EVENTS_BY_PAGE and random.random() < 0.25:
            event_name = random.choice(EVENTS_BY_PAGE[page_path])
            events_data.append((len(sessions_data), event_name, sess_date))

    c.executemany(
        "INSERT INTO sessions (session_date, page_id, source_id, campus, device_type, duration_sec, bounced) VALUES (?,?,?,?,?,?,?)",
        sessions_data
    )

    # Re-fetch real session IDs for events
    conn.commit()
    real_session_ids = [r[0] for r in c.execute("SELECT session_id FROM sessions ORDER BY session_id").fetchall()]

    final_events = []
    for i, (_, event_name, event_date) in enumerate(events_data):
        if i < len(real_session_ids):
            final_events.append((real_session_ids[i], event_name, event_date))

    c.executemany(
        "INSERT INTO events (session_id, event_name, event_date) VALUES (?,?,?)",
        final_events
    )

    conn.commit()
    print(f"✅ Seeded {num_sessions} sessions and {len(final_events)} events over {days} days.")


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    seed(conn)
    conn.close()
    print(f"Database created at {DB_PATH}")
