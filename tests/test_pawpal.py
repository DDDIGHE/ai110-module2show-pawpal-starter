"""Tests for PawPal+ core logic."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Pet, Owner, Task, Scheduler


# ===== Existing tests =====

def test_task_completion():
    """mark_done() should flip completed from False to True."""
    task = Task("Morning walk", 30, "high", "walk")
    assert task.completed is False
    task.mark_done()
    assert task.completed is True


def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task list length."""
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feed dinner", 10, "high", "feed"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Evening walk", 25, "medium", "walk"))
    assert len(pet.tasks) == 2


# ===== Sorting correctness =====

def test_sort_by_time_ordering():
    """Tasks added out of order should be sorted morning → afternoon → evening."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Evening walk", 25, "high", "walk", preferred_time="evening"))
    pet.add_task(Task("Grooming", 20, "medium", "groom", preferred_time="afternoon"))
    pet.add_task(Task("Morning walk", 30, "high", "walk", preferred_time="morning"))

    owner = Owner("Jordan", 120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    scheduler.sort_by_time()

    slots = [t.preferred_time for t in scheduler.plan]
    assert slots == ["morning", "afternoon", "evening"]


def test_sort_stable_within_slot():
    """Tasks in the same time slot should keep priority order (stable sort)."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Give meds", 5, "high", "meds", preferred_time="morning"))
    pet.add_task(Task("Casual walk", 15, "low", "walk", preferred_time="morning"))

    owner = Owner("Jordan", 60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    scheduler.sort_by_time()

    # High priority "Give meds" should come before low priority "Casual walk"
    assert scheduler.plan[0].title == "Give meds"
    assert scheduler.plan[1].title == "Casual walk"


def test_sort_all_anytime():
    """When all tasks are 'anytime', sort_by_time should not change priority order."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Low task", 10, "low", "general"))
    pet.add_task(Task("High task", 10, "high", "general"))

    owner = Owner("Jordan", 60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()  # high first by priority
    original_order = [t.title for t in scheduler.plan]
    scheduler.sort_by_time()
    assert [t.title for t in scheduler.plan] == original_order


# ===== Recurrence logic =====

def test_recurring_daily():
    """Completing a daily task should create next occurrence due tomorrow."""
    today = date.today()
    pet = Pet("Mochi", "dog")
    task = Task("Morning walk", 30, "high", "walk", frequency="daily", due_date=today)
    pet.add_task(task)

    owner = Owner("Jordan", 60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    next_task = scheduler.complete_task(task, pet)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert len(pet.tasks) == 2  # original + new


def test_recurring_weekly():
    """Completing a weekly task should create next occurrence due in 7 days."""
    today = date.today()
    pet = Pet("Bella", "cat")
    task = Task("Grooming", 20, "medium", "groom", frequency="weekly", due_date=today)
    pet.add_task(task)

    owner = Owner("Jordan", 60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    next_task = scheduler.complete_task(task, pet)

    assert next_task.due_date == today + timedelta(weeks=1)


def test_recurring_as_needed_no_repeat():
    """Completing an as_needed task should not create a next occurrence."""
    pet = Pet("Bella", "cat")
    task = Task("Vet visit", 60, "high", "general", frequency="as_needed")
    pet.add_task(task)

    owner = Owner("Jordan", 120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    next_task = scheduler.complete_task(task, pet)

    assert next_task is None
    assert len(pet.tasks) == 1  # no new task added


def test_replan_after_completion():
    """After completing a task, generate_plan should only schedule pending tasks."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high", "walk", is_required=True))
    pet.add_task(Task("Feed", 10, "high", "feed", is_required=True))

    owner = Owner("Jordan", 60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    pet.tasks[0].mark_done()  # Walk done
    scheduler.generate_plan()

    titles = [t.title for t in scheduler.plan]
    assert "Walk" not in titles
    assert "Feed" in titles


# ===== Conflict detection =====

def test_detect_conflict_same_category():
    """Two tasks of the same category in the same time slot should trigger a warning."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, "high", "walk", preferred_time="morning"))
    pet.add_task(Task("Park walk", 20, "medium", "walk", preferred_time="morning"))

    owner = Owner("Jordan", 120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    warnings = scheduler.detect_conflicts()
    assert any("multiple walk tasks" in w for w in warnings)


def test_detect_conflict_duplicate_title():
    """Duplicate task titles in the same slot should trigger a warning."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Give meds", 5, "high", "meds", preferred_time="morning"))
    pet.add_task(Task("Give meds", 5, "high", "meds", preferred_time="morning"))

    owner = Owner("Jordan", 60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    warnings = scheduler.detect_conflicts()
    assert any("'Give meds' appears more than once" in w for w in warnings)


def test_detect_no_conflicts():
    """Tasks in different slots and categories should produce no warnings."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high", "walk", preferred_time="morning"))
    pet.add_task(Task("Grooming", 20, "medium", "groom", preferred_time="afternoon"))
    pet.add_task(Task("Play", 15, "low", "enrichment", preferred_time="evening"))

    owner = Owner("Jordan", 120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert scheduler.detect_conflicts() == []


def test_detect_conflict_cross_pet():
    """Conflicts should be detected across different pets in the same slot."""
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Dog walk", 30, "high", "walk", preferred_time="morning"))
    bella = Pet("Bella", "cat")
    bella.add_task(Task("Cat walk", 15, "medium", "walk", preferred_time="morning"))

    owner = Owner("Jordan", 120)
    owner.add_pet(mochi)
    owner.add_pet(bella)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    warnings = scheduler.detect_conflicts()
    assert any("multiple walk tasks" in w for w in warnings)


# ===== Scheduling edge cases =====

def test_generate_plan_empty_tasks():
    """A pet with no tasks should produce an empty plan."""
    pet = Pet("Mochi", "dog")
    owner = Owner("Jordan", 60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert scheduler.plan == []
    assert scheduler.total_time_used == 0


def test_required_tasks_exceed_budget():
    """Required tasks should be scheduled even if they exceed the time budget."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Long walk", 40, "high", "walk", is_required=True))
    pet.add_task(Task("Give meds", 30, "high", "meds", is_required=True))

    owner = Owner("Jordan", 30)  # budget is only 30 min
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.plan) == 2  # both required, both scheduled
    assert scheduler.total_time_used == 70  # exceeds 30 min budget


def test_generate_plan_exact_fit():
    """Tasks that exactly fill the budget should all be scheduled with nothing skipped."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high", "walk"))
    pet.add_task(Task("Feed", 30, "medium", "feed"))

    owner = Owner("Jordan", 60)  # exactly 30 + 30
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.plan) == 2
    assert scheduler.skipped == []
    assert scheduler.total_time_used == 60
