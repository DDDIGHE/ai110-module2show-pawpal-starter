import streamlit as st
from pawpal_system import Pet, Owner, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A pet care planning assistant that schedules tasks by priority within your time budget.")

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []

# ========== Section 1: Owner + Pet Setup ==========
st.subheader("1. Owner & Pet Setup")

col_owner, col_time = st.columns(2)
with col_owner:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_time:
    available_minutes = st.number_input("Available time (min)", min_value=1, max_value=480, value=60)

st.markdown("**Add a pet:**")
col_pet, col_species = st.columns(2)
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    new_pet = Pet(pet_name, species)
    st.session_state.pets.append(new_pet)
    st.success(f"Added {new_pet.summary()}")

if st.session_state.pets:
    st.write("Your pets:", ", ".join(p.summary() for p in st.session_state.pets))
else:
    st.info("No pets yet. Add one above.")

# Build/update Owner object from current inputs
if st.session_state.pets:
    owner = Owner(owner_name, available_minutes)
    for pet in st.session_state.pets:
        owner.add_pet(pet)
    st.session_state.owner = owner

st.divider()

# ========== Section 2: Task Management ==========
st.subheader("2. Add Tasks to a Pet")

if not st.session_state.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in st.session_state.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)

    col4, col5 = st.columns(2)
    with col4:
        category = st.selectbox("Category", ["walk", "feed", "meds", "groom", "enrichment", "general"])
    with col5:
        is_required = st.checkbox("Required task")

    if st.button("Add task"):
        selected_pet = next(p for p in st.session_state.pets if p.name == selected_pet_name)
        new_task = Task(task_title, int(duration), priority, category, is_required)
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {selected_pet_name}")

    # Show tasks per pet
    for pet in st.session_state.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table([
                {"Task": t.title, "Duration": f"{t.duration_minutes} min",
                 "Priority": t.priority, "Required": t.is_required}
                for t in pet.tasks
            ])

st.divider()

# ========== Section 3: Generate Schedule ==========
st.subheader("3. Generate Daily Schedule")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    if not owner or not owner.all_pending_tasks():
        st.warning("Add at least one pet with tasks before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        scheduler.generate_plan()
        st.code(scheduler.explain_plan())
