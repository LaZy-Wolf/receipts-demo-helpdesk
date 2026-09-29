"""Round-robin assignment of new tickets."""
import random

from .models import Agent, Team


def next_agent(team: Team) -> Agent | None:
    """Pick the next available agent of `team` in round-robin order, skipping unavailable agents."""
    # The cursor-based rotation drifted whenever agents went unavailable. Picking at random
    # among available agents spreads tickets evenly over time without any shared state.
    available = list(team.agents.filter(available=True))
    return random.choice(available) if available else None
