# avenir_du_peuple_app/pages/3_💰_Dépenses.py
import streamlit as st
from database import get_connection, init_db
import pandas as pd

def add_expense():
    st.subheader("Ajouter une dépense")
    with st.form("expense"):
        title = st.text_input("Titre")
        date = st.date_input("Date")
        amount = st.number_input("Montant", min_value=0.0, value=0.0)
        academic_year = st.text_input("Année scolaire (ex: 2024-2025)")
        classe = st.text_input("Classe (laisser vide si générale)")
        note = st.text_area("Note")
        submit = st.form_submit_button("Ajouter dépense")
        if submit:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO academic_years (name) VALUES (?)", (academic_year,))
            cur.execute("INSERT OR IGNORE INTO classes (name) VALUES (?)", (classe or "GENERAL",))
            cur.execute("SELECT id FROM academic_years WHERE name = ?", (academic_year,))
            ay = cur.fetchone()['id']
            cur.execute("SELECT id FROM classes WHERE name = ?", (classe or "GENERAL",))
            cid = cur.fetchone()['id']
            cur.execute("INSERT INTO expenses (title, date, amount, academic_year_id, class_id, note) VALUES (?,?,?,?,?,?)",
                        (title, date.isoformat(), amount, ay, cid, note))
            conn.commit()
            conn.close()
            st.success("Dépense ajoutée.")

def page():
    st.header("Dépenses")
    init_db()
    add_expense()
    conn = get_connection()
    df = pd.read_sql_query("SELECT e.*, a.name as year_name, c.name as class_name FROM expenses e LEFT JOIN academic_years a ON e.academic_year_id=a.id LEFT JOIN classes c ON e.class_id=c.id ORDER BY date DESC", conn)
    conn.close()
    st.subheader("Liste des dépenses")
    st.dataframe(df)

if __name__ == "__main__":
    page()
