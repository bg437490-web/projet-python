# =============================================================
# statistiques.py — Calculs et affichage des statistiques
# Étudiant 1 : Lecture & Vérification
# =============================================================


def calculer_statistiques(patients_valides, patients_rejetes, doublons):
    """
    Calcule toutes les statistiques demandées à partir des données nettoyées.

    Paramètres :
        patients_valides (list) : liste de dicts patients valides ET nettoyés
        patients_rejetes (list) : liste de dicts {'patient': ..., 'anomalies': [...]}
        doublons         (list) : liste des indices de doublons supprimés

    Retour :
        stats (dict) : dictionnaire de toutes les statistiques calculées
    """
    stats = {}

    nb_valides = len(patients_valides)
    nb_rejetes = len(patients_rejetes)
    nb_doublons = len(doublons)
    nb_total = nb_valides + nb_rejetes + nb_doublons

    stats["nb_total"] = nb_total
    stats["nb_valides"] = nb_valides
    stats["nb_rejetes"] = nb_rejetes
    stats["nb_doublons"] = nb_doublons

    # --- Moyenne des âges ---
    ages = []
    for p in patients_valides:
        try:
            ages.append(int(p["age"]))
        except (ValueError, KeyError):
            pass

    if ages:
        stats["moyenne_age"] = round(sum(ages) / len(ages), 2)
    else:
        stats["moyenne_age"] = None

    # --- Moyenne des poids ---
    poids_liste = []
    for p in patients_valides:
        try:
            poids_liste.append(float(p["poids"]))
        except (ValueError, KeyError):
            pass

    if poids_liste:
        stats["moyenne_poids"] = round(sum(poids_liste) / len(poids_liste), 2)
    else:
        stats["moyenne_poids"] = None

    # --- Ville la plus fréquente ---
    compteur_villes = {}
    for p in patients_valides:
        ville = p.get("ville", "").strip()
        if ville:
            compteur_villes[ville] = compteur_villes.get(ville, 0) + 1

    if compteur_villes:
        ville_max = max(compteur_villes, key=lambda v: compteur_villes[v])
        stats["ville_plus_frequente"] = ville_max
        stats["ville_plus_frequente_nb"] = compteur_villes[ville_max]
        stats["repartition_villes"] = compteur_villes
    else:
        stats["ville_plus_frequente"] = None
        stats["ville_plus_frequente_nb"] = 0
        stats["repartition_villes"] = {}

    # --- Répartition des groupes sanguins ---
    compteur_groupes = {}
    for p in patients_valides:
        groupe = p.get("groupe_sanguin", "").strip()
        if groupe:
            compteur_groupes[groupe] = compteur_groupes.get(groupe, 0) + 1

    stats["repartition_groupes"] = compteur_groupes

    return stats


def afficher_statistiques(stats):
    """
    Affiche les statistiques dans la console de façon lisible.

    Paramètre :
        stats (dict) : dictionnaire retourné par calculer_statistiques()
    """
    ligne = "=" * 50

    print(f"\n{ligne}")
    print("         STATISTIQUES DU DATASET")
    print(ligne)

    print(f"  Nombre total de patients (brut)  : {stats.get('nb_total', 0)}")
    print(f"  Patients valides après nettoyage : {stats.get('nb_valides', 0)}")
    print(f"  Doublons supprimés               : {stats.get('nb_doublons', 0)}")
    print(f"  Lignes rejetées                  : {stats.get('nb_rejetes', 0)}")

    print(f"\n{ligne}")
    print("         MOYENNES")
    print(ligne)

    moy_age = stats.get("moyenne_age")
    moy_poids = stats.get("moyenne_poids")
    print(f"  Âge moyen des patients valides   : {moy_age if moy_age is not None else 'N/A'} ans")
    print(f"  Poids moyen des patients valides : {moy_poids if moy_poids is not None else 'N/A'} kg")

    print(f"\n{ligne}")
    print("         VILLES")
    print(ligne)

    ville = stats.get("ville_plus_frequente")
    nb_ville = stats.get("ville_plus_frequente_nb", 0)
    if ville:
        print(f"  Ville la plus fréquente : {ville} ({nb_ville} patients)")

    repartition_villes = stats.get("repartition_villes", {})
    if repartition_villes:
        print("\n  Répartition par ville :")
        # Trier par nombre décroissant
        for v, nb in sorted(repartition_villes.items(), key=lambda x: -x[1]):
            print(f"    {v:<20} : {nb}")

    print(f"\n{ligne}")
    print("         GROUPES SANGUINS")
    print(ligne)

    groupes = stats.get("repartition_groupes", {})
    if groupes:
        for groupe, nb in sorted(groupes.items()):
            print(f"    {groupe:<5} : {nb} patient(s)")
    else:
        print("  Aucune donnée disponible.")

    print(f"{ligne}\n")


def obtenir_resume_texte(stats):
    """
    Retourne un résumé textuel des statistiques (pour le rapport.txt).
    Utilisé par export.py (Étudiant 2).

    Paramètre :
        stats (dict) : dictionnaire retourné par calculer_statistiques()

    Retour :
        texte (str) : chaîne de caractères formatée
    """
    lignes = []
    sep = "=" * 50

    lignes.append(sep)
    lignes.append("STATISTIQUES FINALES")
    lignes.append(sep)
    lignes.append(f"Nombre total de patients bruts   : {stats.get('nb_total', 0)}")
    lignes.append(f"Patients valides après nettoyage : {stats.get('nb_valides', 0)}")
    lignes.append(f"Doublons supprimés               : {stats.get('nb_doublons', 0)}")
    lignes.append(f"Lignes rejetées                  : {stats.get('nb_rejetes', 0)}")
    lignes.append("")

    moy_age = stats.get("moyenne_age")
    moy_poids = stats.get("moyenne_poids")
    lignes.append(f"Âge moyen (patients valides)     : {moy_age if moy_age is not None else 'N/A'} ans")
    lignes.append(f"Poids moyen (patients valides)   : {moy_poids if moy_poids is not None else 'N/A'} kg")
    lignes.append("")

    ville = stats.get("ville_plus_frequente")
    nb_ville = stats.get("ville_plus_frequente_nb", 0)
    lignes.append(f"Ville la plus fréquente          : {ville} ({nb_ville} patients)")
    lignes.append("")

    lignes.append("Répartition des groupes sanguins :")
    groupes = stats.get("repartition_groupes", {})
    for groupe, nb in sorted(groupes.items()):
        lignes.append(f"  {groupe:<5} : {nb}")

    lignes.append(sep)

    return "\n".join(lignes)