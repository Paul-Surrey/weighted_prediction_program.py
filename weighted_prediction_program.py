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
    st.session_state["last_entry"] = None
    st.session_state["new_number_input"] = None
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

def display_predictions(entries, main_numbers, matches):
    if entries and main_numbers:
        total_weight = len(entries)  # Total entries processed as the base weight
        weighted_matches = {num: 0 for num in main_numbers}

        # Calculate weighted probabilities based on occurrences
        for entry in entries:
            if entry in main_numbers:
                weighted_matches[entry] += 1

        probabilities = {num: round((weighted_matches[num] / total_weight) * 100, 2) for num in main_numbers}
        probabilities_sorted = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

        # Calculate "POSSIBLE" probability
        no_hit_probability = 1.0
        for _, prob in probabilities.items():
            no_hit_probability *= (1 - prob / 100)
        possible_probability = round((1 - no_hit_probability) * 100, 2)

        # Display results with smaller font
        st.markdown("<h4>Prediction Results:</h4>", unsafe_allow_html=True)
        results = " | ".join(f"{format_entry_display(num)}: {prob}%" for num, prob in probabilities_sorted)
        st.write(results)
        st.write(f"**POSSIBLE:** {possible_probability}% chance of at least one hit.")

def display_matrix(entries):
    if entries:
        st.markdown("<h4>Matrix of Entries:</h4>", unsafe_allow_html=True)
        # Group entries into columns of six numbers each using a table layout
        num_columns = len(entries) // 6 + (1 if len(entries) % 6 != 0 else 0)
        rows = []
        for i in range(6):  # A maximum of 6 rows
            row = []
            for j in range(num_columns):
                index = j * 6 + i
                if index < len(entries):
                    row.append(format_entry_display(entries[index]))
                else:
                    row.append("")  # Fill empty spaces
            rows.append(row)

        # Render as a simple HTML table for mobile compatibility
        table_html = "<table style='width:100%; text-align:center;'>"
        for row in rows:
            table_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # Add total entries display
        st.markdown(f"<h5>Total Entries: {len(entries)}</h5>", unsafe_allow_html=True)

# Streamlit UI
st.title("Weighted Prediction Program")

# Initialize session state
if "main_numbers" not in st.session_state:
    st.session_state["main_numbers"] = []
if "entries" not in st.session_state:
    st.session_state["entries"] = []
if "matches" not in st.session_state:
    st.session_state["matches"] = np.zeros(38)
if "new_number_input" not in st.session_state:
    st.session_state["new_number_input"] = None
if "last_entry" not in st.session_state:
    st.session_state["last_entry"] = None

# User input for main numbers
main_numbers_input = st.text_input("Enter 6 Main Numbers (comma-separated):")
if st.button("Set Main Numbers"):
    validation_result = validate_main_numbers(main_numbers_input)
    if isinstance(validation_result, str):
        st.error(validation_result)
    else:
        set_main_numbers(validation_result)

# Automatically handle new entry using a number input
new_entry = st.number_input(
    "Enter a New Number (0-36, 37 for '00'):",
    min_value=0,
    max_value=37,
    step=1,
    key="new_number_input"
)

if new_entry != st.session_state.get("last_entry", None):  # Check for valid new input
    st.session_state["last_entry"] = new_entry  # Track the last processed input
    add_entry(int(new_entry))
    display_predictions(st.session_state["entries"], st.session_state["main_numbers"], st.session_state["matches"])
    display_matrix(st.session_state["entries"])
    st.session_state["new_number_input"] = None  # Clear input field

# Buttons for actions (reordered)
if st.button("Backtrack Last Entry"):
    backtrack_entry()
    display_predictions(st.session_state["entries"], st.session_state["main_numbers"], st.session_state["matches"])
    display_matrix(st.session_state["entries"])

if st.button("Reset Program"):
    reset_program()
