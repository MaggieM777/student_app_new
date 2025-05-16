import pandas as pd

st.header("Import Students from Excel")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        required_columns = {"Name", "Points"}
        if not required_columns.issubset(df.columns):
            st.error("Excel file must contain at least 'Name' and 'Points' columns.")
        else:
            for _, row in df.iterrows():
                name = row["Name"]
                points = row["Points"]
                # Събираме всички колони, започващи с 'Choice' като желания
                choices = [row[col] for col in df.columns if col.startswith("Choice") and pd.notna(row[col])]

                if name and pd.notna(points) and choices:
                    st.session_state.students.append({
                        "name": name,
                        "points": points,
                        "choices": choices
                    })
            st.success("Students imported successfully!")
    except Exception as e:
        st.error(f"Error processing file: {e}")
