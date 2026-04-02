"""PawPal+ logic layer — full implementation."""

from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}
TIME_SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str = "general"  # walk, feed, meds, groom, enrichment
    is_required: bool = False
    frequency: str = "daily"  # daily, weekly, as_needed
    preferred_time: str = "anytime"  # morning, afternoon, evening, anytime
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def __post_init__(self):
        """Normalize priority to lowercase and validate against PRIORITY_WEIGHT."""
        self.priority = self.priority.lower()
        if self.priority not in PRIORITY_WEIGHT:
            raise ValueError(f"priority must be one of {list(PRIORITY_WEIGHT)}, got '{self.priority}'")

    def mark_done(self):
        """Mark this task as completed."""
        self.completed = True

    def reset(self):
        """Reset this task to incomplete."""
        self.completed = False

    def next_occurrence(self) -> "Task | None":
        """Create next occurrence for recurring tasks. Returns None for as_needed."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title, duration_minutes=self.duration_minutes,
            priority=self.priority, category=self.category,
            is_required=self.is_required, frequency=self.frequency,
            preferred_time=self.preferred_time, due_date=self.due_date + delta,
        )


@dataclass
class Pet:
    name: str
    species: str  # "dog", "cat", "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove first task matching title; return True if found."""
        for i, t in enumerate(self.tasks):
            if t.title == title:
                self.tasks.pop(i)
                return True
        return False

    def pending_tasks(self) -> list[Task]:
        """Return tasks not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def summary(self) -> str:
        """Return a short description of this pet."""
        return f"{self.name} ({self.species}, {len(self.tasks)} tasks)"


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def all_pending_tasks(self) -> list[Task]:
        """Collect pending tasks across all pets."""
        result = []
        for pet in self.pets:
            result.extend(pet.pending_tasks())
        return result

    def summary(self) -> str:
        """Return a short description of this owner and their pets."""
        pet_names = ", ".join(p.name for p in self.pets) or "no pets"
        return f"{self.name} ({self.available_minutes} min available, pets: {pet_names})"


class Scheduler:
    """The brain: gathers tasks from Owner's pets, schedules by priority within time budget."""

    def __init__(self, owner: Owner):
        if owner.available_minutes <= 0:
            raise ValueError("available_minutes must be positive")
        self.owner = owner
        self.plan: list[Task] = []
        self.skipped: list[Task] = []
        self.total_time_used: int = 0

    def complete_task(self, task: Task, pet: Pet) -> Task | None:
        """Mark task done and auto-create next occurrence for recurring tasks."""
        task.mark_done()
        next_task = task.next_occurrence()
        if next_task:
            pet.add_task(next_task)
        return next_task

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[Task]:
        """Filter owner's tasks by completion status and/or pet name."""
        results = []
        for pet in self.owner.pets:
            if pet_name and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def generate_plan(self, tasks: list[Task] | None = None) -> list[Task]:
        """Greedy schedule: required first, then by priority, until time runs out.
        If tasks not provided, pulls pending tasks from owner's pets."""
        self.plan = []
        self.skipped = []
        self.total_time_used = 0
        budget = self.owner.available_minutes

        if tasks is None:
            tasks = self.owner.all_pending_tasks()

        # Split and sort by priority descending
        required = sorted([t for t in tasks if t.is_required],
                          key=lambda t: PRIORITY_WEIGHT[t.priority], reverse=True)
        optional = sorted([t for t in tasks if not t.is_required],
                          key=lambda t: PRIORITY_WEIGHT[t.priority], reverse=True)

        # Required always go in
        for task in required:
            self.plan.append(task)
            self.total_time_used += task.duration_minutes

        # Optional fill remaining time
        for task in optional:
            if self.total_time_used + task.duration_minutes <= budget:
                self.plan.append(task)
                self.total_time_used += task.duration_minutes
            else:
                self.skipped.append(task)

        return self.plan

    def detect_conflicts(self) -> list[str]:
        """Check for scheduling conflicts: duplicate titles or overfilled time slots."""
        warnings = []
        # Group scheduled tasks by time slot
        slots: dict[str, list[Task]] = {}
        for task in self.plan:
            slots.setdefault(task.preferred_time, []).append(task)

        for slot, tasks in slots.items():
            # Duplicate titles in same slot
            titles = [t.title for t in tasks]
            seen = set()
            for title in titles:
                if title in seen:
                    warnings.append(f"Conflict: '{title}' appears more than once in {slot} slot")
                seen.add(title)

            # Slot overload (same category competing for same time)
            categories: dict[str, list[str]] = {}
            for t in tasks:
                categories.setdefault(t.category, []).append(t.title)
            for cat, cat_titles in categories.items():
                if len(cat_titles) > 1:
                    warnings.append(
                        f"Conflict: multiple {cat} tasks in {slot} slot: {', '.join(cat_titles)}")

        return warnings

    def sort_by_time(self) -> list[Task]:
        """Reorder the plan by preferred time slot (morning → afternoon → evening → anytime)."""
        self.plan.sort(key=lambda t: TIME_SLOT_ORDER.get(t.preferred_time, 3))
        return self.plan

    def explain_plan(self) -> str:
        """Human-readable plan with reasoning."""
        if not self.plan:
            return "No tasks scheduled. Add tasks to your pets first."

        lines = [f"Plan for {self.owner.name} "
                 f"(budget: {self.owner.available_minutes} min)\n"]

        elapsed = 0
        for i, task in enumerate(self.plan, 1):
            tag = "REQUIRED" if task.is_required else task.priority
            lines.append(f"  {i}. {task.title} — {task.duration_minutes} min [{tag}] "
                         f"(starts +{elapsed} min)")
            elapsed += task.duration_minutes

        lines.append(f"\nTotal: {self.total_time_used} / {self.owner.available_minutes} min")

        if self.skipped:
            lines.append("\nSkipped (not enough time):")
            for task in self.skipped:
                lines.append(f"  - {task.title} ({task.duration_minutes} min, {task.priority})")

        req_time = sum(t.duration_minutes for t in self.plan if t.is_required)
        if req_time > self.owner.available_minutes:
            lines.append(f"\nWarning: required tasks need {req_time} min, "
                         f"exceeding {self.owner.available_minutes} min budget.")

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\nConflicts detected:")
            for warning in conflicts:
                lines.append(f"  ! {warning}")

        return "\n".join(lines)
