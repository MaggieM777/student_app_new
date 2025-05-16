import streamlit as st
import pandas as pd

# Инициализация на session_state
if "firms" not in st.session_state:
    st.session_state.firms = []

if "students" not in st.session_state:
    st.session_state.students = []

# Заглавие
st.title("Student-Firm Application")

# === Ръчно добавяне на фирми ===
st.header("Add Firm")
firm_name = st.text_input("Enter Firm Name")
firm_quota = st.number_input("Enter Quota", min_value=1)

if st.button("Add Firm"):
    if firm_name and firm_quota:
        st.session_state.firms.append({"name": firm_name, "quota": firm_quota})
        st.success(f"Firm {firm_name} added successfully!")
    else:
        st.error("Please enter both Firm Name and Quota.")

# Показване на добавените фирми
if st.session_state.firms:
    st.subheader("Added Firms")
    for firm in st.session_state.firms:
        st.write(f"{firm['name']} - Quota: {firm['quota']}")

# === Импортиране на студенти от Excel ===
st.header("Import Students from Excel")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        required_columns = {"Name", "Points"}
        if not required_columns.issubset(df.columns):
            st.error("Excel file must contain at least 'Name' and 'Points' columns.")
        else:
            imported_count = 0
            for _, row in df.iterrows():
                name = row["Name"]
                points = row["Points"]
                choices = [row[col] for col in df.columns if col.startswith("Choice") and pd.notna(row[col])]

                if name and pd.notna(points) and choices:
                    st.session_state.students.append({
                        "name": name,
                        "points": points,
                        "choices": choices
                    })
                    imported_count += 1
            st.success(f"{imported_count} students imported successfully!")
    except Exception as e:
        st.error(f"Error processing file: {e}")

# === Ръчно добавяне на студенти ===
st.header("Add Student")
student_name = st.text_input("Enter Student Name", key="student_name")
student_points = st.number_input("Enter Points", min_value=0, key="student_points")

student_choices = []
if st.session_state.firms:
    for i in range(len(st.session_state.firms)):
        firm_choice = st.selectbox(
            f"Select Firm Choice {i + 1}",
            options=[firm["name"] for firm in st.session_state.firms],
            key=f"choice_{i}"
        )
        student_choices.append(firm_choice)

if st.button("Add Student"):
    if student_name and student_points and student_choices:
        st.session_state.students.append({
            "name": student_name,
            "points": student_points,
            "choices": student_choices
        })
        st.success(f"Student {student_name} added successfully!")
    else:
        st.error("Please enter Student Name, Points, and make firm selections.")

# === Показване на студенти ===
if st.session_state.students:
    st.subheader("Added Students")
    for student in st.session_state.students:
        st.write(f"{student['name']} - Points: {student['points']}")
        st.write(f"Choices: {', '.join(student['choices'])}")

# === Класиране ===
if st.button("Classify Students"):
    students_sorted = sorted(st.session_state.students, key=lambda x: x["points"], reverse=True)
    firm_slots = {firm["name"]: firm["quota"] for firm in st.session_state.firms}
    classified = []

    for student in students_sorted:
        placed = False
        for choice in student["choices"]:
            if firm_slots.get(choice, 0) > 0:
                classified.append({"name": student["name"], "firm": choice})
                firm_slots[choice] -= 1
                placed = True
                break
        if not placed:
            classified.append({"name": student["name"], "firm": "Not Assigned"})

    st.subheader("Results")
    for entry in classified:
        st.write(f"{entry['name']} - Assigned to {entry['firm']}")
