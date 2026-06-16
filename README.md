# Projet Python 1 — Nettoyage de Données Médicales

## Structure du projet

```
projet_python/
├── data/
│   ├── patients_bruts.txt       ← fichier d'entrée (fourni)
│   └── patients_propres.csv     ← généré après export
├── src/
│   ├── main.py          ← menu principal (les deux étudiants)
│   ├── chargement.py    ← lecture du fichier brut       (Étudiant 1)
│   ├── validation.py    ← détection anomalies/doublons  (Étudiant 1)
│   ├── statistiques.py  ← calculs et statistiques       (Étudiant 1)
│   ├── nettoyage.py     ← correction des erreurs        (Étudiant 2)
│   └── export.py        ← écriture CSV et rapport       (Étudiant 2)
├── rapport/
│   └── rapport.txt      ← généré après export
└── README.md
```

## Lancement

```bash
# Depuis la racine du projet
python src/main.py
```

## Ordre d'utilisation du menu

1. **Option 1** — Charger les données brutes
2. **Option 2** — Afficher les anomalies (facultatif, pour vérifier)
3. **Option 3** — Nettoyer les données
4. **Option 4** — Afficher les statistiques
5. **Option 5** — Exporter CSV + rapport

## Modules utilisés

`csv`, `re`, `os`, `sys` — uniquement la bibliothèque standard Python.

# projet-python
