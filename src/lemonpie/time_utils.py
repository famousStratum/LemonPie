from datetime import UTC, datetime


def now_ts():
    return datetime.now(UTC).astimezone().isoformat()

def short_date(iso_ts):
    if not iso_ts:
        return "<unknown>"
    try:
        dt: datetime = datetime.fromisoformat(iso_ts)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_ts
