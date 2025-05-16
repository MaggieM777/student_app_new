import streamlit as st
import pandas as pd

# Инициализация на session_state ако няма данни
if "firms" not in st.session_state:
    st.session_state.firms = []

if "students" not in st.session_state:
    st.session_state.students = []

if "imported_students" not in st.session_state:
    st.session_state.imported_students = []

st.title("Student-Firm Application")

# --- Добавяне на фирми ръчно ---
st.header("Добави фирма")
firm_name = st.text_input("Име на фирмата", key="firm_name_input")
firm_quota = st.number_input("Квота", min_value=1, step=1, key="firm_quota_input")

if st.button("Добави фирма"):
    if firm_name.strip() and firm_quota > 0:
        st.session_state.firms.append({"name": firm_name.strip(), "quota": firm_quota})
        st.success(f"Фирма '{firm_name.strip()}' добавена успешно!")
        st.experimental_rerun()
    else:
        st.error("Моля, въведете име на фирма и валидна квота.")

# Показване на добавените фирми
if st.session_state.firms:
    st.subheader("Добавени фирми")
    for firm in st.session_state.firms:
        st.write(f"{firm['name']} - Квота: {firm['quota']}")

st.markdown("---")

# --- Импортиране на студенти от Excel ---
st.header("Импортиране на студенти от Excel")
uploaded_file = st.file_uploader("Качи Excel файл (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Колони в Excel файла:", list(df.columns))

        # Съответствие на колони в Excel с имената, които очакваме
        required_columns = ["Име", "Точки"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Excel файлът трябва да съдържа поне колоните: {', '.join(required_columns)}.")
        else:
            temp_students = []
            for _, row in df.iterrows():
                name = row["Име"]
                points = row["Точки"]
                # Взимаме колоните за желанията (които започват с "Желание")
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
                before = len(st.session_state.students)
                st.session_state.students.extend(st.session_state.imported_students)
                st.session_state.imported_students = []
                st.success(f"Добавени {len(st.session_state.students) - before} студенти.")
                st.experimental_rerun()
    except Exception as e:
        st.error(f"Грешка при обработка на файла: {e}")

st.markdown("---")

# --- Ръчно добавяне на студенти ---
st.header("Добави студент")

student_name = st.text_input("Име на студента", key="student_name_input")
student_points = st.number_input("Точки", min_value=0, step=1, key="student_points_input")

if st.session_state.firms:
    student_choices = []
    for i in range(6):  # 6 желания
        choice = st.selectbox(f"Избери фирма - предпочитание {i+1}",
                              options=[firm["name"] for firm in st.session_state.firms],
                              key=f"choice_{i}")
        student_choices.append(choice)
else:
    st.info("Моля, добавете поне една фирма, за да можете да избирате фирми за студентите.")

if st.button("Добави студент"):
    if student_name.strip() and student_points >= 0 and student_choices:
        st.session_state.students.append({
            "name": student_name.strip(),
            "points": student_points,
            "choices": student_choices
        })
        st.success(f"Студентът '{student_name.strip()}' добавен успешно!")
        st.experimental_rerun()
    else:
        st.error("Моля, въведете име, точки и изберете фирми за всички желания.")

# Показване на всички студенти (от файл и ръчно)
if st.session_state.students:
    st.subheader("Добавени студенти")
    for student in st.session_state.students:
        st.write(f"{student['name']} - Точки: {student['points']}")
        st.write(f"Желания: {', '.join(student['choices'])}")

st.markdown("---")

# --- Класиране на студентите ---
if st.button("Класирай студентите"):
    if not st.session_state.firms:
        st.error("Няма добавени фирми за класиране.")
    elif not st.session_state.students:
        st.error("Няма добавени студенти за класиране.")
    else:
        # Сортиране на студентите по точки низходящо
        students_sorted = sorted(st.session_state.students, key=lambda x: x["points"], reverse=True)

        # Квоти за фирмите
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
                classified.append({"name": student["name"], "firm": "Не е класиран"})

        st.subheader("Резултати от класирането")
        for c in classified:
            st.write(f"{c['name']} - Класиран във фирма: {c['firm']}")
