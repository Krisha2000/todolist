import streamlit as st
import json
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(
    page_title="Pro To-Do List",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- File for Data Persistence ---
TASKS_FILE = Path("tasks.json")

# --- Helper Functions for Data Handling ---
def load_tasks():
    """Loads tasks from the JSON file. Returns an empty list if file not found."""
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []  # Return empty list if file is corrupted or empty
    return []

def save_tasks(tasks):
    """Saves the current list of tasks to the JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# --- State Management ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()
if 'filter' not in st.session_state:
    st.session_state.filter = "All"

# --- App Layout ---
st.title("🚀 Pro To-Do List")
st.markdown("---")

# --- Task Summary & Progress ---
total_tasks = len(st.session_state.tasks)
completed_tasks = sum(1 for task in st.session_state.tasks if task["completed"])

st.subheader("Your Progress", divider="rainbow")
if total_tasks > 0:
    progress_percent = completed_tasks / total_tasks
    st.progress(progress_percent, text=f"**{completed_tasks} of {total_tasks} tasks completed**")
else:
    st.info("Your to-do list is empty. Add a task below to get started!")

st.markdown("---")

# --- Task Input Form ---
with st.form("new_task_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        new_task_content = st.text_input(
            "Add a new task", 
            placeholder="What needs to be done?",
            label_visibility="collapsed"
        )
    with col2:
        priority = st.selectbox(
            "Priority",
            ("🔴 High", "🟡 Medium", "🟢 Low"),
            label_visibility="collapsed"
        )
    
    submitted = st.form_submit_button("Add Task", use_container_width=True, type="primary")

if submitted and new_task_content:
    new_task = {"task": new_task_content, "completed": False, "priority": priority}
    st.session_state.tasks.append(new_task)
    save_tasks(st.session_state.tasks)
    st.success("Task added successfully! 🎉")

# --- Filtering and Task Display ---
col1, col2 = st.columns([2, 1.2])

with col1:
    st.subheader("📋 Your Tasks")
with col2:
    st.session_state.filter = st.radio(
        "Filter tasks",
        ["All", "Active", "Completed"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("---")

# Filter logic
if st.session_state.filter == "Completed":
    filtered_tasks = [task for task in st.session_state.tasks if task["completed"]]
elif st.session_state.filter == "Active":
    filtered_tasks = [task for task in st.session_state.tasks if not task["completed"]]
else:
    filtered_tasks = st.session_state.tasks

# Displaying tasks
if not filtered_tasks:
    st.warning(f"No tasks found for the filter: **{st.session_state.filter}**")
else:
    for index, task in enumerate(st.session_state.tasks):
        # This complex logic is to find the original index for proper modification/deletion
        if task in filtered_tasks:
            original_index = st.session_state.tasks.index(task)
            
            task_col1, task_col2, task_col3 = st.columns([0.15, 2, 0.5])

            with task_col1:
                # Checkbox for marking task as complete
                is_completed = st.checkbox(
                    "", 
                    value=task["completed"], 
                    key=f"task_{original_index}"
                )
                if is_completed != task["completed"]:
                    st.session_state.tasks[original_index]["completed"] = is_completed
                    save_tasks(st.session_state.tasks)
                    st.rerun()

            with task_col2:
                # Display task with priority
                display_text = f"{task['priority']} - {task['task']}"
                if task["completed"]:
                    st.markdown(f"~~_{display_text}_~~")
                else:
                    st.markdown(f"**{display_text}**")
            
            with task_col3:
                # Delete button
                if st.button("Delete 🗑️", key=f"delete_{original_index}", use_container_width=True):
                    st.session_state.tasks.pop(original_index)
                    save_tasks(st.session_state.tasks)
                    st.rerun()

# --- Clear Completed Tasks Button ---
if any(task["completed"] for task in st.session_state.tasks):
    st.markdown("---")
    if st.button("Clear All Completed Tasks", use_container_width=True):
        st.session_state.tasks = [task for task in st.session_state.tasks if not task["completed"]]
        save_tasks(st.session_state.tasks)
        st.rerun()