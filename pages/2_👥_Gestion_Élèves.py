# avenir_du_peuple_app/pages/2_👥_Gestion_Elèves.py
import streamlit as st
import pandas as pd
from database import get_connection, init_db
from pathlib import Path

def list_students(year=None):
    conn = get_connection()
    q = "SELECT s.*, c.name as class_name, a.name as year_name FROM students s LEFT JOIN classes c ON s.class_id=c.id LEFT JOIN academic_years a ON s.academic_year_id=a.id"
    if year and year != "Toutes":
        df = pd.read_sql_query(q + " WHERE a.name = ?", conn, params=(year,))
    else:
        df = pd.read_sql_query(q, conn)
    conn.close()
    return df

def add_student_form():
    st.subheader("Ajouter un élève")
    with st.form("add_student"):
        full_name = st.text_input("Nom complet")
        date_insc = st.date_input("Date d'inscription")
        classe = st.text_input("Classe (ex: SIL)")
        academic_year = st.text_input("Année scolaire (ex: 2024-2025)")
        inscription = st.number_input("Inscription", value=0)
        tranche1 = st.number_input("1ère tranche", value=0)
        tranche2 = st.number_input("2e tranche", value=0)
        status = st.text_input("Status (ex: PARTI)")
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            conn = get_connection()
            cur = conn.cursor()
            # ensure classes and year exist
            cur.execute("INSERT OR IGNORE INTO academic_years (name) VALUES (?)", (academic_year,))
            cur.execute("INSERT OR IGNORE INTO classes (name) VALUES (?)", (classe,))
            cur.execute("SELECT id FROM academic_years WHERE name = ?", (academic_year,))
            ay = cur.fetchone()['id']
            cur.execute("SELECT id FROM classes WHERE name = ?", (classe,))
            cid = cur.fetchone()['id']
            total = inscription + tranche1 + tranche2
            cur.execute("""
            INSERT INTO students (full_name, date_inscription, class_id, academic_year_id,
                                  inscription_fee, tranche1, tranche2, reste, total_paye, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (full_name, date_insc.isoformat(), cid, ay, inscription, tranche1, tranche2, 0, total, status))
            conn.commit()
            conn.close()
            st.success("Élève ajouté.")

def page():
    st.header("Gestion des Élèves")
    init_db()
    conn = get_connection()
    yrs = pd.read_sql_query("SELECT name FROM academic_years ORDER BY name DESC", conn)
    years = ["Toutes"] + yrs['name'].tolist()
    conn.close()
    year = st.selectbox("Filtrer par année", years)
    add_student_form()
    df = list_students(year if year!="Toutes" else None)
    st.subheader("Liste")
    st.dataframe(df)

if __name__ == "__main__":
    page()
