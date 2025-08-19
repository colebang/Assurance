from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

from underwriting.models import Policy
from complaints.models import Complaint
from claims.models import Claim

PERIOD_MAP = {
    "day": TruncDay,
    "week": TruncWeek,
    "month": TruncMonth,
}


def counters():
    today = timezone.localdate()
    return {
        "policies_today": Policy.objects.filter(created_at__date=today).count(),
        "complaints_today": Complaint.objects.filter(filed_at__date=today).count(),
        "claims_submitted_today": Claim.objects.filter(declared_at__date=today).count(),
        "claims_approved_today": Claim.objects.filter(approved_at__date=today).count(),
    }


def parse_dates(date_from, date_to):
    if date_from:
        start = date.fromisoformat(date_from)
    else:
        start = timezone.localdate() - timedelta(days=30)
    if date_to:
        end = date.fromisoformat(date_to)
    else:
        end = timezone.localdate()
    return start, end


def policies_series(date_from=None, date_to=None, period="day"):
    start, end = parse_dates(date_from, date_to)
    truncate = PERIOD_MAP.get(period, TruncDay)
    qs = Policy.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
    data = (
        qs.annotate(bucket=truncate("created_at"))
        .values("bucket")
        .annotate(count=Count("id"))
        .order_by("bucket")
    )
    labels = [d["bucket"].date().isoformat() for d in data]
    counts = [d["count"] for d in data]
    return {"labels": labels, "datasets": [{"label": "Policies", "data": counts}]}


def claims_status_series(date_from=None, date_to=None):
    start, end = parse_dates(date_from, date_to)
    qs = Claim.objects.filter(declared_at__date__gte=start, declared_at__date__lte=end)
    data = qs.values("status").annotate(count=Count("id"))
    labels = [d["status"] for d in data]
    counts = [d["count"] for d in data]
    return {"labels": labels, "datasets": [{"label": "Claims", "data": counts}]}


def series(metric, date_from=None, date_to=None, period="day"):
    if metric == "policies":
        return policies_series(date_from, date_to, period)
    if metric == "claims_status":
        return claims_status_series(date_from, date_to)
    return {"labels": [], "datasets": []}
