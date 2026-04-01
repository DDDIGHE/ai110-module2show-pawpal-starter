"""PawPal+ logic layer — class skeletons based on UML diagram."""

from dataclasses import dataclass, field

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Pet:
    name: str
    species: str  # "dog", "cat", "other"

    def summary(self) -> str:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pet: Pet
    preferences: list[str] = field(default_factory=list)

    def summary(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str = "general"  # walk, feed, meds, groom, enrichment
    is_required: bool = False


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[Task] = []
        self.total_time_used: int = 0

    def generate_plan(self, tasks: list[Task]) -> list[Task]:
        """Select and order tasks within the owner's time budget."""
        pass

    def explain_plan(self) -> str:
        """Return human-readable reasoning for the generated plan."""
        pass
