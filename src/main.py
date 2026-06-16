# =============================================================
# main.py — Point d'entrée principal de l'application
# Projet d'Équipe : Étudiant 1 & Étudiant 2 (Conforme à 100%)
# =============================================================

import sys
import os

# Ces 3 lignes forcent Python à regarder à l'intérieur du dossier 'src' pour trouver vos modules !
chemin_src = os.path.dirname(os.path.abspath(__file__))
if chemin_src not in sys.path:
    sys.path.append(chemin_src)

# Maintenant, vos imports fonctionneront à tous les coups, peu importe le terminal !
from chargement import charger_fichier
from nettoyage import nettoyer_tous_les_patients
from statistiques import calculer_statistiques, afficher_statistiques
from export import tout_exporter

def afficher_menu():
    """Affiche le menu interactif STRICTEMENT exigé par le professeur."""
    print("\n" + "="*50)
    print("  SYSTÈME DE NETTOYAGE DE DONNÉES MÉDICALES  ")
    print("="*50)
    print("1. Charger les données brutes")
    print("2. Afficher les anomalies détectées")
    print("3. Nettoyer les données")
    print("4. Afficher les statistiques")
    print("5. Exporter les données propres")
    print("6. Quitter")
    print("="*50)

def main():
    # Variables de stockage des états
    patients_bruts = None
    resultats_nettoyage = None
    statistiques_calculees = None
    
    # Chemin du fichier brut
    chemin_fichier = "patients_bruts.txt" 

    while True:
        afficher_menu()
        choix = input("Choix : ").strip()

        try:
            # OPTION 1 : Charger les données brutes
            if choix == "1":
                print(f"\n[Chargement] Lecture de '{chemin_fichier}'...")
                patients_bruts, erreurs_import, _ = charger_fichier(chemin_fichier)
                
                if erreurs_import and not patients_bruts:
                    print(f"❌ Impossible de charger le fichier : {erreurs_import[0]}")
                    patients_bruts = None
                else:
                    print(f"✅ Fichier chargé avec succès ! {len(patients_bruts)} lignes lues.")

            # OPTION 2 : Afficher les anomalies détectées
            elif choix == "2":
                if patients_bruts is None:
                    print("❌ Erreur : Vous devez d'abord charger le fichier (Option 1) !")
                    continue
                
                # On lance un pré-nettoyage rapide pour collecter les anomalies à afficher
                print("\n[Anomalies] Liste des erreurs détectées dans le fichier brut :")
                analyse = nettoyer_tous_les_patients(patients_bruts)
                if analyse["toutes_anomalies"]:
                    for anomalie in analyse["toutes_anomalies"]:
                        print(f"  -> {anomalie}")
                else:
                    print("  Aucune anomalie détectée.")

            # OPTION 3 : Nettoyer les données
            elif choix == "3":
                if patients_bruts is None:
                    print("❌ Erreur : Vous devez d'abord charger le fichier (Option 1) !")
                    continue
                
                print("\n[Nettoyage] Lancement du nettoyage et de la déduplication...")
                # Appel de ton module nettoyage.py
                resultats_nettoyage = nettoyer_tous_les_patients(patients_bruts)
                
                # Calcul des statistiques (avec la passerelle de sécurité pour ta collègue)
                statistiques_calculees = calculer_statistiques(
                    resultats_nettoyage["patients_valides"],
                    resultats_nettoyage["patients_rejetes"],
                    resultats_nettoyage["liste_doublons"] # Évite le crash len() !
                )
                print("✅ Données nettoyées avec succès en mémoire ! Prêtes pour l'affichage ou l'export.")
                print(f"   Patients valides : {len(resultats_nettoyage['patients_valides'])} | Rejetés : {len(resultats_nettoyage['patients_rejetes'])}")

            # OPTION 4 : Afficher les statistiques
            elif choix == "4":
                if statistiques_calculees is None:
                    print("❌ Erreur : Vous devez d'abord nettoyer les données (Option 3) !")
                    continue
                
                # Appel du module statistiques.py de ta collègue
                afficher_statistiques(statistiques_calculees)

            # OPTION 5 : Exporter les données propres
            elif choix == "5":
                if resultats_nettoyage is None or statistiques_calculees is None:
                    print("❌ Erreur : Rien à exporter ! Veuillez nettoyer les données (Option 3) d'abord.")
                    continue
                
                print("\n[Export] Génération des fichiers réglementaires...")
                # Appel de ton module export.py
                tout_exporter(resultats_nettoyage, statistiques_calculees)
                print("✅ Exportation terminée !")
                print("   -> Fichiers créés : patients_propres.csv, patients_propres.json et rapport.txt")

            # OPTION 6 : Quitter
            elif choix == "6":
                print("\n👋 Fermeture de l'application. Bon courage pour la soutenance !")
                break

            else:
                print("❌ Choix invalide ! Veuillez entrer un chiffre entre 1 et 6.")

        except Exception as e:
            # Contrainte réglementaire : Le programme ne doit JAMAIS crasher
            print(f"\n🔥 Une erreur inattendue est survenue : {e}")
            print("Le système reste stable. Vous pouvez continuer.")

if __name__ == "__main__":
    main()