"""
Recurrence engine — computes next occurrence dates for recurring tasks,
and streak logic for habits.

Recurrence rule format (simple, JSON-string stored in DB):
    {"freq": "daily"}                       -> every day
    {"freq": "weekly", "days": [0,2,4]}      -> Mon, Wed, Fri (0=Mon)
    {"freq": "monthly", "day_of_month": 15}  -> 15th every month
    {"freq": "custom", "every_n_days": 3}    -> every 3 days
"""
import json
from datetime import datetime, timedelta, date


def compute_next_occurrence(rule_json: str, from_date: date = None) -> str:
    if not rule_json:
        return None
    rule = json.loads(rule_json)
    from_date = from_date or date.today()
    freq = rule.get("freq")

    if freq == "daily":
        nxt = from_date + timedelta(days=1)

    elif freq == "weekly":
        target_days = rule.get("days", [from_date.weekday()])
        nxt = from_date + timedelta(days=1)
        for _ in range(8):
            if nxt.weekday() in target_days:
                break
            nxt += timedelta(days=1)

    elif freq == "monthly":
        day_of_month = rule.get("day_of_month", from_date.day)
        month = from_date.month + 1
        year = from_date.year + (1 if month > 12 else 0)
        month = 1 if month > 12 else month
        try:
            nxt = date(year, month, day_of_month)
        except ValueError:
            # clamp to last valid day of month
            next_month_first = date(year, month, 1)
            following = next_month_first.replace(day=28) + timedelta(days=4)
            last_day = (following - timedelta(days=following.day)).day
            nxt = date(year, month, min(day_of_month, last_day))

    elif freq == "custom":
        every_n = rule.get("every_n_days", 1)
        nxt = from_date + timedelta(days=every_n)

    else:
        return None

    return nxt.isoformat()


def calculate_streak(logged_dates: list, frequency: str = "daily") -> dict:
    """
    Given a sorted list of ISO date strings a habit was logged on,
    returns current streak and longest streak.
    """
    if not logged_dates:
        return {"current_streak": 0, "longest_streak": 0}

    dates = sorted({datetime.fromisoformat(d).date() for d in logged_dates})

    longest = 1
    current = 1
    streaks = [1]

    for i in range(1, len(dates)):
        gap = (dates[i] - dates[i - 1]).days
        expected_gap = 7 if frequency == "weekly" else 1
        if gap == expected_gap:
            streaks[-1] += 1
        else:
            streaks.append(1)

    longest = max(streaks)

    # current streak only counts if the last logged date is today or
    # within the expected gap window from today
    today = date.today()
    expected_gap = 7 if frequency == "weekly" else 1
    if (today - dates[-1]).days <= expected_gap:
        current = streaks[-1]
    else:
        current = 0

    return {"current_streak": current, "longest_streak": longest}
