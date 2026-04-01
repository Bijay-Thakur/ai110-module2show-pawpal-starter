from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task — a single pet care action
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    description: str
    duration_minutes: int
    priority: str                        # "low" | "medium" | "high"
    frequency: str                       # e.g. "daily", "weekly", "as needed"
    preferred_time: Optional[str] = None # e.g. "08:00"
    due_date: Optional[date] = None
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def get_priority_score(self) -> int:
        """Return a numeric score (higher = more urgent) for sorting."""
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority.lower(), 0)

    def clone_for_next_occurrence(self) -> Optional["Task"]:
        """Create the next recurring task instance for daily or weekly frequencies."""
        if self.frequency not in {"daily", "weekly"}:
            return None

        current_due = self.due_date or date.today()
        delta = timedelta(days=1 if self.frequency == "daily" else 7)
        next_due = current_due + delta

        return Task(
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            due_date=next_due,
        )

    def __repr__(self) -> str:
        """Return a compact string showing title, priority, frequency, duration, and status."""
        status = "done" if self.is_completed else "pending"
        time_str = f" @ {self.preferred_time}" if self.preferred_time else ""
        due_str = f" due {self.due_date}" if self.due_date else ""
        return (
            f"Task({self.title!r}, {self.priority}, {self.frequency}, "
            f"{self.duration_minutes}min{time_str}{due_str}, {status})"
        )


# ---------------------------------------------------------------------------
# Pet — the animal being cared for
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str                                        # e.g. "dog", "cat"
    age: int
    breed: str = ""
    special_needs: list[str] = field(default_factory=list)
    _tasks: list[Task] = field(default_factory=list, repr=False)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet; silently skips duplicates."""
        if task not in self._tasks:
            self._tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's list."""
        self._tasks.remove(task)

    def get_tasks(self, include_completed: bool = False) -> list[Task]:
        """Return a copy of this pet's tasks, excluding completed ones by default."""
        if include_completed:
            return list(self._tasks)
        return [t for t in self._tasks if not t.is_completed]

    def __repr__(self) -> str:
        """Return a compact string showing the pet's name, species, age, needs, and task count."""
        breed_str = f" ({self.breed})" if self.breed else ""
        needs_str = f", needs: {self.special_needs}" if self.special_needs else ""
        return (
            f"Pet({self.name!r}, {self.species}{breed_str}, "
            f"age={self.age}{needs_str}, tasks={len(self._tasks)})"
        )


# ---------------------------------------------------------------------------
# Owner — the person responsible for the pet(s)
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        name: str,
        contact_info: str = "",
        available_hours: list[str] = None,
    ):
        """Initialize an Owner with a name, optional contact info, and available time slots."""
        self.name = name
        self.contact_info = contact_info
        # Avoid mutable default argument; copy to prevent external aliasing
        self.available_hours: list[str] = list(available_hours) if available_hours else []
        self._pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner; silently skips duplicates."""
        if pet not in self._pets:
            self._pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list."""
        self._pets.remove(pet)

    def get_pets(self) -> list[Pet]:
        """Return a copy of all registered pets."""
        return list(self._pets)

    def get_all_tasks(self, include_completed: bool = False) -> list[Task]:
        """Return a flat list of every task across all owned pets."""
        tasks: list[Task] = []
        for pet in self._pets:
            tasks.extend(pet.get_tasks(include_completed=include_completed))
        return tasks

    def __repr__(self) -> str:
        """Return a compact string showing the owner's name, pet count, and available slots."""
        contact_str = f", contact={self.contact_info!r}" if self.contact_info else ""
        return (
            f"Owner({self.name!r}{contact_str}, "
            f"pets={len(self._pets)}, slots={self.available_hours})"
        )


# ---------------------------------------------------------------------------
# Scheduler — builds and explains a daily care plan across all pets
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the Scheduler for a given owner, managing tasks across all their pets."""
        self.owner = owner
        # Maps each tracked task to its associated pet for grouping / display
        self._task_pet_map: dict[int, tuple[Task, Pet]] = {}
        self.schedule: list[dict] = []  # each entry: {time, task, pet_name, reason}
        self.schedule_warnings: list[str] = []

    def add_task(self, task: Task, pet: Pet) -> None:
        """Add a task to the given pet AND track it internally."""
        pet.add_task(task)
        # Use id(task) as key so identical-valued tasks from different pets stay distinct
        if id(task) not in self._task_pet_map:
            self._task_pet_map[id(task)] = (task, pet)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by preferred time, with unscheduled tasks last."""
        return sorted(tasks, key=lambda t: t.preferred_time or "23:59")

    def filter_tasks(self, pet_name: str = None, include_completed: bool = False) -> list[Task]:
        """Filter tasks by pet name and completion status."""
        if pet_name is None:
            return self.owner.get_all_tasks(include_completed=include_completed)

        for pet in self.owner.get_pets():
            if pet.name == pet_name:
                return pet.get_tasks(include_completed=include_completed)

        return []

    def detect_conflicts(self, schedule: list[dict] = None) -> list[str]:
        """Return lightweight warnings for tasks that share the same scheduled time."""
        schedule = schedule if schedule is not None else self.schedule
        warnings: list[str] = []
        grouped: dict[str, list[dict]] = {}

        for entry in schedule:
            if entry["time"] == "UNSCHEDULED":
                continue
            grouped.setdefault(entry["time"], []).append(entry)

        for time, entries in grouped.items():
            if len(entries) > 1:
                pet_names = ", ".join(sorted({entry["pet_name"] for entry in entries}))
                task_titles = ", ".join(entry["task"].title for entry in entries)
                warnings.append(
                    f"Conflict at {time}: {task_titles} for {pet_names}."
                )

        return warnings

    def prioritize_tasks(self, pet: Pet = None) -> list[Task]:
        """Return pending tasks sorted by descending priority then preferred time; scope to one pet if given."""
        if pet is not None:
            tasks = pet.get_tasks(include_completed=False)
        else:
            # Gather every tracked task that is still pending
            tasks = [
                t for (t, _p) in self._task_pet_map.values()
                if not t.is_completed
            ]

        return sorted(
            tasks,
            key=lambda t: (-t.get_priority_score(), t.preferred_time or "23:59"),
        )

    def generate_schedule(self) -> list[dict]:
        """Assign pending tasks to the owner's available time slots, flagging overflow as UNSCHEDULED."""
        sorted_tasks = self.prioritize_tasks()  # already excludes completed
        available_slots = list(self.owner.available_hours)
        used_slots: set[str] = set()
        self.schedule = []

        for task in sorted_tasks:
            _, pet = self._task_pet_map.get(id(task), (task, None))
            pet_name = pet.name if pet is not None else "Unknown"

            if task.preferred_time and task.preferred_time in available_slots:
                # Honor preferred time even if another task already uses it; detect conflicts later.
                time = task.preferred_time
                used_slots.add(time)
            else:
                next_available = next(
                    (slot for slot in available_slots if slot not in used_slots),
                    None,
                )
                if next_available is not None:
                    time = next_available
                    used_slots.add(time)
                else:
                    time = "UNSCHEDULED"

            reason = (
                f"{task.title} ({task.priority} priority, "
                f"{task.duration_minutes} min, {task.frequency})"
            )
            if time == "UNSCHEDULED":
                reason = (
                    f"{task.title} could not be placed — no available time slots remaining"
                )

            self.schedule.append(
                {"time": time, "task": task, "pet_name": pet_name, "reason": reason}
            )

        self.schedule_warnings = self.detect_conflicts(self.schedule)
        return list(self.schedule)  # return a copy

    def explain_plan(self) -> str:
        """Return a human-readable schedule grouped by pet, with an overflow warning."""
        if not self.schedule:
            return "No schedule has been generated yet. Call generate_schedule() first."

        # Group entries by pet_name to make the output easier to scan
        grouped: dict[str, list[dict]] = {}
        for entry in self.schedule:
            grouped.setdefault(entry["pet_name"], []).append(entry)

        lines = [f"Daily care plan for {self.owner.name}:"]
        lines.append("-" * 50)

        for pet_name, entries in grouped.items():
            lines.append(f"  {pet_name}:")
            for entry in entries:
                lines.append(f"    {entry['time']:>11}  —  {entry['reason']}")

        unscheduled_count = sum(
            1 for e in self.schedule if e["time"] == "UNSCHEDULED"
        )
        if unscheduled_count:
            lines.append(
                f"\n  WARNING: {unscheduled_count} task(s) could not be scheduled. "
                "Add more available hours to fit them."
            )

        if self.schedule_warnings:
            lines.append("\n  CONFLICTS detected:")
            for warning in self.schedule_warnings:
                lines.append(f"    - {warning}")

        return "\n".join(lines)

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task complete, regenerate the schedule, and enqueue the next occurrence for recurring tasks."""
        task.mark_complete()
        next_task = task.clone_for_next_occurrence()
        if next_task is not None and id(task) in self._task_pet_map:
            _, pet = self._task_pet_map[id(task)]
            self.add_task(next_task, pet)

        self.generate_schedule()

    def reset(self) -> None:
        """Clear the current schedule so generate_schedule() can be called fresh."""
        self.schedule = []
