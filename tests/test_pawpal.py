from pawpal_system import Task, Pet


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
