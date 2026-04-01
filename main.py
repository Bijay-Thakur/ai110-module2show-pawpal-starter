from pawpal_system import Owner, Pet, Task, Scheduler

# --- Owner ---
owner = Owner(
    name="Bijay",
    contact_info="bijay@example.com",
    available_hours=["07:00", "08:00", "09:00", "12:00", "17:00", "19:00"],
)

# --- Pets ---
luna = Pet(name="Luna", species="dog", age=3, breed="Golden Retriever",
           special_needs=["hip supplement with food"])
mochi = Pet(name="Mochi", species="cat", age=5, breed="Ragdoll")

owner.add_pet(luna)
owner.add_pet(mochi)

# --- Tasks for Luna ---
morning_walk = Task(
    title="Morning Walk",
    description="30-minute walk around the park",
    duration_minutes=30,
    priority="high",
    frequency="daily",
    preferred_time="07:00",
)
feeding_luna = Task(
    title="Feed Luna",
    description="1 cup dry food + hip supplement",
    duration_minutes=5,
    priority="high",
    frequency="daily",
    preferred_time="08:00",
)
grooming = Task(
    title="Brush Coat",
    description="Brush to prevent matting",
    duration_minutes=15,
    priority="low",
    frequency="weekly",
    preferred_time="19:00",
)

# --- Tasks for Mochi ---
feeding_mochi = Task(
    title="Feed Mochi",
    description="Half can wet food, morning",
    duration_minutes=5,
    priority="high",
    frequency="daily",
    preferred_time="08:00",
)
playtime = Task(
    title="Playtime",
    description="Wand toy session to keep Mochi active",
    duration_minutes=20,
    priority="medium",
    frequency="daily",
    preferred_time="17:00",
)
litter_box = Task(
    title="Clean Litter Box",
    description="Scoop and refresh litter",
    duration_minutes=10,
    priority="medium",
    frequency="daily",
    preferred_time="09:00",
)

# --- Scheduler ---
scheduler = Scheduler(owner)

# Add tasks in a different order than their preferred times to verify sorting and scheduling logic.
scheduler.add_task(playtime, mochi)
scheduler.add_task(litter_box, mochi)
scheduler.add_task(morning_walk, luna)
scheduler.add_task(feeding_mochi, mochi)
scheduler.add_task(grooming, luna)
scheduler.add_task(feeding_luna, luna)

# --- Sort and filter checks ---
print("All pending tasks sorted by preferred time:")
all_pending = scheduler.filter_tasks()
for task in scheduler.sort_by_time(all_pending):
    print(f"- {task.title} @ {task.preferred_time or 'Anytime'} ({task.priority})")

print("\nMochi's pending tasks:")
for task in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"- {task.title} @ {task.preferred_time or 'Anytime'}")

scheduler.generate_schedule()

print("\nConflicts detected:")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"- {warning}")
else:
    print("- None")

# --- Print Today's Schedule ---
print("=" * 50)
print("        TODAY'S SCHEDULE — PawPal+")
print("=" * 50)
print(scheduler.explain_plan())
print("=" * 50)

# --- Recurring task behavior ---
print("\nMarking 'Feed Luna' complete to create its next occurrence:")
scheduler.mark_task_complete(feeding_luna)
print("Remaining pending tasks for Luna:")
for task in luna.get_tasks():
    print(f"- {task.title} due {task.due_date or 'today'} @ {task.preferred_time}")
