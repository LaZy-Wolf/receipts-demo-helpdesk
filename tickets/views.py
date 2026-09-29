import csv
import json
from functools import wraps

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from . import sla
from .assignment import next_agent
from .filters import apply_filters
from .models import Agent, Comment, Ticket
from .serializers import iso as _iso
from .serializers import ticket_json


def api(*methods):
    """JSON endpoint: logged-in agent only, allowed methods only, parsed JSON body on request.data."""
    def decorator(view):
        @csrf_exempt
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"detail": "authentication required"}, status=401)
            try:
                request.agent = request.user.agent
            except Agent.DoesNotExist:
                return JsonResponse({"detail": "only agents can use the API"}, status=403)
            if request.method not in methods:
                return JsonResponse({"detail": "method not allowed"}, status=405)
            request.data = {}
            if request.body and request.content_type == "application/json":
                try:
                    request.data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({"detail": "invalid JSON"}, status=400)
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def team_tickets(request):
    return Ticket.objects.filter(team=request.agent.team).select_related("assignee__user")


@api("GET", "POST")
def tickets(request):
    if request.method == "GET":
        found = apply_filters(team_tickets(request), request.GET, request.agent)
        return JsonResponse({"results": [ticket_json(t) for t in found]})

    data = request.data
    missing = [f for f in ("subject", "requester_email") if not data.get(f)]
    if missing:
        return JsonResponse({"detail": f"missing fields: {', '.join(missing)}"}, status=400)
    priority = data.get("priority", "medium")
    if priority not in sla.SLA_HOURS:
        return JsonResponse({"detail": f"unknown priority {priority!r}"}, status=400)
    team = request.agent.team
    now = timezone.now()
    ticket = Ticket.objects.create(
        team=team,
        subject=data["subject"],
        body=data.get("body", ""),
        requester_email=data["requester_email"],
        priority=priority,
        created_at=now,
        due_at=sla.due_at(team, priority, now),
        assignee=next_agent(team),
    )
    return JsonResponse(ticket_json(ticket), status=201)


@api("GET")
def ticket_detail(request, pk):
    ticket = get_object_or_404(team_tickets(request), pk=pk)
    return JsonResponse(ticket_json(ticket, with_comments=True))


@api("POST")
def add_comment(request, pk):
    ticket = get_object_or_404(team_tickets(request), pk=pk)
    body = (request.data.get("body") or "").strip()
    if not body:
        return JsonResponse({"detail": "comment body is required"}, status=400)
    Comment.objects.create(ticket=ticket, author=request.user, body=body, internal=bool(request.data.get("internal")))
    return JsonResponse(ticket_json(ticket, with_comments=True), status=201)


@api("POST")
def close_ticket(request, pk):
    ticket = get_object_or_404(team_tickets(request), pk=pk)
    if ticket.status == "closed":
        return JsonResponse({"detail": "ticket is already closed"}, status=409)
    ticket.status = "closed"
    ticket.closed_at = timezone.now()
    ticket.save(update_fields=["status", "closed_at"])
    return JsonResponse(ticket_json(ticket))


@api("POST")
def reopen_ticket(request, pk):
    ticket = get_object_or_404(team_tickets(request), pk=pk)
    if ticket.status != "closed":
        return JsonResponse({"detail": "only closed tickets can be reopened"}, status=409)
    ticket.status = "open"
    ticket.save(update_fields=["status"])
    return JsonResponse(ticket_json(ticket))


@api("GET")
def export_csv(request):
    found = apply_filters(Ticket.objects.select_related("assignee__user"), request.GET, request.agent)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="tickets.csv"'
    writer = csv.writer(response)
    writer.writerow(["id", "subject", "priority", "status", "assignee", "created_at", "due_at"])
    for t in found:
        writer.writerow([t.pk, t.subject, t.priority, t.status, t.assignee.user.username if t.assignee else "",
                         _iso(t.created_at), _iso(t.due_at)])
    return response
