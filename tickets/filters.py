from django.db.models import QuerySet


def apply_filters(qs: QuerySet, params, agent) -> QuerySet | list:
    statuses = [s.strip() for s in (params.get("status") or "").split(",") if s.strip()]
    if statuses:
        qs = qs.filter(status__in=statuses)
    else:
        qs = qs.exclude(status="closed")

    if params.get("priority"):
        qs = qs.filter(priority=params["priority"])
    if params.get("mine") == "1":
        qs = qs.filter(assignee=agent)

    qs = qs.order_by("priority", "created_at", "id")

    if params.get("overdue") == "1":
        return [ticket for ticket in qs if ticket.is_overdue()]
    return qs
