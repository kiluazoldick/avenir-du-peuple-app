# avenir_du_peuple_app/app.py
import streamlit as st
from database import init_db
import os

def main():
    st.set_page_config(page_title="Avenir du Peuple - School Manager", layout="wide")
    st.title("Avenir du Peuple — School Manager App")

    # Initialiser la base de données si nécessaire
    init_db()

    # ------------------- Mode d'emploi détaillé -------------------
    st.header("Bienvenue sur Avenir du Peuple - School Manager")
    st.markdown("""
    Cette application est conçue pour vous aider à **gérer facilement votre école**, suivre les élèves, leurs paiements et générer des rapports financiers clairs. Voici comment vous pouvez l'utiliser :

    ### 1️⃣ Dashboard
    - **Vue d’ensemble** : voyez rapidement le nombre d'élèves, les revenus totaux, et les paiements par type.
    - **Graphiques** : découvrez la répartition des élèves et des revenus par classe.
    - **Détails des élèves** : consultez la liste complète avec les paiements effectués.
    - **Téléchargement** : vous pouvez générer un **rapport Excel** complet pour garder une trace.

    ### 2️⃣ Gestion des élèves
    - **Ajouter un nouvel élève** : renseignez le nom, la classe et l'année scolaire.
    - **Modifier un élève** : mettez à jour les informations ou les paiements.
    - **Suivi des paiements** : visualisez combien chaque élève a payé et ce qu’il reste à payer.

    ### 3️⃣ Dépenses
    - **Ajouter une dépense** : saisissez le titre, la date et le montant.
    - **Suivi** : voyez toutes les dépenses par classe ou par année scolaire.
    - **Impact sur le budget** : les dépenses sont prises en compte dans les rapports financiers.

    ### 4️⃣ Rapports
    - **Génération automatique** : créez des relevés financiers clairs, par année scolaire.
    - **Téléchargement Excel** : gardez un historique complet de tous les paiements et dépenses.
    - **Résumé** : consultez directement le total des revenus, des dépenses et le bénéfice.

    ### ⚡ Conseils d’utilisation
    - Sélectionnez l'année scolaire en haut de chaque page pour filtrer les informations.
    - Les totaux sont mis à jour automatiquement à chaque changement.
    - Les rapports téléchargés contiennent toutes les informations visibles sur l'application.

    **C’est simple, rapide et pratique pour suivre la gestion financière de votre école !**
    """)

    st.markdown("---")
    st.markdown("Utilisez le menu sur la gauche pour naviguer entre le **Dashboard**, **Gestion des élèves**, **Dépenses** et **Rapports**.")

if __name__ == "__main__":
    main()
