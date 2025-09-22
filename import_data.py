# avenir_du_peuple_app/import_data.py
import pandas as pd
from pathlib import Path
from database import get_connection, init_db
from datetime import datetime
import sqlite3

def clean_and_load_excel(path, academic_year_name="2024-2025"):
    # Lecture brute du fichier
    df = pd.read_excel(path, sheet_name=0, header=0)
    # Très souvent la première ligne contient les en-têtes réels (voir ton fichier)
    # Si on détecte que la première ligne est "Nom et prenom", on la prend comme header:
    first_row = df.iloc[0].tolist()
    if "Nom et prenom" in first_row or "Nom et prénom" in first_row or "Nom" in first_row:
        # set header from the first row and drop it
        df.columns = df.iloc[0].fillna("").astype(str).tolist()
        df = df[1:].reset_index(drop=True)

    # Normaliser noms de colonnes
    col_map = {}
    for col in df.columns:
        c = str(col).strip().lower()
        if "nom" in c:
            col_map[col] = "full_name"
        elif "date" in c:
            col_map[col] = "date_inscription"
        elif "classe" in c:
            col_map[col] = "classe"
        elif "inscription" in c and "1ere" not in c and "tranche" not in c:
            col_map[col] = "inscription_fee"
        elif "1ere" in c or ("1" in c and "tranche" in c):
            col_map[col] = "tranche1"
        elif "2e" in c or ("2" in c and "tranche" in c):
            col_map[col] = "tranche2"
        elif "reste" in c:
            col_map[col] = "reste"
        elif "total" in c:
            col_map[col] = "total_paye"
        elif "status" in c:
            col_map[col] = "status"
    df = df.rename(columns=col_map)

    # Garder seulement colonnes utiles
    keep = ["full_name","date_inscription","classe","inscription_fee","tranche1","tranche2","reste","total_paye","status"]
    df = df[[c for c in keep if c in df.columns]]

    # Convert types
    # date_inscription may be string or datetime
    if "date_inscription" in df.columns:
        df["date_inscription"] = pd.to_datetime(df["date_inscription"], errors="coerce").dt.strftime("%Y-%m-%d")

    for col in ["inscription_fee","tranche1","tranche2","reste","total_paye"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Fill missing classe
    if "classe" in df.columns:
        df["classe"] = df["classe"].fillna("Non-definie")

    # Insert into DB
    conn = get_connection()
    cur = conn.cursor()
    # Ensure DB exists
    init_db()

    # Add academic year
    cur.execute("INSERT OR IGNORE INTO academic_years (name) VALUES (?)", (academic_year_name,))
    cur.execute("SELECT id FROM academic_years WHERE name = ?", (academic_year_name,))
    academic_year_id = cur.fetchone()[0]

    # Upsert classes
    classes = df["classe"].unique().tolist() if "classe" in df.columns else []
    for c in classes:
        cur.execute("INSERT OR IGNORE INTO classes (name) VALUES (?)", (str(c),))
    conn.commit()

    # Map class name -> id
    class_map = {}
    cur.execute("SELECT id, name FROM classes")
    for r in cur.fetchall():
        class_map[r["name"]] = r["id"]

    # Insert students and payments
    inserted = 0
    for _, row in df.iterrows():
        full_name = str(row.get("full_name","")).strip()
        if not full_name:
            continue
        class_name = row.get("classe")
        class_id = class_map.get(class_name)
        inscription_fee = float(row.get("inscription_fee",0) or 0)
        tranche1 = float(row.get("tranche1",0) or 0)
        tranche2 = float(row.get("tranche2",0) or 0)
        reste = float(row.get("reste",0) or 0)
        total_paye = float(row.get("total_paye", inscription_fee+tranche1+tranche2) or 0)
        date_insc = row.get("date_inscription", None)
        status = row.get("status", None)

        cur.execute("""
            INSERT INTO students (full_name, date_inscription, class_id, academic_year_id,
                                  inscription_fee, tranche1, tranche2, reste, total_paye, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (full_name, date_insc, class_id, academic_year_id,
              inscription_fee, tranche1, tranche2, reste, total_paye, status))
        student_id = cur.lastrowid

        # Optionally: create payments rows if amounts > 0
        if inscription_fee > 0:
            cur.execute("INSERT INTO payments (student_id, academic_year_id, payment_type, amount, date) VALUES (?,?,?,?,?)",
                        (student_id, academic_year_id, "inscription", inscription_fee, date_insc))
        if tranche1 > 0:
            cur.execute("INSERT INTO payments (student_id, academic_year_id, payment_type, amount, date) VALUES (?,?,?,?,?)",
                        (student_id, academic_year_id, "tranche1", tranche1, date_insc))
        if tranche2 > 0:
            cur.execute("INSERT INTO payments (student_id, academic_year_id, payment_type, amount, date) VALUES (?,?,?,?,?)",
                        (student_id, academic_year_id, "tranche2", tranche2, date_insc))

        inserted += 1

    conn.commit()
    conn.close()
    return {"inserted": inserted, "rows": len(df)}

if __name__ == "__main__":
    path = Path(__file__).parent / "../revenue avenir du peuple.xlsx"
    r = clean_and_load_excel(path, academic_year_name="2024-2025")
    print("Inserted:", r)
