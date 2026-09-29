from django.db.models import QuerySet


def apply_filters(qs: QuerySet, params, agent) -> QuerySet | list:
    status = params.get("status")
    if status and status != "all":
        qs = qs.filter(status=status.split(",")[0])
    elif not status:
        qs = qs.exclude(status="closed")

    if params.get("priority"):
        qs = qs.filter(priority=params["priority"])
    if params.get("mine") == "1":
        qs = qs.filter(assignee=agent)

    qs = qs.order_by("-priority", "created_at", "id")

    if params.get("overdue") == "1":
        return [ticket for ticket in qs if ticket.is_overdue()]
    return qs
