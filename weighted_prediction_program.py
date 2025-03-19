import streamlit as st
import numpy as np

# Helper Functions
def validate_main_numbers(input_text):
    try:
        nums = [int(num.strip()) for num in input_text.split(',')]
        if len(nums) != 6:
            return "Please enter exactly 6 numbers."
        elif not all(0 <= n <= 37 for n in nums):
            return "Numbers must be between 0 and 37 (37 for '00')."
        return nums
    except ValueError:
        return "Invalid input. Ensure only integers separated by commas."

def update_matches_for_entry(number, main_numbers, matches, weight=1):
    """Update matches array when adding or removing an entry."""
    if number in main_numbers:
        matches[number] += weight
    return matches

def format_entry_display(entry):
    """Format entries for display, showing '00' instead of 37."""
    return "00" if entry == 37 else str(entry)

# Core Functions
def set_main_numbers(nums):
    st.session_state["main_numbers"] = nums
    st.success(f"Main numbers set: {nums}")

def add_entry(number):
    entries = st.session_state.get("entries", [])
    matches = st.session_state.get("matches", np.zeros(38))
    main_numbers = st.session_state.get("main_numbers", [])

    entries.append(number)
    matches = update_matches_for_entry(number, main_numbers, matches, weight=1)

    st.session_state["entries"] = entries
    st.session_state["matches"] = matches
    st.success(f"Entry added: {number}")

def reset_program():
    st.session_state["entries"] = []
    st.session_state["matches"] = np.zeros(38)
    st.success("Program reset completed.")

def backtrack_entry():
    entries = st.session_state.get("entries", [])
    matches = st.session_state.get("matches", np.zeros(38))
    main_numbers = st.session_state.get("main_numbers", [])

    if entries:
        last_entry = entries.pop()
        matches = update_matches_for_entry(last_entry, main_numbers, matches, weight=-1)
        st.session_state["entries"] = entries
        st.session_state["matches"] = matches
        st.success(f"Removed last entry: {last_entry}")

def display_matrix(entries):
    if entries:
        matrix = [[format_entry_display(entry) for entry in entries[i:i + 6]] for i in range(0, len(entries), 6)]
        st.write("### Matrix of Entries:")
        st.dataframe(matrix, use_container_width=True)

def display_predictions(entries, main_numbers, matches):
    if entries and main_numbers:
        total_weight = len(entries)  # Total entries processed as the base weight
        weighted_matches = {num: 0 for num in main_numbers}

        # Calculate weighted probabilities based on occurrences
        for entry in entries:
            if entry in main_numbers:
                weighted_matches[entry] += 1

        probabilities = {num: round((weighted_matches[num] / total_weight) * 100, 2) for num in main_numbers}

        # Display results
        st.write("### Prediction Results:")
        results = " | ".join(f"{format_entry_display(num)}: {prob}%" for num, prob in probabilities.items())
        st.write(results)


# Streamlit UI
st.title("Weighted Prediction Program")

# Initialize session state
if "main_numbers" not in st.session_state:
    st.session_state["main_numbers"] = []
if "entries" not in st.session_state:
    st.session_state["entries"] = []
if "matches" not in st.session_state:
    st.session_state["matches"] = np.zeros(38)

# User input for main numbers
main_numbers_input = st.text_input("Enter 6 Main Numbers (comma-separated):")
if st.button("Set Main Numbers"):
    validation_result = validate_main_numbers(main_numbers_input)
    if isinstance(validation_result, str):
        st.error(validation_result)
    else:
        set_main_numbers(validation_result)

# User input for new entries
new_entry = st.number_input("Enter a New Number (0-36, 37 for '00'):", min_value=0, max_value=37, step=1)
if st.button("Add Entry"):
    add_entry(int(new_entry))
    display_matrix(st.session_state["entries"])  # Show matrix
    display_predictions(st.session_state["entries"], st.session_state["main_numbers"], st.session_state["matches"])  # Show predictions

# Buttons for actions
if st.button("Reset Program"):
    reset_program()

if st.button("Backtrack Last Entry"):
    backtrack_entry()
    display_matrix(st.session_state["entries"])  # Update matrix
    display_predictions(st.session_state["entries"], st.session_state["main_numbers"], st.session_state["matches"])  # Update predictions
