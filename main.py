"""Temporary testing ground — verify PawPal+ logic in terminal."""

from pawpal_system import Pet, Owner, Task, Scheduler

# --- Setup: Owner with two pets ---
mochi = Pet("Mochi", "dog")
mochi.add_task(Task("Morning walk", 30, "high", "walk", is_required=True))
mochi.add_task(Task("Give meds", 5, "high", "meds", is_required=True))
mochi.add_task(Task("Grooming", 20, "medium", "groom"))
mochi.add_task(Task("Enrichment toy", 15, "low", "enrichment"))

bella = Pet("Bella", "cat")
bella.add_task(Task("Feed breakfast", 10, "high", "feed", is_required=True))
bella.add_task(Task("Litter box clean", 10, "medium", "general"))
bella.add_task(Task("Play with feather toy", 15, "low", "enrichment"))

jordan = Owner("Jordan", 75, preferences=["walk in morning", "meds before food"])
jordan.add_pet(mochi)
jordan.add_pet(bella)

# --- Print owner & pet summaries ---
print("=" * 50)
print(f"Owner: {jordan.summary()}")
print("-" * 50)
for pet in jordan.pets:
    print(f"  {pet.summary()}")
    for task in pet.tasks:
        print(f"    - {task}")

# --- Generate and display schedule ---
print("\n" + "=" * 50)
print("Today's Schedule")
print("=" * 50)

scheduler = Scheduler(jordan)
scheduler.generate_plan()
print(scheduler.explain_plan())
