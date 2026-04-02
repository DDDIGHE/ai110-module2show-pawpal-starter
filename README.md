# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Beyond basic priority ordering, PawPal+ includes:

- **Time-slot sorting** — tasks have a `preferred_time` (morning, afternoon, evening). `sort_by_time()` reorders the plan so morning tasks come first, using Python's stable sort to preserve priority order within each slot.
- **Multi-criteria filtering** — `filter_tasks()` narrows tasks by completion status, pet name, or both. Useful for viewing only pending tasks or tasks for a specific pet.
- **Conflict detection** — `detect_conflicts()` warns (without crashing) when duplicate task titles or multiple tasks of the same category land in the same time slot.
- **Recurring tasks** — completing a daily or weekly task auto-creates the next occurrence with an updated `due_date`. One-off tasks (`as_needed`) do not recur.

## Testing PawPal+

Run the full test suite:

```bash
python -m pytest tests/test_pawpal.py -v
```

The suite contains **16 tests** covering five areas:

| Area | Tests | What's verified |
|---|---|---|
| Sorting | 3 | Time-slot ordering, stable sort within slots, "anytime" passthrough |
| Recurrence | 4 | Daily (+1 day), weekly (+7 days), as_needed (no repeat), re-plan excludes completed |
| Conflict detection | 4 | Same category warns, duplicate title warns, no false positives, cross-pet detection |
| Scheduling edge cases | 3 | Empty task list, required tasks exceeding budget, exact budget fit |
| Basics | 2 | Task completion, task addition to pet |

**Confidence Level: 4/5**

Core scheduling, sorting, recurrence, and conflict logic are well-covered with both happy paths and edge cases. One star withheld because the Streamlit UI integration and `Owner.preferences` behavior are not yet tested — preferences are stored but not used by the scheduler.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
