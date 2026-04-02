"""Temporary testing ground — test conflict detection."""

from pawpal_system import Pet, Owner, Task, Scheduler

# --- Setup: intentional conflicts ---
mochi = Pet("Mochi", "dog")
# Conflict 1: two walk tasks in morning slot (same category, same time)
mochi.add_task(Task("Morning walk", 30, "high", "walk", is_required=True, preferred_time="morning"))
mochi.add_task(Task("Park walk", 25, "medium", "walk", preferred_time="morning"))

# Conflict 2: duplicate title
mochi.add_task(Task("Give meds", 5, "high", "meds", is_required=True, preferred_time="morning"))
mochi.add_task(Task("Give meds", 5, "high", "meds", is_required=True, preferred_time="morning"))

bella = Pet("Bella", "cat")
bella.add_task(Task("Feed breakfast", 10, "high", "feed", is_required=True, preferred_time="morning"))
# Conflict 3: cross-pet conflict — two feed tasks in same slot
bella.add_task(Task("Feed snack", 5, "low", "feed", preferred_time="morning"))

# No conflict — different time slot
bella.add_task(Task("Litter box clean", 10, "medium", "general", preferred_time="afternoon"))

jordan = Owner("Jordan", 120)
jordan.add_pet(mochi)
jordan.add_pet(bella)

scheduler = Scheduler(jordan)
scheduler.generate_plan()
scheduler.sort_by_time()
print(scheduler.explain_plan())
