import streamlit as st

# Списъци за студентите, фирмите и резултатите
students = []
firms = []

# Функция за добавяне на студент
def add_student():
    name = st.text_input("Student Name")
    points = st.number_input("Points", min_value=0)
    choices = []
    for i in range(len(firms)):
        choice = st.selectbox(f"Choice for Firm {i+1}", [firm['name'] for firm in firms])
        choices.append(choice)
    
    if st.button("Add Student"):
        students.append({"name": name, "points": points, "choices": choices})
        st.success(f"Student {name} added!")

# Функция за добавяне на фирма
def add_firm():
    name = st.text_input("Firm Name")
    quota = st.number_input("Quota", min_value=1)
    
    if st.button("Add Firm"):
        firms.append({"name": name, "quota": quota})
        st.success(f"Firm {name} added!")

# Функция за класифициране на студентите
def classify_students():
    sorted_students = sorted(students, key=lambda x: x['points'], reverse=True)
    
    firm_slots = {firm['name']: firm['quota'] for firm in firms}
    placements = []
    
    for student in sorted_students:
        placed = False
        for choice in student['choices']:
            if firm_slots.get(choice, 0) > 0:
                placements.append(f"{student['name']} -> {choice}")
                firm_slots[choice] -= 1
                placed = True
                break
        if not placed:
            placements.append(f"{student['name']} -> Not Assigned")
    
    st.write("### Results")
    for placement in placements:
        st.write(placement)

# Заглавие на приложението
st.title("Student-Firm Assignment App")

# Добавяне на фирми и студенти
st.header("Add Firms")
add_firm()

st.header("Add Students")
add_student()

# Бутон за класифициране на студентите
if st.button("Classify Students"):
    if not students or not firms:
        st.error("Please add both students and firms first!")
    else:
        classify_students()

# Показване на текущите добавени фирми и студенти
st.write("### Current Firms")
for firm in firms:
    st.write(f"{firm['name']} (Quota: {firm['quota']})")

st.write("### Current Students")
for student in students:
    st.write(f"Name: {student['name']}, Points: {student['points']}, Choices: {', '.join(student['choices'])}")
