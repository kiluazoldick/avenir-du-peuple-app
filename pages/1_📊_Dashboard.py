# avenir_du_peuple_app/pages/1_📊_Dashboard.py
import streamlit as st
import pandas as pd
from database import get_connection
import plotly.express as px
import io

# ------------------- Fonctions utilitaires -------------------
def load_students_df(year=None):
    conn = get_connection()
    query = """
    SELECT s.id, s.full_name, s.date_inscription, s.class_id, s.academic_year_id,
           s.inscription_fee, s.tranche1, s.tranche2,
           (s.inscription_fee + s.tranche1 + s.tranche2) as total_paye,
           c.name as class_name, a.name as year_name
    FROM students s
    LEFT JOIN classes c ON s.class_id=c.id
    LEFT JOIN academic_years a ON s.academic_year_id=a.id
    """
    params = None
    if year:
        query += " WHERE a.name = ?"
        params = (year,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # S'assurer que les colonnes numériques existent et sont valides
    numeric_cols = ["inscription_fee", "tranche1", "tranche2", "total_paye"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0
    # Si class_name ou full_name manquant
    for col in ["class_name", "full_name"]:
        if col not in df.columns:
            df[col] = ""
    return df

def load_expenses_df(year=None):
    conn = get_connection()
    query = """
    SELECT e.id, e.title, e.date, e.amount, e.note, c.name as class_name, a.name as year_name
    FROM expenses e
    LEFT JOIN classes c ON e.class_id=c.id
    LEFT JOIN academic_years a ON e.academic_year_id=a.id
    """
    params = None
    if year:
        query += " WHERE a.name = ?"
        params = (year,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    else:
        df["amount"] = 0
    # Si class_name ou title manquant
    for col in ["class_name", "title"]:
        if col not in df.columns:
            df[col] = ""
    return df

def generate_report_excel(df_students, df_expenses):
    total_revenus = df_students["total_paye"].sum() if not df_students.empty else 0
    total_depenses = df_expenses["amount"].sum() if not df_expenses.empty else 0
    benefice = total_revenus - total_depenses

    totals = pd.DataFrame([{
        "Total Revenus": total_revenus,
        "Total Dépenses": total_depenses,
        "Bénéfice": benefice
    }])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_students.to_excel(writer, index=False, sheet_name="Élèves")
        df_expenses.to_excel(writer, index=False, sheet_name="Dépenses")
        totals.to_excel(writer, index=False, sheet_name="Résumé")
    output.seek(0)
    return output

# ------------------- Page Dashboard -------------------
def page():
    st.set_page_config(page_title="Dashboard", layout="wide")
    st.header("Dashboard")

    # Récupérer les années
    conn = get_connection()
    yrs = pd.read_sql_query("SELECT name FROM academic_years ORDER BY name DESC", conn)
    conn.close()
    years = yrs['name'].tolist()

    year = st.selectbox("Année scolaire", ["Toutes"] + years)
    selected_year = None if year == "Toutes" else year

    # Chargement des données
    df_students = load_students_df(selected_year)
    df_expenses = load_expenses_df(selected_year)

    # ---------------- Stats rapides ----------------
    st.subheader("Stats rapides")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total élèves", int(df_students.shape[0]))
    col2.metric(
        "Total revenus (somme Total paye)",
        f"{df_students['total_paye'].sum():,.0f}" if not df_students.empty else "0"
    )
    col3.metric(
        "Total inscriptions",
        f"{df_students['inscription_fee'].sum():,.0f}" if not df_students.empty else "0"
    )
    col4.metric(
        "Total 1ere tranche",
        f"{df_students['tranche1'].sum():,.0f}" if not df_students.empty else "0"
    )

    # ---------------- Revenus par classe ----------------
    st.subheader("Revenus par classe")
    if not df_students.empty:
        rev_by_class = df_students.groupby("class_name")[["inscription_fee","tranche1","tranche2","total_paye"]].sum().reset_index().fillna(0)
        rev_long = rev_by_class.melt(id_vars="class_name", var_name="type", value_name="amount")
        fig = px.bar(rev_long, x="class_name", y="amount", color="type", barmode="group", title="Revenus par classe et type")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée de revenus.")

    # ---------------- Nombre d'élèves par classe ----------------
    st.subheader("Nombre d'élèves par classe")
    if not df_students.empty:
        count = df_students.groupby("class_name").size().reset_index(name="count")
        fig2 = px.pie(count, names="class_name", values="count", title="Répartition des élèves par classe")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Aucune donnée d'élèves.")

    # ---------------- Table de données ----------------
    st.subheader("Détail élèves")
    if not df_students.empty:
        st.dataframe(df_students.sort_values(["class_name","full_name"]), height=400)
    else:
        st.info("Aucune donnée d'élèves à afficher.")

    # ---------------- Téléchargement du rapport ----------------
    st.subheader("Télécharger le rapport financier")
    excel_file = generate_report_excel(df_students, df_expenses)
    st.download_button(
        label="📥 Télécharger le rapport Excel",
        data=excel_file,
        file_name=f"rapport_financier_{year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ------------------- Exécution directe -------------------
if __name__ == "__main__":
    page()
