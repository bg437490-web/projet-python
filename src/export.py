# =============================================================
# Export.py — Creation des fichier json, rapport et csv
# Membre2 (Ababacar Sedikh Gueye) 
# =============================================================

import csv
import json
import os
from datetime import datetime

# Indication du programme ou va lire et ecrire c'est fichier de sorti

DOSSIER_DATA    = os.path.join(os.path.dirname(__file__), "..", "data")
DOSSIER_RAPPORT = os.path.join(os.path.dirname(__file__), "..", "rapport")

FICHIER_CSV     = os.path.join(DOSSIER_DATA,    "patients_propres.csv")
FICHIER_JSON    = os.path.join(DOSSIER_DATA,    "patients_propres.json")
FICHIER_RAPPORT = os.path.join(DOSSIER_RAPPORT, "rapport.txt")

EN_TETES_CSV = ["id", "nom", "prenom", "age", "telephone", "ville",
                "groupe_sanguin", "poids", "taille"]

# Creation des dossier de sorti
def _creer_dossiers():
    try:
        os.makedirs(DOSSIER_DATA,    exist_ok=True)
        os.makedirs(DOSSIER_RAPPORT, exist_ok=True)
    except OSError as e:
        print(f"[ERREUR] Impossible de créer les dossiers : {e}")

# Convertion en entier
def _to_int(valeur):
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return None

# Conversion en reel
def _to_float(valeur):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None

# Exportation des patient falide dans le fichier csv
def exporter_csv(patients_valides, chemin=None):
    if chemin is None:
        chemin = FICHIER_CSV
    _creer_dossiers()
    try:
        with open(chemin, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=EN_TETES_CSV, delimiter=";",
                                    extrasaction="ignore")
            writer.writeheader()
            for patient in patients_valides:
                ligne = {}
                for cle in EN_TETES_CSV:
                    valeur = str(patient.get(cle, "")).replace(";", ",")
                    ligne[cle] = valeur
                writer.writerow(ligne)
        print(f"[OK] CSV exporté → {chemin} ({len(patients_valides)} patients)")
        return True
    except (IOError, OSError) as e:
        print(f"[ERREUR] Impossible d'écrire le CSV : {e}")
        return False

# Creation du fichier json 
def exporter_json(patients_valides, chemin=None):
    if chemin is None:
        chemin = FICHIER_JSON
    _creer_dossiers()
    try:
        patients_serialisables = []
        for p in patients_valides:
            patients_serialisables.append({
                "id":             p.get("id"),
                "nom":            p.get("nom"),
                "prenom":         p.get("prenom"),
                "age":            _to_int(p.get("age")),
                "telephone":      p.get("telephone"),
                "ville":          p.get("ville"),
                "groupe_sanguin": p.get("groupe_sanguin"),
                "poids":          _to_float(p.get("poids")),
                "taille":         _to_int(p.get("taille")),
            })
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(patients_serialisables, f, ensure_ascii=False, indent=4)
        print(f"[OK] JSON exporté → {chemin} ({len(patients_valides)} patients)")
        return True
    except (IOError, OSError) as e:
        print(f"[ERREUR] Impossible d'écrire le JSON : {e}")
        return False

# Cadrage du rapport
def _section(titre, largeur=55):
    return f"\n{'─' * largeur}\n  {titre}\n{'─' * largeur}"

#Construction du rapport
def generer_rapport(resultats_nettoyage, statistiques, chemin=None):
    if chemin is None:
        chemin = FICHIER_RAPPORT
    _creer_dossiers()

    patients_valides = resultats_nettoyage.get("patients_valides", [])
    patients_rejetes = resultats_nettoyage.get("patients_rejetes", [])
    toutes_anomalies = resultats_nettoyage.get("toutes_anomalies", [])
    nb_doublons      = resultats_nettoyage.get("nb_doublons", 0)

    nb_lus     = statistiques.get("nb_total", 0)
    nb_valides = len(patients_valides)
    nb_rejetes = len(patients_rejetes)

    maintenant = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

    lignes = []
    lignes.append("=" * 55)
    lignes.append("   RAPPORT DE NETTOYAGE — DONNÉES MÉDICALES PATIENTS")
    lignes.append("=" * 55)
    lignes.append(f"  Généré le : {maintenant}")
    lignes.append("=" * 55)

    lignes.append(_section("RÉSUMÉ GÉNÉRAL"))
    lignes.append(f"  Lignes lues dans le fichier brut  : {nb_lus}")
    lignes.append(f"  Patients valides après nettoyage  : {nb_valides}")
    lignes.append(f"  Doublons supprimés                : {nb_doublons}")
    lignes.append(f"  Patients rejetés                  : {nb_rejetes}")

    lignes.append(_section("STATISTIQUES SUR LES PATIENTS VALIDES"))
    moy_age        = statistiques.get("moyenne_age")
    moy_poids      = statistiques.get("moyenne_poids")
    ville_freq     = statistiques.get("ville_plus_frequente")
    repartition_gs = statistiques.get("repartition_groupes", {})

    lignes.append(f"  Moyenne des âges        : {f'{moy_age:.2f} ans' if moy_age is not None else 'N/A'}")
    lignes.append(f"  Moyenne des poids       : {f'{moy_poids:.2f} kg' if moy_poids is not None else 'N/A'}")
    lignes.append(f"  Ville la plus fréquente : {ville_freq or 'N/A'}")

    if repartition_gs:
        lignes.append("\n  Répartition des groupes sanguins :")
        for groupe, nb in sorted(repartition_gs.items()):
            lignes.append(f"    {groupe:5s} : {nb} patient(s)")
    else:
        lignes.append("\n  Répartition des groupes sanguins : N/A")

    lignes.append(_section(f"ANOMALIES DÉTECTÉES ({len(toutes_anomalies)} au total)"))
    if toutes_anomalies:
        for anomalie in toutes_anomalies:
            lignes.append(f"  • {anomalie}")
    else:
        lignes.append("  Aucune anomalie détectée.")

    lignes.append(_section(f"PATIENTS REJETÉS ({nb_rejetes})"))
    if patients_rejetes:
        for item in patients_rejetes:
            p      = item.get("patient", {})
            id_p   = p.get("id", "?")
            nom_p  = f"{p.get('nom', '?')} {p.get('prenom', '?')}"
            lignes.append(f"\n  Patient #{id_p} — {nom_p}")
            for err in item.get("erreurs", []):
                lignes.append(f"    → {err}")
    else:
        lignes.append("  Aucun patient rejeté.")

    lignes.append("\n" + "=" * 55)
    lignes.append("  Fin du rapport")
    lignes.append("=" * 55 + "\n")

    try:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("\n".join(lignes))
        print(f"[OK] Rapport généré → {chemin}")
        return True
    except (IOError, OSError) as e:
        print(f"[ERREUR] Impossible d'écrire le rapport : {e}")
        return False

# creation du fonction exporter pour faire appel au fichier json, csv et le rapport
def tout_exporter(resultats_nettoyage, statistiques):
    print("\n" + "─" * 45)
    print("  EXPORT DES DONNÉES")
    print("─" * 45)

    patients_valides = resultats_nettoyage.get("patients_valides", [])

    succes_csv     = exporter_csv(patients_valides)
    succes_json    = exporter_json(patients_valides)
    succes_rapport = generer_rapport(resultats_nettoyage, statistiques)

    print("─" * 45)
    if succes_csv and succes_rapport:
        print("  Exports obligatoires réussis (CSV + rapport).")
        if not succes_json:
            print("  [WARN] Export JSON (bonus) échoué.")
    else:
        print("  Certains exports obligatoires ont échoué. Vérifiez les messages ci-dessus.")
    print("─" * 45 + "\n")

    return succes_csv and succes_rapport