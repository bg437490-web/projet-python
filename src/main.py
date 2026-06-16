# =============================================================
# main.py — Menu principal du système de nettoyage médical
# Fait ensemble par les deux étudiants (Version Finale Stabilisée)
# =============================================================

import os
import sys

# 1. Résolution dynamique et robuste du dossier des modules (src)
chemin_script = os.path.dirname(os.path.abspath(__file__))
if chemin_script not in sys.path:
    sys.path.insert(0, chemin_script)

# Si un sous-dossier 'src' existe, on l'ajoute au PATH
chemin_src = os.path.join(chemin_script, "src")
if os.path.exists(chemin_src) and chemin_src not in sys.path:
    sys.path.insert(0, chemin_src)

# 2. Imports sécurisés des modules
try:
    from chargement import charger_fichier
    from validation import valider_tous_patients
    from statistiques import calculer_statistiques, afficher_statistiques
except ImportError:
    sys.path.append(os.getcwd())
    from chargement import charger_fichier
    from validation import valider_tous_patients
    from statistiques import calculer_statistiques, afficher_statistiques

# 3. Détermination automatique du chemin du fichier de données
if chemin_script.endswith("src") or not os.path.exists(os.path.join(chemin_script, "data")):
    CHEMIN_BRUT = os.path.abspath(os.path.join(chemin_script, "..", "data", "patients_bruts.txt"))
else:
    CHEMIN_BRUT = os.path.abspath(os.path.join(chemin_script, "data", "patients_bruts.txt"))

# Noms des colonnes pour la reconstruction adaptative des dictionnaires
COLONNES = ["id", "nom", "prenom", "age", "telephone", "ville", "groupe_sanguin", "poids", "taille"]

# Variables globales de session (état partagé entre les options du menu)
patients_bruts = []          # données chargées brutes
patients_valides = []        # après nettoyage (liste de dicts)
patients_rejetes = []        # rejetés formatés pour statistiques.py
doublons = []                # liste des doublons pour statistiques.py
toutes_anomalies = []        # toutes les anomalies détectées
stats = {}                   # statistiques calculées

# Structure d'échange globale préservée intacte pour export.py
resultats_nettoyage_global = {}

donnees_chargees = False
donnees_nettoyees = False


def afficher_menu():
    print("\n============================================")
    print("  SYSTÈME DE NETTOYAGE DE DONNÉES MÉDICALES")
    print("============================================")
    print("  1. Charger les données brutes")
    print("  2. Afficher les anomalies détectées")
    print("  3. Nettoyer les données")
    print("  4. Afficher les statistiques")
    print("  5. Exporter les données propres")
    print("  6. Quitter")
    print("--------------------------------------------")


def option_charger():
    """Option 1 : Charger le fichier brut."""
    global patients_bruts, donnees_chargees, donnees_nettoyees
    print(f"\n→ Tentative de lecture du fichier : {CHEMIN_BRUT}")
    
    os.makedirs(os.path.dirname(CHEMIN_BRUT), exist_ok=True)
    
    patients_bruts, erreurs_lecture, nb_lus = charger_fichier(CHEMIN_BRUT)

    if erreurs_lecture:
        print("\n⚠ Remarque/Erreur de lecture :")
        for err in erreurs_lecture:
            print(f"  {err}")

    if not patients_bruts:
        print("✗ Aucune donnée chargée. Vérifiez l'emplacement de 'data/patients_bruts.txt'.")
        donnees_chargees = False
        return

    print(f"\n✓ {nb_lus} ligne(s) lue(s)")
    print(f"✓ {len(patients_bruts)} patient(s) chargé(s) en mémoire.")
    donnees_chargees = True
    donnees_nettoyees = False


def option_afficher_anomalies():
    """Option 2 : Afficher toutes les anomalies détectées."""
    if not donnees_chargees:
        print("\n✗ Veuillez d'abord charger les données (option 1).")
        return

    from nettoyage import nettoyer_tous_les_patients

    print("\n--- ANALYSE DES ANOMALIES ---")
    analyse = nettoyer_tous_les_patients(patients_bruts)
    anomalies_temp = analyse.get("toutes_anomalies", [])

    if not anomalies_temp:
        print("✓ Aucune anomalie détectée !")
        return

    print(f"{len(anomalies_temp)} anomalie(s) détectée(s) :\n")
    for anomalie in anomalies_temp[:15]:
        print(f"  -> {anomalie}")
    if len(anomalies_temp) > 15:
        print(f"  ... et {len(anomalies_temp) - 15} autre(s) anomalie(s).")


def option_nettoyer():
    """Option 3 : Nettoyage et synchronisation adaptative complète des structures."""
    global patients_valides, patients_rejetes, toutes_anomalies, doublons, donnees_nettoyees, resultats_nettoyage_global

    if not donnees_chargees:
        print("\n✗ Veuillez d'abord charger les données (option 1).")
        return

    from nettoyage import nettoyer_tous_les_patients

    print("\n→ Nettoyage complet en cours...")
    
    # 1. Récupération des résultats bruts du script nettoyage.py
    resultats_nettoyage_global = nettoyer_tous_les_patients(patients_bruts)
    
    # 2. Extraction sécurisée
    patients_valides = resultats_nettoyage_global.get("patients_valides", [])
    rejetes_bruts = resultats_nettoyage_global.get("patients_rejetes", [])
    if not rejetes_bruts and "rejetes" in resultats_nettoyage_global:
        rejetes_bruts = resultats_nettoyage_global.get("rejetes", [])
        
    doublons_bruts = resultats_nettoyage_global.get("liste_doublons", [])
    toutes_anomalies = resultats_nettoyage_global.get("toutes_anomalies", [])

    # 3. Synchronisation pour export.py (Il lui faut absolument la clé 'nb_doublons')
    resultats_nettoyage_global["nb_doublons"] = len(doublons_bruts)

    # 4. Normalisation adaptative des rejetés pour statistiques.py (Doit être une liste de dicts de patients directs)
    patients_rejetes = []
    rejetes_formates_pour_export = []

    for r in rejetes_bruts:
        # Extraire le patient qu'il soit brut ou encapsulé
        info_patient = r["patient"] if isinstance(r, dict) and "patient" in r else r
        erreurs_patient = r["erreurs"] if isinstance(r, dict) and "erreurs" in r else ["Données invalides"]
        
        # Conversion forcée en dictionnaire si c'est une liste
        if isinstance(info_patient, list):
            dict_patient = {}
            for idx, col in enumerate(COLONNES):
                if idx < len(info_patient):
                    dict_patient[col] = str(info_patient[idx])
                else:
                    dict_patient[col] = ""
            p_dict = dict_patient
        elif isinstance(info_patient, dict):
            p_dict = info_patient
        else:
            p_dict = {}

        patients_rejetes.append(p_dict)
        rejetes_formates_pour_export.append({"patient": p_dict, "erreurs": erreurs_patient})

    # On remet la structure parfaitement propre attendue par export.py à la ligne 153
    resultats_nettoyage_global["patients_rejetes"] = rejetes_formates_pour_export
    resultats_nettoyage_global["patients_valides"] = patients_valides

    # Transmission du nombre de doublons attendu par statistiques.py
    doublons = [i for i in range(len(doublons_bruts))]

    print(f"✓ Nettoyage terminé avec succès !")
    print(f"  Patients valides   : {len(patients_valides)}")
    print(f"  Patients rejetés   : {len(patients_rejetes)}")
    print(f"  Doublons supprimés : {len(doublons_bruts)}")
    donnees_nettoyees = True


def option_statistiques():
    """Option 4 : Afficher les statistiques."""
    global stats

    if not donnees_nettoyees:
        print("\n✗ Veuillez d'abord nettoyer les données (option 3).")
        return

    stats = calculer_statistiques(patients_valides, patients_rejetes, doublons)
    afficher_statistiques(stats)


def option_exporter():
    """Option 5 : Exporter les fichiers propres."""
    if not donnees_nettoyees:
        print("\n✗ Veuillez d'abord nettoyer les données (option 3).")
        return

    from export import tout_exporter

    stats_export = stats if stats else calculer_statistiques(patients_valides, patients_rejetes, doublons)
    tout_exporter(resultats_nettoyage_global, stats_export)


def main():
    """Boucle principale du menu."""
    while True:
        afficher_menu()

        try:
            choix = input("Choix : ").strip()
        except KeyboardInterrupt:
            print("\n\nAu revoir !")
            break

        if choix == "1":
            option_charger()
        elif choix == "2":
            option_afficher_anomalies()
        elif choix == "3":
            option_nettoyer()
        elif choix == "4":
            option_statistiques()
        elif choix == "5":
            option_exporter()
        elif choix == "6":
            print("\nAu revoir !\n")
            break
        else:
            print("\n✗ Choix invalide. Entrez un nombre entre 1 et 6.")


if __name__ == "__main__":
    main()