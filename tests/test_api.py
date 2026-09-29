import csv
import io
from datetime import timedelta

from django.test import Client
from django.utils import timezone

from tests.conftest import make_agent


def test_requires_login(team):
    assert Client().get("/api/tickets/").status_code == 401


def test_create_ticket(api, alice):
    resp = api.post("/api/tickets/", {"subject": "VPN down", "requester_email": "a@b.co", "priority": "high"},
                    content_type="application/json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["assignee"] == "alice"
    assert body["due_at"] is not None
    assert body["status"] == "open"


def test_create_requires_fields(api):
    resp = api.post("/api/tickets/", {"subject": "x"}, content_type="application/json")
    assert resp.status_code == 400


def test_unknown_priority(api):
    resp = api.post("/api/tickets/", {"subject": "x", "requester_email": "a@b.co", "priority": "meh"},
                    content_type="application/json")
    assert resp.status_code == 400


def test_list_hides_closed_by_default(api, make_ticket):
    make_ticket(subject="open one")
    make_ticket(subject="closed one", status="closed")
    subjects = [t["subject"] for t in api.get("/api/tickets/").json()["results"]]
    assert subjects == ["open one"]


def test_status_filter(api, make_ticket):
    make_ticket(subject="a", status="pending")
    make_ticket(subject="b", status="open")
    subjects = [t["subject"] for t in api.get("/api/tickets/", {"status": "pending"}).json()["results"]]
    assert subjects == ["a"]


def test_status_all_includes_closed(api, make_ticket):
    make_ticket(subject="a")
    make_ticket(subject="b", status="closed")
    assert len(api.get("/api/tickets/", {"status": "all"}).json()["results"]) == 2


def test_oldest_first_within_priority(api, make_ticket):
    now = timezone.now()
    make_ticket(subject="newer", created_at=now)
    make_ticket(subject="older", created_at=now - timedelta(hours=2))
    subjects = [t["subject"] for t in api.get("/api/tickets/").json()["results"]]
    assert subjects == ["older", "newer"]


def test_mine_filter(api, team, alice, make_ticket):
    bob = make_agent(team, "bob")
    make_ticket(subject="mine", assignee=alice)
    make_ticket(subject="bobs", assignee=bob)
    subjects = [t["subject"] for t in api.get("/api/tickets/", {"mine": "1"}).json()["results"]]
    assert subjects == ["mine"]


def test_other_team_hidden(api, other_team, make_ticket):
    make_ticket(subject="theirs", team=other_team)
    assert api.get("/api/tickets/").json()["results"] == []


def test_detail_other_team_404(api, other_team, make_ticket):
    ticket = make_ticket(team=other_team)
    assert api.get(f"/api/tickets/{ticket.pk}/").status_code == 404


def test_comment(api, make_ticket):
    ticket = make_ticket()
    resp = api.post(f"/api/tickets/{ticket.pk}/comments/", {"body": "On it"}, content_type="application/json")
    assert resp.status_code == 201
    assert resp.json()["comments"][0]["body"] == "On it"


def test_close(api, make_ticket):
    ticket = make_ticket()
    body = api.post(f"/api/tickets/{ticket.pk}/close/").json()
    assert body["status"] == "closed"
    assert body["closed_at"] is not None


def test_reopen_sets_open(api, make_ticket):
    ticket = make_ticket(status="closed", closed_at=timezone.now())
    assert api.post(f"/api/tickets/{ticket.pk}/reopen/").json()["status"] == "open"


def test_reopen_requires_closed(api, make_ticket):
    ticket = make_ticket()
    assert api.post(f"/api/tickets/{ticket.pk}/reopen/").status_code == 409


def test_export_csv(api, alice, make_ticket):
    make_ticket(subject="Printer", assignee=alice)
    rows = list(csv.reader(io.StringIO(api.get("/api/tickets/export.csv").content.decode())))
    assert rows[0][:2] == ["id", "subject"]
    assert rows[1][1] == "Printer"


def test_wrong_method(api):
    assert api.delete("/api/tickets/").status_code == 405
