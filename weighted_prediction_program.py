import streamlit as st
import numpy as np

# Global variables (initialized in session state)

# Set Main Numbers
def set_main_numbers(nums):
    st.session_state["main_numbers"] = nums
    st.success(f"Main numbers set: {nums}")

# Add a new entry
def add_entry(number):
    entries = st.session_state.get("entries", [])
    matches = st.session_state.get("matches", np.zeros(38))
    main_numbers = st.session_state.get("main_numbers", [])

    entries.append(number)
    if number in main_numbers:
        matches[number] += 1

    st.session_state["entries"] = entries
    st.session_state["matches"] = matches
    st.success(f"Entry added: {number}")

# Reset all data
def reset_program():
    st.session_state["entries"] = []
    st.session_state["matches"] = np.zeros(38)
    st.success("Program reset completed.")

# Backtrack last entry
def backtrack_entry():
    entries = st.session_state.get("entries", [])
    matches = st.session_state.get("matches", np.zeros(38))
    main_numbers = st.session_state.get("main_numbers", [])

    if entries:
        last_entry = entries.pop()
        if last_entry in main_numbers:
            matches[last_entry] -= 1
        st.session_state["entries"] = entries
        st.session_state["matches"] = matches
        st.success(f"Removed last entry: {last_entry}")

# Display matrix of entries with weighted predictions
def display_matrix():
    entries = st.session_state.get("entries", [])
    main_numbers = st.session_state.get("main_numbers", [])
    matches = st.session_state.get("matches", np.zeros(38))

    matrix = [entries[i:i+6] for i in range(0, len(entries), 6)]
    st.write("### Matrix of Entries:")
    for col in zip(*matrix):
        st.text(col)

    if len(entries) >= 36 and main_numbers:
        st.write("### Prediction Probabilities (Weighted by Recency):")
        total_weight = 0
        weighted_matches = {num: 0 for num in main_numbers}

        # Assign weights based on recency (newest entries have higher weight)
        for i, entry in enumerate(reversed(entries)):
            weight = (i + 1)  # Simple linear weighting: newest has weight 1, oldest has weight len(entries)
            total_weight += weight
            if entry in main_numbers:
                weighted_matches[entry] += weight

        probabilities = {}
        if total_weight > 0:
            for num in main_numbers:
                probabilities[num] = round((weighted_matches[num] / total_weight) * 100, 2)
        else:
            probabilities = {num: 0.0 for num in main_numbers}

        st.write(probabilities)

# Streamlit UI
st.title("Weighted Prediction Program")

# Initialize session state if not present
if "main_numbers" not in st.session_state:
    st.session_state["main_numbers"] = []
if "entries" not in st.session_state:
    st.session_state["entries"] = []
if "matches" not in st.session_state:
    st.session_state["matches"] = np.zeros(38)

# User input for main numbers
main_numbers_input = st.text_input("Enter 6 Main Numbers (comma-separated):")
if st.button("Set Main Numbers"):
    try:
        nums_str = main_numbers_input.split(',')
        nums = [int(num.strip()) for num in nums_str]
        if len(nums) != 6:
            st.error("Please enter exactly 6 numbers.")
        elif not all(0 <= n <= 37 for n in nums):
            st.error("Please enter numbers between 0 and 37 (37 for '00').")
        else:
            set_main_numbers(nums)
    except ValueError:
        st.error("Invalid input. Please enter numbers separated by commas.")

# User input for new entries
new_entry = st.number_input("Enter a New Number (0-36, 37 for '00'):", min_value=0, max_value=37, step=1)
if st.button("Add Entry"):
    add_entry(int(new_entry))

# Buttons for actions
if st.button("Display Matrix and Predictions"):
    display_matrix()

if st.button("Reset Program"):
    reset_program()

if st.button("Backtrack Last Entry"):
    backtrack_entry()