"""Tests for PawPal+ core logic."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task


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
