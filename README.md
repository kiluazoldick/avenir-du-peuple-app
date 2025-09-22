# Avenir du Peuple - School Manager App

Application de gestion scolaire pour la saisie des élèves, suivi des paiements et génération de rapports financiers.

## Installation locale

1. Cloner le repo :
```bash
git clone https://github.com/kiluazoldick/avenir-du-peuple-app.git
cd avenir-du-peuple-app
```
2. Installer les dépendances :

```pip install -r requirements.txt```


3. Lancer l’application :

```streamlit run app.py```

4. Contenu

app.py : point d’entrée de l’application.

database.py : gestion de la base SQLite.

pages/ : pages Streamlit (Dashboard, Élèves, Dépenses, Rapports).

school_data.db : base de données initiale.

requirements.txt : dépendances Python.

5. Déploiement

L’application peut être déployée sur Streamlit Cloud
.

Créer un compte Streamlit.

Lier ton dépôt GitHub.

Sélectionner le fichier app.py comme point d’entrée.

Déployer.
