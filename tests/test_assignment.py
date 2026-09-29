from tests.conftest import make_agent
from tickets.assignment import next_agent


def test_assigns_an_available_agent(team, alice):
    assert next_agent(team) == alice


def test_none_when_nobody_available(team):
    make_agent(team, "zoe", available=False)
    assert next_agent(team) is None


def test_skips_unavailable_agents(team, alice):
    bob = make_agent(team, "bob", available=False)
    picked = {next_agent(team) for _ in range(4)}
    assert bob not in picked


def test_only_team_members(team, other_team, alice):
    outsider = make_agent(other_team, "oscar")
    assert all(next_agent(team) != outsider for _ in range(3))
