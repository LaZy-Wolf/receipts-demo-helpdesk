"""Round-robin assignment of new tickets."""
from .models import Agent, Team


def next_agent(team: Team) -> Agent | None:
    """Pick the next available agent of `team` in round-robin order, skipping unavailable agents."""
    agents = list(team.agents.order_by("id"))
    if not any(agent.available for agent in agents):
        return None
    for step in range(len(agents)):
        candidate = agents[(team.rr_cursor + step) % len(agents)]
        if candidate.available:
            team.rr_cursor = (team.rr_cursor + 1) % len(agents)
            team.save(update_fields=["rr_cursor"])
            return candidate
    return None
