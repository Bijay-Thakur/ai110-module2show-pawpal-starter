import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This demo now connects the UI to the backend logic layer, so pets and tasks
are stored in Streamlit session state and persist while you interact with the app.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_hours=["08:00", "12:00", "16:00"])

owner = st.session_state.owner

owner_name = st.text_input("Owner name", value=owner.name)
if owner_name and owner_name != owner.name:
    owner.name = owner_name

available_hours_input = st.text_input(
    "Available hours (comma-separated)",
    value=", ".join(owner.available_hours) if owner.available_hours else "08:00, 12:00, 16:00",
)
owner.available_hours = [hour.strip() for hour in available_hours_input.split(",") if hour.strip()]

st.divider()

st.subheader("Owner summary")
if owner.get_pets():
    st.write(f"**{owner.name}** has {len(owner.get_pets())} pet(s):")
    for pet in owner.get_pets():
        st.write(f"- {pet.name} ({pet.species}, age {pet.age})")
else:
    st.info("No pets yet. Add a pet below.")

st.divider()

st.subheader("Add a pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age", min_value=0, max_value=30, value=2)
    add_pet_button = st.form_submit_button("Add pet")

if add_pet_button:
    new_pet = Pet(name=pet_name, species=species, age=int(age))
    owner.add_pet(new_pet)
    st.success(f"Added {new_pet.name} to {owner.name}'s pets.")
    st.experimental_rerun()

st.divider()

st.subheader("Add a task")
if owner.get_pets():
    pet_names = [pet.name for pet in owner.get_pets()]
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox("Select pet", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        description = st.text_area("Description", value="A short walk around the block.")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"], index=0)
        preferred_time = st.text_input("Preferred time", value="08:00")
        add_task_button = st.form_submit_button("Add task")

    if add_task_button:
        selected_pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)
        new_task = Task(
            title=task_title,
            description=description,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            preferred_time=preferred_time or None,
        )
        selected_pet.add_task(new_task)
        st.success(f"Added task '{new_task.title}' for {selected_pet.name}.")
        st.experimental_rerun()

    if owner.get_all_tasks():
        st.markdown("### Current tasks")
        task_rows = []
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                task_rows.append(
                    {
                        "pet": pet.name,
                        "title": task.title,
                        "priority": task.priority,
                        "duration": task.duration_minutes,
                        "frequency": task.frequency,
                        "preferred_time": task.preferred_time or "Anytime",
                    }
                )
        st.table(task_rows)
    else:
        st.info("No tasks yet. Add one to a pet above.")
else:
    st.info("Add a pet first to start assigning tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button now uses the Scheduler class from the logic layer.")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    elif not owner.available_hours:
        st.warning("Set available hours before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                scheduler.add_task(task, pet)

        schedule = scheduler.generate_schedule()
        st.success("Schedule generated.")
        st.table(
            [
                {
                    "time": entry["time"],
                    "pet": entry["pet_name"],
                    "task": entry["task"].title,
                    "reason": entry["reason"],
                }
                for entry in schedule
            ]
        )
