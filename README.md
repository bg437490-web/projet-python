# Projet Python 1 — Nettoyage de Données Médicales

## Structure du projet

```
projet_python/
├── data/
│   ├── patients_bruts.txt       ← fichier d'entrée (fourni)
│   └── patients_propres.csv     ← généré après export
├── src/
│   ├── main.py          ← menu principal (Fait en binome)
│   ├── chargement.py    ← lecture du fichier brut       (Mame Binta Niang)
│   ├── validation.py    ← détection anomalies/doublons  (Mame Binta Niang)
│   ├── statistiques.py  ← calculs et statistiques       (Mame Binta Niang)
│   ├── nettoyage.py     ← correction des erreurs        (Ababacar Sedikh Gueye)
│   └── export.py        ← écriture CSV et rapport       (Ababacar Sedikh Gueye)
├── rapport/
│   └── rapport.txt      ← généré après export
└── README.md (Fait en binome)
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
