from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(**overrides):
    """Return a minimal Task, with any field overridable."""
    defaults = dict(
        title="Morning Walk",
        description="Walk around the park",
        duration_minutes=30,
        priority="medium",
        frequency="daily",
    )
    defaults.update(overrides)
    return Task(**defaults)


def make_pet(**overrides):
    """Return a minimal Pet, with any field overridable."""
    defaults = dict(name="Luna", species="dog", age=3)
    defaults.update(overrides)
    return Pet(**defaults)


# ---------------------------------------------------------------------------
# Test 1 — Task completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.is_completed is False, "Task should start as incomplete"

    task.mark_complete()

    assert task.is_completed is True, "Task should be complete after mark_complete()"


# ---------------------------------------------------------------------------
# Test 2 — Task addition to a Pet
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.get_tasks(include_completed=True)) == 0, "Pet should start with no tasks"

    pet.add_task(make_task(title="Feed"))
    assert len(pet.get_tasks(include_completed=True)) == 1

    pet.add_task(make_task(title="Groom"))
    assert len(pet.get_tasks(include_completed=True)) == 2


# ---------------------------------------------------------------------------
# Test 3 — Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_orders_tasks_chronologically():
    owner = Owner(name="Owner", available_hours=["08:00", "12:00"])
    scheduler = Scheduler(owner)

    early = make_task(title="Breakfast", preferred_time="08:00")
    later = make_task(title="Walk", preferred_time="12:00")

    sorted_tasks = scheduler.sort_by_time([later, early])

    assert sorted_tasks == [early, later]


# ---------------------------------------------------------------------------
# Test 4 — Recurrence logic
# ---------------------------------------------------------------------------

def test_mark_complete_creates_next_daily_occurrence():
    owner = Owner(name="Owner", available_hours=["08:00"])
    pet = make_pet()
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    task = make_task(
        title="Feed",
        frequency="daily",
        preferred_time="08:00",
        due_date=date(2026, 4, 1),
    )
    scheduler.add_task(task, pet)

    scheduler.mark_task_complete(task)

    pending_tasks = pet.get_tasks()
    assert len(pending_tasks) == 1

    next_task = pending_tasks[0]
    assert next_task.title == "Feed"
    assert next_task.due_date == date(2026, 4, 2)
    assert next_task.is_completed is False
    assert task.is_completed is True
    assert next_task is not task


# ---------------------------------------------------------------------------
# Test 5 — Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_duplicate_times():
    owner = Owner(name="Owner", available_hours=["08:00", "09:00"])
    pet_a = make_pet(name="Luna")
    pet_b = make_pet(name="Mochi", species="cat", age=4)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)
    scheduler = Scheduler(owner)

    first = make_task(title="Feed Luna", preferred_time="08:00")
    second = make_task(title="Feed Mochi", preferred_time="08:00")

    scheduler.add_task(first, pet_a)
    scheduler.add_task(second, pet_b)
    scheduler.generate_schedule()

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert warnings[0] == "Conflict at 08:00: Feed Luna, Feed Mochi for Luna, Mochi."
