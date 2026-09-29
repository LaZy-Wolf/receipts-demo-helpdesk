from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone

from tickets.models import Agent, Team, Ticket


@pytest.fixture(autouse=True)
def _db(db):
    pass


@pytest.fixture
def team():
    return Team.objects.create(name="Support")


@pytest.fixture
def other_team():
    return Team.objects.create(name="Billing")


def make_agent(team, username, available=True):
    user = User.objects.create_user(username=username, password="x")
    return Agent.objects.create(user=user, team=team, available=available)


@pytest.fixture
def alice(team):
    return make_agent(team, "alice")


@pytest.fixture
def api(alice):
    client = Client()
    client.force_login(alice.user)
    return client


@pytest.fixture
def make_ticket(team):
    def make(**fields):
        fields.setdefault("team", team)
        fields.setdefault("subject", "Printer on fire")
        fields.setdefault("requester_email", "someone@example.com")
        fields.setdefault("due_at", timezone.now() + timedelta(days=1))
        return Ticket.objects.create(**fields)
    return make
