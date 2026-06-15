"""
nettoyage.py
Module de nettoyage des données patients.
Etudiant 2 — Projet Python 1 : Prétraitement de Données Médicales
"""

import re

# ─────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────

GROUPES_SANGUINS_VALIDES = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}

CORRECTIONS_VILLES = {
    "dakar":        "Dakar",
    "dakarr":       "Dakar",
    "thies":        "Thiès",
    "thiès":        "Thiès",
    "saint louis":  "Saint-Louis",
    "saint-louis":  "Saint-Louis",
    "ziguinchor":   "Ziguinchor",
    "ziginchor":    "Ziguinchor",
    "ziguincor":    "Ziguinchor",
    "tambacounda":  "Tambacounda",
    "tamba":        "Tambacounda",
    "louga":        "Louga",
    "kaolack":      "Kaolack",
    "kaolak":       "Kaolack",
    "diourbel":     "Diourbel",
    "diorbel":      "Diourbel",
    "kolda":        "Kolda",
    "matam":        "Matam",
    "fatick":       "Fatick",
    "kaffrine":     "Kaffrine",
    "kedougou":     "Kédougou",
    "kédougou":     "Kédougou",
    "sedhiou":      "Sédhiou",
    "sédhiou":      "Sédhiou",
}


# ─────────────────────────────────────────────
#  Utilitaire : capitalisation respectant les tirets
#  Ex: "saint-louis" → "Saint-Louis"  (et non "Saint-louis" avec .title())
# ─────────────────────────────────────────────

def _capitaliser(texte):
    """
    Capitalise chaque mot séparé par un espace ou un tiret.
    Évite le bug de .title() sur les noms composés (Saint-Louis, etc.).
    """
    if not texte:
        return texte
    # Séparer sur les tirets, capitaliser chaque partie, réassembler
    parties = texte.split("-")
    parties_corrigees = []
    for partie in parties:
        mots = partie.split()
        parties_corrigees.append(" ".join(m.capitalize() for m in mots))
    return "-".join(parties_corrigees)


# ─────────────────────────────────────────────
#  1. Nettoyage des noms et prénoms
# ─────────────────────────────────────────────

def nettoyer_nom(valeur):
    """
    Nettoie un nom ou prénom :
    - Supprime les espaces/caractères invisibles en début et fin
    - Normalise les espaces internes
    - Applique une capitalisation correcte (respecte les tirets)
    Retourne (valeur_nettoyée_ou_None, liste_erreurs).
    """
    erreurs = []
    if not valeur or not str(valeur).strip():
        erreurs.append("Nom/prénom manquant")
        return None, erreurs

    original = str(valeur)

    # Supprimer espaces invisibles et normaliser
    nettoye = original.strip().replace("\xa0", " ").replace("\t", " ")
    nettoye = " ".join(nettoye.split())

    if nettoye != original.strip():
        erreurs.append(f"Espaces inutiles supprimés dans '{original.strip()}'")

    if nettoye.islower():
        erreurs.append(f"Nom entièrement en minuscules : '{nettoye}'")
    elif nettoye.isupper():
        erreurs.append(f"Nom entièrement en majuscules : '{nettoye}'")

    # Capitalisation correcte (gère les tirets)
    nettoye = _capitaliser(nettoye)

    return nettoye, erreurs


# ─────────────────────────────────────────────
#  2. Nettoyage des âges
#  CORRECTION BUG : âge 0 = nourrisson, valide mais signalé
# ─────────────────────────────────────────────

def nettoyer_age(valeur):
    """
    Valide un âge patient.
    - Âge 0 : accepté (nourrisson < 1 an), signalé en [INFO]
    - Âge négatif ou > 120 : rejeté
    - Âge manquant : rejeté
    Retourne (age_int_ou_None, liste_erreurs).
    """
    erreurs = []

    if valeur is None or str(valeur).strip() == "":
        erreurs.append("Âge manquant")
        return None, erreurs

    try:
        age = int(str(valeur).strip())
    except ValueError:
        erreurs.append(f"Âge non numérique : '{valeur}'")
        return None, erreurs

    if age < 0:
        erreurs.append(f"Âge négatif invalide : {age}")
        return None, erreurs

    if age > 120:
        erreurs.append(f"Âge irréaliste (> 120) : {age}")
        return None, erreurs

    # CORRECTION : âge 0 = nourrisson de moins d'un an → valide mais signalé
    if age == 0:
        erreurs.append(f"[INFO] Âge = 0 (nourrisson de moins d'un an mais signaler comme suspect) — patient conservé")

    return age, erreurs


# ─────────────────────────────────────────────
#  3. Nettoyage des téléphones
#  CORRECTION BUG : isoler le + AVANT la regex pour éviter isdigit() faux
# ─────────────────────────────────────────────

def nettoyer_telephone(valeur):
    """
    Nettoie un numéro de téléphone sénégalais.
    Ordre de traitement :
      1. Retirer les espaces et tirets
      2. Retirer les préfixes internationaux (+221, 00221)
      3. Vérifier : 9 chiffres, commence par 7
    Retourne (tel_nettoyé_ou_None, liste_erreurs).
    """
    erreurs = []

    if not valeur or str(valeur).strip() == "":
        erreurs.append("Téléphone manquant")
        return None, erreurs

    original = str(valeur).strip()
    tel = original

    # Étape 1 : supprimer espaces et tirets (mais PAS le + encore)
    tel_sans_espaces = re.sub(r"[\s\-]", "", tel)
    if tel_sans_espaces != original:
        erreurs.append(f"Espaces/tirets supprimés dans '{original}'")
    tel = tel_sans_espaces

    # Étape 2 : supprimer les préfixes internationaux
    # On teste AVANT isdigit() car le + n'est pas un chiffre
    if tel.startswith("+221"):
        tel = tel[4:]
        erreurs.append(f"Préfixe '+221' supprimé de '{original}'")
    elif tel.startswith("00221"):
        tel = tel[5:]
        erreurs.append(f"Préfixe '00221' supprimé de '{original}'")

    # Étape 3 : vérifier que le reste ne contient que des chiffres
    if not tel.isdigit():
        erreurs.append(f"Téléphone contient des caractères invalides après nettoyage : '{original}'")
        return None, erreurs

    # Étape 4 : vérifier longueur exacte = 9
    if len(tel) != 9:
        erreurs.append(f"Téléphone : longueur incorrecte ({len(tel)} chiffres) → '{original}'")
        return None, erreurs

    # Étape 5 : commence obligatoirement par 7
    if not tel.startswith("7"):
        erreurs.append(f"Téléphone ne commence pas par 7 : '{tel}'")
        return None, erreurs

    # Numéro suspect (tous chiffres identiques) — conservé mais signalé
    if len(set(tel)) == 1:
        erreurs.append(f"[INFO] Téléphone suspect (tous chiffres identiques) : '{tel}'")

    return tel, erreurs


# ─────────────────────────────────────────────
#  4. Nettoyage des villes
#  CORRECTION BUG : utiliser _capitaliser() au lieu de .title()
# ─────────────────────────────────────────────

def nettoyer_ville(valeur):
    """
    Nettoie le nom d'une ville :
    - Supprime les espaces inutiles
    - Corrige via dictionnaire (Saint-Louis, Thiès, etc.)
    - Capitalise correctement les noms composés avec tiret
    Retourne (ville_nettoyée_ou_None, liste_erreurs).
    """
    erreurs = []

    if not valeur or str(valeur).strip() == "":
        erreurs.append("Ville manquante")
        return None, erreurs

    original = str(valeur).strip()
    ville_lower = original.lower().strip()

    if original != str(valeur):
        erreurs.append(f"Espaces inutiles dans la ville '{valeur}'")

    # Chercher dans le dictionnaire de corrections
    if ville_lower in CORRECTIONS_VILLES:
        ville_corrigee = CORRECTIONS_VILLES[ville_lower]
        if ville_corrigee != original:
            erreurs.append(f"Ville corrigée : '{original}' → '{ville_corrigee}'")
        return ville_corrigee, erreurs

    # Sinon, capitalisation correcte (respecte les tirets)
    ville_corrigee = _capitaliser(original)
    if ville_corrigee != original:
        erreurs.append(f"Casse corrigée : '{original}' → '{ville_corrigee}'")

    return ville_corrigee, erreurs


# ─────────────────────────────────────────────
#  5. Validation du groupe sanguin
#  CORRECTION BUG : nettoyer "O" seul ou "0" (zéro) avant rejet
# ─────────────────────────────────────────────

def nettoyer_groupe_sanguin(valeur):
    """
    Valide le groupe sanguin.
    Nettoyage préalable :
      - "0" (chiffre zéro) → "O" (lettre O) : faute de frappe fréquente
      - Groupe "O" sans signe : invalide et rejeté (on ne peut pas deviner + ou -)
    Seuls A+, A-, B+, B-, AB+, AB-, O+, O- sont acceptés.
    Retourne (groupe_ou_None, liste_erreurs).
    """
    erreurs = []

    if not valeur or str(valeur).strip() == "":
        erreurs.append("Groupe sanguin manquant")
        return None, erreurs

    groupe = str(valeur).strip().upper()

    # Corriger la confusion zéro/lettre O (ex: "0+" → "O+")
    if groupe and groupe[0] == "0":
        groupe_corrige = "O" + groupe[1:]
        erreurs.append(f"Groupe sanguin : '0' (zéro) corrigé en 'O' → '{groupe}' → '{groupe_corrige}'")
        groupe = groupe_corrige

    # Valider
    if groupe not in GROUPES_SANGUINS_VALIDES:
        # Cas particulier : "O" seul sans signe → on ne peut pas deviner, rejet
        erreurs.append(f"Groupe sanguin invalide (signe +/- manquant ou groupe inconnu) : '{valeur}'")
        return None, erreurs

    return groupe, erreurs


# ─────────────────────────────────────────────
#  6. Poids et taille
# ─────────────────────────────────────────────

def nettoyer_poids(valeur):
    """
    Valide le poids (float entre 1 et 300 kg).
    Retourne (poids_ou_None, liste_erreurs).
    """
    erreurs = []
    if not valeur or str(valeur).strip() in ("", "N/A", "n/a", "NA"):
        erreurs.append("Poids manquant ou N/A")
        return None, erreurs
    try:
        poids = float(str(valeur).strip())
    except ValueError:
        erreurs.append(f"Poids non numérique : '{valeur}'")
        return None, erreurs
    if poids < 1 or poids > 300:
        erreurs.append(f"Poids impossible : {poids} kg (doit être entre 1 et 300)")
        return None, erreurs
    return poids, erreurs


def nettoyer_taille(valeur):
    """
    Valide la taille (entier entre 50 et 250 cm).
    Retourne (taille_ou_None, liste_erreurs).
    """
    erreurs = []
    if not valeur or str(valeur).strip() in ("", "N/A", "n/a", "NA"):
        erreurs.append("Taille manquante ou N/A")
        return None, erreurs
    try:
        taille = int(float(str(valeur).strip()))
    except ValueError:
        erreurs.append(f"Taille non numérique : '{valeur}'")
        return None, erreurs
    if taille < 50 or taille > 250:
        erreurs.append(f"Taille impossible : {taille} cm (doit être entre 50 et 250)")
        return None, erreurs
    return taille, erreurs


# ─────────────────────────────────────────────
#  7. Nettoyage complet d'un patient
# ─────────────────────────────────────────────

def nettoyer_patient(patient_brut):
    """
    Applique toutes les fonctions de nettoyage à un dictionnaire patient.
    Retourne (patient_propre_ou_None, liste_erreurs, est_valide).
    """
    toutes_erreurs = []
    patient_propre = {"id": patient_brut.get("id", "?")}

    nom,    err = nettoyer_nom(patient_brut.get("nom", ""))
    patient_propre["nom"] = nom
    toutes_erreurs.extend([f"[Nom] {e}" for e in err])

    prenom, err = nettoyer_nom(patient_brut.get("prenom", ""))
    patient_propre["prenom"] = prenom
    toutes_erreurs.extend([f"[Prénom] {e}" for e in err])

    age,    err = nettoyer_age(patient_brut.get("age", ""))
    patient_propre["age"] = age
    toutes_erreurs.extend([f"[Âge] {e}" for e in err])

    tel,    err = nettoyer_telephone(patient_brut.get("telephone", ""))
    patient_propre["telephone"] = tel
    toutes_erreurs.extend([f"[Téléphone] {e}" for e in err])

    ville,  err = nettoyer_ville(patient_brut.get("ville", ""))
    patient_propre["ville"] = ville
    toutes_erreurs.extend([f"[Ville] {e}" for e in err])

    groupe, err = nettoyer_groupe_sanguin(patient_brut.get("groupe_sanguin", ""))
    patient_propre["groupe_sanguin"] = groupe
    toutes_erreurs.extend([f"[Groupe sanguin] {e}" for e in err])

    poids,  err = nettoyer_poids(patient_brut.get("poids", ""))
    patient_propre["poids"] = poids
    toutes_erreurs.extend([f"[Poids] {e}" for e in err])

    taille, err = nettoyer_taille(patient_brut.get("taille", ""))
    patient_propre["taille"] = taille
    toutes_erreurs.extend([f"[Taille] {e}" for e in err])

    # Rejet si un champ critique est None
    champs_invalides = [
        c for c, v in {
            "nom": nom, "prenom": prenom, "age": age,
            "telephone": tel, "groupe_sanguin": groupe,
            "poids": poids, "taille": taille,
        }.items() if v is None
    ]

    est_valide = len(champs_invalides) == 0
    if not est_valide:
        toutes_erreurs.append(
            f"[REJET] Champs invalides : {', '.join(champs_invalides)}"
        )

    return patient_propre, toutes_erreurs, est_valide


# ─────────────────────────────────────────────
#  8.Gestion des doublons
# ─────────────────────────────────────────────




# ─────────────────────────────────────────────
#  9. Processus global de nettoyage
# ─────────────────────────────────────────────

def nettoyer_tous_les_patients(patients_bruts):
    """
    Nettoie tous les patients et retourne :
    {
        "patients_valides":  [...],
        "patients_rejetes":  [...],
        "toutes_anomalies":  [...],
        "nb_doublons":       int,
    }
    """
    valides_avant_dedup = []
    rejetes = []
    anomalies = []

    for p in patients_bruts:
        propre, erreurs, valide = nettoyer_patient(p)
        id_p = p.get("id", "?")
        for e in erreurs:
            anomalies.append(f"Patient #{id_p} : {e}")
        if valide:
            valides_avant_dedup.append(propre)
        else:
            rejetes.append({"patient": p, "erreurs": erreurs})

    valides, nb_doublons = supprimer_doublons(valides_avant_dedup)
    if nb_doublons > 0:
        anomalies.append(
            f"[DOUBLONS] {nb_doublons} doublon(s) supprimé(s)"
        )

    return {
        "patients_valides": valides,
        "patients_rejetes": rejetes,
        "toutes_anomalies": anomalies,
        "nb_doublons":      nb_doublons,
    }





 