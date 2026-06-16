# =============================================================
# validation.py — Détection des anomalies et des doublons
# Étudiant 1 : Lecture & Vérification
# =============================================================

import re

# Groupes sanguins strictement autorisés
GROUPES_SANGUINS_VALIDES = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}

# Villes connues : formes incorrectes → forme correcte
# (utilisé aussi par nettoyage.py, centralisé ici)
CORRECTIONS_VILLES = {
    "dakar": "Dakar",
    "dakkar": "Dakar",
    "dakarr": "Dakar",
    "thies": "Thiès",
    "thiès": "Thiès",
    "saint louis": "Saint-Louis",
    "saint-louis": "Saint-Louis",
    "ziguinchor": "Ziguinchor",
    "ziginchor": "Ziguinchor",
    "ziguincor": "Ziguinchor",
    "tambacounda": "Tambacounda",
    "tamba": "Tambacounda",
    "kaolack": "Kaolack",
    "kaolak": "Kaolack",
    "diourbel": "Diourbel",
    "diorbel": "Diourbel",
    "louga": "Louga",
    "lougar": "Louga",
    "saint-louis": "Saint-Louis",
}


# =============================================================
# FONCTIONS DE VALIDATION INDIVIDUELLE (par champ)
# Chaque fonction retourne (valeur_brute_nettoyée, message_erreur_ou_None)
# =============================================================

def valider_nom_prenom(valeur, libelle="Champ"):
    """
    Détecte si un nom/prénom est manquant.
    Retourne le nom strip() et un message d'anomalie si vide.
    """
    anomalie = None
    valeur_nettoyee = valeur.strip()
    if not valeur_nettoyee:
        anomalie = f"{libelle} manquant(e)"
    return valeur_nettoyee, anomalie


def valider_age(valeur):
    """
    Valide la valeur d'âge brute.
    Retourne (age_int_ou_None, message_anomalie_ou_None, est_rejetable).
    est_rejetable = True si l'anomalie entraîne le rejet du patient.
    """
    anomalie = None
    est_rejetable = False
    valeur = valeur.strip()

    if valeur == "":
        return None, "Âge manquant", True

    try:
        age = int(valeur)
    except ValueError:
        return None, f"Âge non numérique : '{valeur}'", True

    if age < 0:
        anomalie = f"Âge négatif : {age}"
        est_rejetable = True
    elif age == 0:
        anomalie = f"Âge égal à zéro (suspect) : {age}"
        est_rejetable = True
    elif age > 120:
        anomalie = f"Âge irréaliste (> 120) : {age}"
        est_rejetable = True

    return age, anomalie, est_rejetable


def valider_telephone(valeur):
    """
    Valide et pré-nettoie un numéro de téléphone.
    Supprime espaces, tirets et préfixes internationaux.
    Retourne (numero_nettoye_ou_None, message_anomalie_ou_None, est_rejetable).
    """
    anomalie = None
    est_rejetable = False
    valeur = valeur.strip()

    # Supprimer les espaces et tirets
    numero = valeur.replace(" ", "").replace("-", "")

    # Supprimer les préfixes internationaux
    if numero.startswith("00221"):
        numero = numero[5:]
    elif numero.startswith("+221"):
        numero = numero[4:]

    # Vérifier que le numéro ne contient que des chiffres
    if not numero.isdigit():
        return None, f"Téléphone non numérique après nettoyage : '{valeur}'", True

    # Vérifier la longueur : doit être exactement 9 chiffres
    if len(numero) != 9:
        return None, f"Téléphone invalide (longueur {len(numero)}) : '{valeur}'", True

    # Vérifier que le numéro commence par 7
    if not numero.startswith("7"):
        return None, f"Téléphone ne commençant pas par 7 : '{numero}'", True

    # Détecter les numéros suspects (tous chiffres identiques)
    if len(set(numero)) == 1:
        anomalie = f"Téléphone suspect (chiffres identiques) : '{numero}'"
        # Ce n'est pas une raison de rejet selon le sujet, juste un avertissement

    return numero, anomalie, est_rejetable


def valider_ville(valeur):
    """
    Détecte les anomalies de ville (fautes de frappe, casse, espaces).
    Retourne (ville_normalisee, message_anomalie_ou_None).
    La correction réelle est faite dans nettoyage.py.
    """
    anomalie = None
    ville = valeur.strip()

    if not ville:
        return ville, "Ville manquante"

    ville_lower = ville.lower()
    if ville_lower in CORRECTIONS_VILLES and CORRECTIONS_VILLES[ville_lower] != ville:
        anomalie = f"Ville mal orthographiée ou mal formatée : '{ville}'"

    return ville, anomalie


def valider_groupe_sanguin(valeur):
    """
    Vérifie que le groupe sanguin est dans la liste autorisée.
    Retourne (groupe_brut, message_anomalie_ou_None, est_rejetable).
    """
    # Force la mise en majuscules pour accepter 'a+' ou 'ab-' sans rejeter le patient
    groupe = valeur.strip().upper()

    if groupe not in GROUPES_SANGUINS_VALIDES:
        return valeur, f"Groupe sanguin invalide : '{valeur}'", True

    return groupe, None, False


def valider_poids(valeur):
    """
    Valide la valeur de poids.
    Retourne (poids_float_ou_None, message_anomalie_ou_None, est_rejetable).
    """
    valeur = valeur.strip()

    if valeur == "" or valeur.upper() == "N/A":
        return None, "Poids manquant ou N/A", True

    try:
        poids = float(valeur)
    except ValueError:
        return None, f"Poids non numérique : '{valeur}'", True

    if poids < 1 or poids > 300:
        return None, f"Poids hors limites (doit être entre 1 et 300) : {poids}", True

    return poids, None, False


def valider_taille(valeur):
    """
    Valide la valeur de taille.
    Retourne (taille_int_ou_None, message_anomalie_ou_None, est_rejetable).
    """
    valeur = valeur.strip()

    if valeur == "" or valeur.upper() == "N/A":
        return None, "Taille manquante ou N/A", True

    try:
        taille = int(float(valeur))  # accepte "175.0" aussi
    except ValueError:
        return None, f"Taille non numérique : '{valeur}'", True

    if taille < 50 or taille > 250:
        return None, f"Taille hors limites (doit être entre 50 et 250) : {taille}", True

    return taille, None, False


# =============================================================
# VALIDATION COMPLÈTE D'UN PATIENT
# =============================================================

def valider_patient(patient):
    """
    Valide tous les champs d'un patient brut.

    Paramètre :
        patient (dict) : dictionnaire patient avec valeurs brutes

    Retour :
        anomalies   (list) : liste de toutes les anomalies détectées
        est_valide  (bool) : True si le patient peut être conservé après nettoyage
    """
    anomalies = []
    est_valide = True  # devient False si une anomalie rédhibitoire est trouvée
    ligne = patient.get("_ligne", "?")

    # --- Nom ---
    _, err = valider_nom_prenom(patient.get("nom", ""), "Nom")
    if err:
        anomalies.append(f"Ligne {ligne} | NOM     | {err}")
        est_valide = False

    # --- Prénom ---
    _, err = valider_nom_prenom(patient.get("prenom", ""), "Prénom")
    if err:
        anomalies.append(f"Ligne {ligne} | PRÉNOM  | {err}")
        est_valide = False

    # --- Âge ---
    _, err, rejetable = valider_age(patient.get("age", ""))
    if err:
        anomalies.append(f"Ligne {ligne} | ÂGE     | {err}")
        if rejetable:
            est_valide = False

    # --- Téléphone ---
    _, err, rejetable = valider_telephone(patient.get("telephone", ""))
    if err:
        anomalies.append(f"Ligne {ligne} | TÉL     | {err}")
        if rejetable:
            est_valide = False

    # --- Ville ---
    _, err = valider_ville(patient.get("ville", ""))
    if err:
        anomalies.append(f"Ligne {ligne} | VILLE   | {err}")
        # La ville ne cause pas un rejet à elle seule

    # --- Groupe sanguin ---
    _, err, rejetable = valider_groupe_sanguin(patient.get("groupe_sanguin", ""))
    if err:
        anomalies.append(f"Ligne {ligne} | GROUPE  | {err}")
        if rejetable:
            est_valide = False

    # --- Poids ---
    _, err, rejetable = valider_poids(patient.get("poids", ""))
    if err:
        anomalies.append(f"Ligne {ligne} | POIDS   | {err}")
        if rejetable:
            est_valide = False

    # --- Taille ---
    _, err, rejetable = valider_taille(patient.get("taille", ""))
    if err:
        anomalies.append(f"Ligne {ligne} | TAILLE  | {err}")
        if rejetable:
            est_valide = False

    return anomalies, est_valide


# =============================================================
# DÉTECTION DES DOUBLONS
# =============================================================

def _cle_doublon(patient):
    """
    Génère une clé normalisée pour comparer les patients entre eux.
    On compare nom+prénom+âge+téléphone (après nettoyage minimal).
    """
    nom = patient.get("nom", "").strip().lower()
    prenom = patient.get("prenom", "").strip().lower()
    age = patient.get("age", "").strip()

    # Nettoyer le téléphone pour la comparaison
    tel = patient.get("telephone", "").strip()
    tel = tel.replace(" ", "").replace("-", "")
    if tel.startswith("00221"):
        tel = tel[5:]
    elif tel.startswith("+221"):
        tel = tel[4:]

    return (nom, prenom, age, tel)


def detecter_doublons(patients):
    """
    Détecte les doublons exacts et quasi-doublons dans la liste de patients.

    Paramètre :
        patients (list) : liste de dicts patients (données brutes)

    Retour :
        patients_uniques     (list) : patients sans doublons
        indices_doublons     (list) : indices (dans la liste originale) des doublons supprimés
        rapport_doublons     (list) : messages décrivant chaque doublon détecté
    """
    vus = {}             # clé_doublon → index du premier patient vu
    indices_doublons = []
    rapport_doublons = []
    patients_uniques = []

    for i, patient in enumerate(patients):
        cle = _cle_doublon(patient)
        ligne = patient.get("_ligne", "?")

        if cle in vus:
            # C'est un doublon
            premier_index = vus[cle]
            premier_ligne = patients[premier_index].get("_ligne", "?")
            indices_doublons.append(i)
            rapport_doublons.append(
                f"Doublon détecté : ligne {ligne} est identique à la ligne {premier_ligne} "
                f"→ {patient.get('nom','').strip()} {patient.get('prenom','').strip()}, "
                f"âge={patient.get('age','').strip()}, tél={patient.get('telephone','').strip()}"
            )
        else:
            vus[cle] = i
            patients_uniques.append(patient)

    return patients_uniques, indices_doublons, rapport_doublons


# =============================================================
# VALIDATION DE TOUTE LA LISTE
# =============================================================

def valider_tous_patients(patients):
    """
    Valide chaque patient et retourne la liste des patients valides
    ainsi que les rapports d'anomalies et de rejets.

    Paramètre :
        patients (list) : liste de dicts patients (sans doublons)

    Retour :
        patients_valides  (list) : patients qui passent toutes les validations
        patients_rejetes  (list) : patients rejetés avec leurs anomalies
        toutes_anomalies  (list) : toutes les anomalies détectées (valides et rejetés)
    """
    patients_valides = []
    patients_rejetes = []
    toutes_anomalies = []

    for patient in patients:
        anomalies, est_valide = valider_patient(patient)
        toutes_anomalies.extend(anomalies)

        if est_valide:
            patients_valides.append(patient)
        else:
            patients_rejetes.append({
                "patient": patient,
                "anomalies": anomalies
            })

    return patients_valides, patients_rejetes, toutes_anomalies