import streamlit as st
import pandas as pd

# Инициализация на session_state, ако няма данни
if "firms" not in st.session_state:
    st.session_state.firms = []

if "students" not in st.session_state:
    st.session_state.students = []

if "imported_students" not in st.session_state:
    st.session_state.imported_students = []

# Заглавие на приложението
st.title("Student-Firm Application")

# Функция за показване на всички студенти (ръчно добавени + импортирани)
def show_all_students():
    all_students = st.session_state.students + st.session_state.imported_students
    if all_students:
        st.subheader("Всички студенти")
        for student in all_students:
            st.write(f"{student['name']} - Точки: {student['points']}")
            st.write(f"Желания: {', '.join(student['choices'])}")
    else:
        st.info("Все още няма добавени студенти.")

# Форма за добавяне на фирми ръчно
st.header("Добави фирма")
firm_name = st.text_input("Име на фирмата", key="firm_name_input")
firm_quota = st.number_input("Квота", min_value=1, step=1, key="firm_quota_input")

if st.button("Добави фирма"):
    if firm_name and firm_quota > 0:
        st.session_state.firms.append({"name": firm_name, "quota": firm_quota})
        st.success(f"Фирма '{firm_name}' добавена успешно!")
        st.experimental_rerun()
    else:
        st.error("Моля, въведете име и квота на фирмата.")

# Показване на добавените фирми
if st.session_state.firms:
    st.subheader("Добавени фирми")
    for firm in st.session_state.firms:
        st.write(f"{firm['name']} - Квота: {firm['quota']}")
else:
    st.info("Все още няма добавени фирми.")

# Форма за добавяне на студенти ръчно
st.header("Добави студент")
student_name = st.text_input("Име на студента", key="student_name_input")
student_points = st.number_input("Точки", min_value=0, step=1, key="student_points_input")

student_choices = []
if st.session_state.firms:
    for i in range(6):  # 6 желания
        choice = st.selectbox(f"Избери фирма - предпочитание {i+1}", options=[firm["name"] for firm in st.session_state.firms], key=f"choice_{i}")
        student_choices.append(choice)

if st.button("Добави студент"):
    if student_name and student_points >= 0 and student_choices:
        st.session_state.students.append({
            "name": student_name,
            "points": student_points,
            "choices": student_choices
        })
        st.success(f"Студент '{student_name}' добавен успешно!")
        st.experimental_rerun()
    else:
        st.error("Моля, въведете име, точки и направете избор на фирми.")

# Показване на всички студенти (ръчно + импорт)
show_all_students()

# Импортиране на студенти от Excel
st.header("Импортиране на студенти от Excel")
uploaded_file = st.file_uploader("Качи Excel файл (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Ако заглавията в твоя файл са на 5-ти ред (индекс 4), смени ако трябва
        df = pd.read_excel(uploaded_file, header=4) 

        st.write("Колони в Excel файла:", list(df.columns))

        required_columns = ["Ученик :", "Точки"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Excel файлът трябва да съдържа поне колоните: {', '.join(required_columns)}.")
        else:
            temp_students = []
            for _, row in df.iterrows():
                name = row["Ученик :"]
                points = row["Точки"]
                # Вземаме всички колони с желания, започващи с "Желание"
                choices = [row[col] for col in df.columns if str(col).startswith("Желание") and pd.notna(row[col])]
                if pd.notna(name) and pd.notna(points) and choices:
                    temp_students.append({
                        "name": str(name),
                        "points": int(points),
                        "choices": choices
                    })
            st.session_state.imported_students = temp_students
            st.success(f"Файлът е прочетен успешно! Намерени студенти: {len(temp_students)}")
            show_all_students()

    except Exception as e:
        st.error(f"Грешка при обработка на файла: {e}")

# Класиране на студентите
st.header("Класиране на студенти")

if st.button("Класирай студенти"):
    if not st.session_state.firms:
        st.error("Моля, добавете поне една фирма.")
    else:
        all_students = st.session_state.students + st.session_state.imported_students
        if not all_students:
            st.error("Няма добавени студенти за класиране.")
        else:
            # Сортиране по точки (намаляващо)
            students_sorted = sorted(all_students, key=lambda x: x["points"], reverse=True)

            # Квоти за фирмите
            firm_slots = {firm["name"]: firm["quota"] for firm in st.session_state.firms}

            classified = []
            for student in students_sorted:
                placed = False
                for choice in student["choices"]:
                    if choice in firm_slots and firm_slots[choice] > 0:
                        classified.append({"name": student["name"], "firm": choice})
                        firm_slots[choice] -= 1
                        placed = True
                        break
                if not placed:
                    classified.append({"name": student["name"], "firm": "Не е класиран"})

            # Показване на резултатите
            st.subheader("Резултати от класирането")
            for entry in classified:
                st.write(f"{entry['name']} - Класиран във фирма: {entry['firm']}")
