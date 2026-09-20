from datetime import datetime, timezone

def now_ts():
    return datetime.now(timezone.utc).astimezone().isoformat()

def short_date(iso_ts):
    if not iso_ts:
        return "<unknown>"
    try:
        dt = datetime.fromisoformat(iso_ts)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_ts
