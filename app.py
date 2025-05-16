import streamlit as st
import pandas as pd

# Инициализация на session_state
if "firms" not in st.session_state:
    st.session_state.firms = []

if "students" not in st.session_state:
    st.session_state.students = []

if "imported_students" not in st.session_state:
    st.session_state.imported_students = []

st.title("Student-Firm Application")

# Ръчно добавяне на фирми
st.header("Добави фирма")
firm_name = st.text_input("Име на фирмата")
firm_quota = st.number_input("Квота", min_value=1)

if st.button("Добави фирма"):
    if firm_name and firm_quota:
        st.session_state.firms.append({"name": firm_name, "quota": firm_quota})
        st.success(f"Фирма {firm_name} добавена успешно!")
    else:
        st.error("Моля, въведете име на фирмата и квота.")

# Показване на фирми
if st.session_state.firms:
    st.subheader("Добавени фирми")
    for firm in st.session_state.firms:
        st.write(f"{firm['name']} - Квота: {firm['quota']}")

# Импортиране на студенти от Excel
st.header("Импортиране на студенти от Excel")
uploaded_file = st.file_uploader("Качете Excel файл (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Колони в Excel файла:", list(df.columns))
        df.columns = df.columns.str.strip().str.replace('\n', '').str.replace('\r', '').str.replace(r'\s+', ' ', regex=True)

        required_columns = {"Име", "Точки"}
        if not required_columns.issubset(df.columns):
            st.error("Excel файлът трябва да съдържа поне колоните 'Име' и 'Точки'.")
        else:
            # Събираме студентите в временен списък
            temp_students = []
            for _, row in df.iterrows():
                name = row["Име"]
                points = row["Точки"]
                choices = [row[col] for col in df.columns if col.startswith("Желание") and pd.notna(row[col])]
                if name and pd.notna(points) and choices:
                    temp_students.append({
                        "name": name,
                        "points": points,
                        "choices": choices
                    })
            st.session_state.imported_students = temp_students
            st.success(f"Файлът е прочетен успешно! Намерени студенти: {len(temp_students)}")

            if st.button("Добави импортираните студенти към списъка"):
                count_before = len(st.session_state.students)
                st.session_state.students.extend(st.session_state.imported_students)
                st.session_state.imported_students = []
                st.success(f"Добавени {len(st.session_state.students) - count_before} студенти.")
    except Exception as e:
        st.error(f"Грешка при обработка на файла: {e}")

# Ръчно добавяне на студенти
if st.session_state.firms:
    st.header("Добави студент")
    student_name = st.text_input("Име на студента", key="student_name")
    student_points = st.number_input("Точки", min_value=0, key="student_points")

    student_choices = []
    for i in range(len(st.session_state.firms)):
        firm_choice = st.selectbox(
            f"Избери фирма - предпочитание {i + 1}",
            options=[firm["name"] for firm in st.session_state.firms],
            key=f"choice_{i}"
        )
        student_choices.append(firm_choice)

    if st.button("Добави студент"):
        if student_name and student_points and student_choices:
            st.session_state.students.append({
                "name": student_name,
                "points": student_points,
                "choices": student_choices
            })
            st.success(f"Студент {student_name} добавен успешно!")
        else:
            st.error("Моля, въведете име, точки и изберете фирми.")
else:
    st.info("Моля, добавете поне една фирма, преди да добавяте студенти.")

# Показване на студенти
if st.session_state.students:
    st.subheader("Добавени студенти")
    for student in st.session_state.students:
        st.write(f"{student['name']} - Точки: {student['points']}")
        st.write(f"Желания: {', '.join(student['choices'])}")

# Класиране
if st.button("Класирай студентите"):
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
            classified.append({"name": student["name"], "firm": "Не е разпределен"})

    st.subheader("Резултати")
    for entry in classified:
        st.write(f"{entry['name']} - Разпределен във фирма: {entry['firm']}")
