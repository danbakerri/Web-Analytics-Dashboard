-- =============================================================
-- CCRI Web Analytics — Example Queries
-- Run against data/analytics.db
-- =============================================================

-- ── 1. Top 10 pages by sessions ──────────────────────────────
SELECT
    p.title,
    p.path,
    p.section,
    COUNT(s.session_id)                             AS sessions,
    ROUND(AVG(s.duration_sec))                      AS avg_duration_sec,
    ROUND(100.0 * SUM(s.bounced) / COUNT(*), 1)     AS bounce_rate_pct
FROM sessions s
JOIN pages p ON s.page_id = p.page_id
GROUP BY p.page_id
ORDER BY sessions DESC
LIMIT 10;


-- ── 2. Traffic by source / medium ────────────────────────────
SELECT
    ts.source,
    ts.medium,
    COUNT(s.session_id)                             AS sessions,
    ROUND(100.0 * SUM(s.bounced) / COUNT(*), 1)     AS bounce_rate_pct,
    ROUND(AVG(s.duration_sec))                      AS avg_duration_sec
FROM sessions s
JOIN traffic_sources ts ON s.source_id = ts.source_id
GROUP BY ts.source_id
ORDER BY sessions DESC;


-- ── 3. Sessions by device type ───────────────────────────────
SELECT
    device_type,
    COUNT(*)                                        AS sessions,
    ROUND(100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM sessions), 1)         AS pct_of_total
FROM sessions
GROUP BY device_type
ORDER BY sessions DESC;


-- ── 4. Sessions by campus ────────────────────────────────────
SELECT
    campus,
    COUNT(*)                                        AS sessions,
    ROUND(100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM sessions), 1)         AS pct_of_total,
    ROUND(AVG(duration_sec))                        AS avg_duration_sec
FROM sessions
GROUP BY campus
ORDER BY sessions DESC;


-- ── 5. Weekly session trend (last 12 weeks) ──────────────────
SELECT
    strftime('%Y-W%W', session_date)                AS week,
    COUNT(*)                                        AS sessions
FROM sessions
WHERE session_date >= date('now', '-84 days')
GROUP BY week
ORDER BY week;


-- ── 6. Top conversion events ─────────────────────────────────
SELECT
    e.event_name,
    COUNT(*)                                        AS total_fires,
    COUNT(DISTINCT e.session_id)                    AS unique_sessions
FROM events e
GROUP BY e.event_name
ORDER BY total_fires DESC;


-- ── 7. Admissions funnel ─────────────────────────────────────
--   How many sessions hit key admissions pages?
SELECT
    p.title,
    p.path,
    COUNT(s.session_id)                             AS sessions
FROM sessions s
JOIN pages p ON s.page_id = p.page_id
WHERE p.section = 'Admissions'
GROUP BY p.page_id
ORDER BY sessions DESC;


-- ── 8. Top pages by section ──────────────────────────────────
SELECT
    p.section,
    COUNT(s.session_id)                             AS sessions,
    ROUND(100.0 * SUM(s.bounced) / COUNT(*), 1)     AS bounce_rate_pct
FROM sessions s
JOIN pages p ON s.page_id = p.page_id
GROUP BY p.section
ORDER BY sessions DESC;


-- ── 9. Best organic search pages ─────────────────────────────
SELECT
    p.title,
    p.path,
    COUNT(s.session_id)                             AS organic_sessions
FROM sessions s
JOIN pages p ON s.page_id = p.page_id
JOIN traffic_sources ts ON s.source_id = ts.source_id
WHERE ts.medium = 'organic'
GROUP BY p.page_id
ORDER BY organic_sessions DESC
LIMIT 10;


-- ── 10. High-bounce pages with decent traffic ─────────────────
--   Pages that may need content/UX work
SELECT
    p.title,
    p.path,
    COUNT(*)                                        AS sessions,
    ROUND(100.0 * SUM(s.bounced) / COUNT(*), 1)     AS bounce_rate_pct,
    ROUND(AVG(s.duration_sec))                      AS avg_duration_sec
FROM sessions s
JOIN pages p ON s.page_id = p.page_id
GROUP BY p.page_id
HAVING sessions > 100 AND bounce_rate_pct > 50
ORDER BY bounce_rate_pct DESC;
