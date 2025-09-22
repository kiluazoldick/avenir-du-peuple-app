# avenir_du_peuple_app/app.py
import streamlit as st
from database import init_db
import os

def main():
    st.set_page_config(page_title="Avenir du Peuple - School Manager", layout="wide")
    st.title("Avenir du Peuple — School Manager App")

    # Init DB if needed
    init_db()

    st.markdown("""
    Utilise les pages du menu (Dashboard, Gestion Élèves, Dépenses, Rapports).
    """)

if __name__ == "__main__":
    main()
