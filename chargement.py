# =============================================================
# chargement.py — Lecture du fichier patients_bruts.txt
# =============================================================

import os

COLONNES = [
    "id", "nom", "prenom", "age",
    "telephone", "ville",
    "groupe_sanguin", "poids", "taille"
]


def charger_fichier(chemin_fichier):
    patients = []
    erreurs = []
    nb_lignes = 0

    if not os.path.exists(chemin_fichier):
        erreurs.append(f"Fichier introuvable : {chemin_fichier}")
        return patients, erreurs, nb_lignes

    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            lignes = f.readlines()
    except Exception as e:
        erreurs.append(f"Erreur lecture fichier : {e}")
        return patients, erreurs, nb_lignes

    if not lignes:
        erreurs.append("Fichier vide")
        return patients, erreurs, nb_lignes

    # Vérification en-tête
    header = lignes[0].strip().split(";")
    if header != COLONNES:
        erreurs.append(f"En-tête incorrect : {header}")

    # Lecture données
    for i, ligne in enumerate(lignes[1:], start=2):
        ligne = ligne.strip()
        if not ligne:
            continue

        champs = ligne.split(";")

        if len(champs) != len(COLONNES):
            erreurs.append(f"Ligne {i} invalide (colonnes incorrectes)")
            continue

        patient = {COLONNES[j]: champs[j] for j in range(len(COLONNES))}
        patient["_ligne"] = i

        patients.append(patient)
        nb_lignes += 1

    return patients, erreurs, nb_lignes


def afficher_apercu(patients, n=5):
    print("\n--- APERÇU DONNÉES ---")
    for p in patients[:n]:
        print(p)
    print("----------------------\n")