import streamlit as st

# Инициализация на session_state ако няма данни
if "firms" not in st.session_state:
    st.session_state.firms = []

if "students" not in st.session_state:
    st.session_state.students = []

# Заглавие на приложението
st.title("Student-Firm Application")

# Формата за добавяне на фирми
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

# Формата за добавяне на студенти
st.header("Add Student")
student_name = st.text_input("Enter Student Name")
student_points = st.number_input("Enter Points", min_value=0)

# Падащо меню за избор на фирма за студентите
if st.session_state.firms:
    student_choices = []
    for i in range(len(st.session_state.firms)):  # Променяме тук броя на падащите менюта
        firm_choice = st.selectbox(f"Select Firm Choice {i+1}", options=[firm["name"] for firm in st.session_state.firms], key=f"choice_{i}")
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
        st.error("Please enter Student Name, Points and make selections for at least one Firm.")

# Показване на добавените студенти
if st.session_state.students:
    st.subheader("Added Students")
    for student in st.session_state.students:
        st.write(f"{student['name']} - Points: {student['points']}")
        st.write(f"Choices: {', '.join(student['choices'])}")

# Логика за класиране на студентите
if st.button("Classify Students"):
    # Сортиране на студентите по точки
    students_sorted = sorted(st.session_state.students, key=lambda x: x["points"], reverse=True)

    # Поставяне на студентите в съответните фирми
    classified = []
    firm_slots = {firm["name"]: firm["quota"] for firm in st.session_state.firms}

    for student in students_sorted:
        placed = False
        for choice in student["choices"]:
            if firm_slots[choice] > 0:
                classified.append({"name": student["name"], "firm": choice})
                firm_slots[choice] -= 1
                placed = True
                break
        if not placed:
            classified.append({"name": student["name"], "firm": "Not Assigned"})

    # Показване на резултатите
    st.subheader("Results")
    for entry in classified:
        st.write(f"{entry['name']} - Assigned to {entry['firm']}")

