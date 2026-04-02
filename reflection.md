# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML has four classes, split into data objects and a logic class:

- **Pet** (dataclass) — Holds pet identity: name and species. Provides a `summary()` for display. Has no behavior of its own; it is owned by an Owner.
- **Owner** (dataclass) — Holds the owner's name, daily time budget (`available_minutes`), a reference to their Pet, and a list of free-text preferences. The Owner is the entry point for the Scheduler to access both human constraints and pet info.
- **Task** (dataclass) — Represents a single care activity: title, duration in minutes, priority (low/medium/high), category (walk, feed, meds, etc.), and an `is_required` flag to distinguish must-do tasks from optional ones.
- **Scheduler** — The only class with real logic. Takes an Owner (and through it, the Pet), receives a list of Tasks, and produces an ordered daily plan via `generate_plan()`. Also provides `explain_plan()` to justify the schedule in human-readable form.

Key relationship: Owner "has-a" Pet (1:1), and Scheduler "uses" Owner (1:1) and "schedules" Tasks (1:many). The Scheduler accesses the Pet through `owner.pet` rather than holding a separate reference, to avoid redundancy.

**Core user actions:**

1. **Set up a profile** — The user enters owner info (name, available time, preferences) and pet info (name, species). This grounds the scheduler in real constraints so the plan reflects the owner's actual situation.

2. **Manage care tasks** — The user adds, edits, or removes pet care tasks (e.g., walk, feed, give meds, grooming). Each task has at minimum a duration (in minutes) and a priority (low, medium, high). These are the building blocks the scheduler works with.

3. **Generate & view a daily plan** — The user requests a schedule for the day. The system selects and orders tasks based on priority and available time, then displays the plan with reasoning for why each task was included and placed where it is.

**b. Design changes**

Yes, three changes were made after reviewing the skeleton for missing relationships and logic bottlenecks:

1. **Removed redundant `Scheduler → Pet` link.** The initial UML had the Scheduler hold both an `owner` and a separate `pet` reference. Since Owner already has `pet`, keeping both created two paths to the same object that could go out of sync. Now the Scheduler accesses the pet via `self.owner.pet`.

2. **Added `skipped` list to Scheduler.** The original design only tracked the final `plan` and `total_time_used`. Without a `skipped` list, `explain_plan()` would have no way to tell the user which tasks were dropped and why. This is important for transparency — a plan that silently ignores tasks is frustrating.

3. **Added input validation on Task and Scheduler.** `Task.priority` was a raw string with no guard — passing `"urgent"` or `"HIGH"` would crash the scheduler at lookup time. Added `__post_init__` to normalize to lowercase and reject invalid values. Also added a check that `Owner.available_minutes > 0` in `Scheduler.__init__`, since a zero or negative budget is meaningless and would produce an empty plan with no explanation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detection system checks for same-category or duplicate-title tasks within the same **time slot** (morning/afternoon/evening), but it does not compute actual overlapping time ranges. For example, if two 30-minute morning tasks are scheduled, the system flags "multiple walk tasks in morning slot" but cannot tell you whether they actually overlap in minutes — it treats the entire morning as one block.

This is a reasonable tradeoff because:
- Pet care tasks rarely have exact clock times ("walk at 8:07 AM"). Owners think in broad slots: morning, afternoon, evening.
- Implementing true overlap detection would require start/end timestamps for each task and interval comparison logic, adding significant complexity for minimal real-world benefit in this use case.
- The current approach catches the most common mistake — accidentally scheduling the same type of activity twice in the same part of the day — which is the main thing a pet owner would want to know.

A secondary tradeoff: the AI suggested rewriting `detect_conflicts()` using `Counter` and generator expressions for a more "Pythonic" style. The compressed version saved ~5 lines but was harder to read and debug. I kept the explicit loop version because readability matters more than brevity in a method that produces user-facing warnings.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
