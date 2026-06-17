"""
nettoyage.py
Module de nettoyage des données patients.
Etudiant 2 — Projet Python 1 : Prétraitement de Données Médicales
"""

import re

# ─────────────────────────────────────────────
#  Constantes (Partagées avec validation.py)
# ─────────────────────────────────────────────
from validation import CORRECTIONS_VILLES, GROUPES_SANGUINS_VALIDES


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
#  8. Gestion des doublons
# ─────────────────────────────────────────────


from validation import valider_patient, CORRECTIONS_VILLES

def supprimer_doublons(patients_valides):
    """
    Supprime les doublons d'une liste de patients nettoyés.
    Deux patients sont considérés comme doublons s'ils ont les mêmes 
    nom, prénom et numéro de téléphone.
    """
    propres_sans_doublons = []
    liste_doublons = []
    vus = set()

    for p in patients_valides:
        if isinstance(p, dict):
            nom = str(p.get("nom", "")).strip().lower()
            prenom = str(p.get("prenom", "")).strip().lower()
            telephone = str(p.get("telephone", "")).strip().lower()
        else:
            nom, prenom, telephone = "", "", ""

        cle_unique = (nom, prenom, telephone)
        
        if not nom and not prenom:
            propres_sans_doublons.append(p)
            continue

        if cle_unique in vus:
            liste_doublons.append(p)
        else:
            vus.add(cle_unique)
            propres_sans_doublons.append(p)
            
    return propres_sans_doublons, liste_doublons


def nettoyer_tous_les_patients(patients_bruts):
    """
    Fonction maîtresse qui orchestre la validation, l'application
    RÉELLE des fonctions de nettoyage par champ, la séparation
    des rejets et le dédoublonnage.

    CORRECTION : cette fonction appelle désormais nettoyer_nom,
    nettoyer_telephone, nettoyer_ville, nettoyer_groupe_sanguin,
    nettoyer_poids et nettoyer_taille (au lieu de copier les valeurs
    brutes). C'est ce qui garantit que patients_propres.csv contient
    bien des noms en format titre et des téléphones au format
    7XXXXXXXX, comme l'exige le sujet.
    """
    valides_avant_dedup = []
    rejetes = []
    anomalies_globales = []

    for p in patients_bruts:
        # 1. Appel de la fonction de validation (validation.py) qui décide
        #    si le patient doit être rejeté (anomalies grave :
        #    groupe sanguin invalide, âge impossible, tél invalide, etc.)
        anomalies_patient, est_valide = valider_patient(p)

        if not est_valide:
            # Anomalie serieuse -> REJET, on garde le patient brut
            # tel quel dans le rapport des rejetés (rien à nettoyer ici)
            rejetes.append({
                "patient": p,
                "erreurs": anomalies_patient if anomalies_patient else ["Données critiques invalides"]
            })
            anomalies_globales.extend(anomalies_patient)
            continue

        # 2. # 2. Pour les patient valide : on applique le vrai nettoyage par champ
        # (et on garde les anomalies non-rejet détectées, sauf la ville déjà 
        #signalée plus bas par nettoyer_ville).
      
        anomalies_globales.extend([a for a in anomalies_patient if "| VILLE " not in a])

        p_propre = {"id": p.get("id", "?"), "_ligne": p.get("_ligne", "?")}

        nom, err_nom = nettoyer_nom(p.get("nom", ""))
        p_propre["nom"] = nom
        anomalies_globales.extend([f"Ligne {p.get('_ligne','?')} | NOM     | {e}" for e in err_nom])

        prenom, err_prenom = nettoyer_nom(p.get("prenom", ""))
        p_propre["prenom"] = prenom
        anomalies_globales.extend([f"Ligne {p.get('_ligne','?')} | PRÉNOM  | {e}" for e in err_prenom])

        # Mettre l'age en int
        try:
            p_propre["age"] = int(str(p.get("age", "")).strip())
        except ValueError:
            p_propre["age"] = None

        tel, err_tel = nettoyer_telephone(p.get("telephone", ""))
        p_propre["telephone"] = tel
        anomalies_globales.extend([f"Ligne {p.get('_ligne','?')} | TÉL     | {e}" for e in err_tel])

        ville, err_ville = nettoyer_ville(p.get("ville", ""))
        p_propre["ville"] = ville
        anomalies_globales.extend([f"Ligne {p.get('_ligne','?')} | VILLE   | {e}" for e in err_ville])

        groupe, err_groupe = nettoyer_groupe_sanguin(p.get("groupe_sanguin", ""))
        p_propre["groupe_sanguin"] = groupe
        anomalies_globales.extend([f"Ligne {p.get('_ligne','?')} | GROUPE  | {e}" for e in err_groupe])

        poids, err_poids = nettoyer_poids(p.get("poids", ""))
        p_propre["poids"] = poids
        anomalies_globales.extend([f"Ligne {p.get('_ligne','?')} | POIDS   | {e}" for e in err_poids])

        taille, err_taille = nettoyer_taille(p.get("taille", ""))
        p_propre["taille"] = taille
        anomalies_globales.extend([f"Ligne {p.get('_ligne','?')} | TAILLE  | {e}" for e in err_taille])

        
        champs_invalides = [
            c for c, v in {
                "nom": nom, "prenom": prenom, "telephone": tel,
                "groupe_sanguin": groupe, "poids": poids, "taille": taille,
            }.items() if v is None
        ]
        if champs_invalides:
            rejetes.append({
                "patient": p,
                "erreurs": [f"[REJET après nettoyage] Champs invalides : {', '.join(champs_invalides)}"]
            })
            continue

        valides_avant_dedup.append(p_propre)

    # 3 verification des dedoublonnage
    valides_finals, les_doublons_trouves = supprimer_doublons(valides_avant_dedup)

    # 4. Enregistrement des anomalies de doublons
    for d in les_doublons_trouves:
        nom_d = d.get("nom", "Inconnu")
        prenom_d = d.get("prenom", "")
        tel_d = d.get("telephone", "N/A")
        anomalies_globales.append(f"Ligne {d.get('_ligne', '?')} | DOUBLON | Doublon supprimé : {nom_d} {prenom_d} ({tel_d})")

    # 5. Renvoi du dictionnaire complet attendu par le menu principal (main)
    return {
        "patients_valides": valides_finals,
        "patients_rejetes": rejetes,
        "toutes_anomalies": anomalies_globales,
        "liste_doublons": les_doublons_trouves
    }