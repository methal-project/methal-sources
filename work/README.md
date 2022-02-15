# Work

- This directory documents the encoding procedure for the first plays we encoded in TEI, for which we used rule and lexicon-based methods to transform OCR output into TEI. After these first plays, we moved to machine learning for our TEI encoding, using a sequence labeling method called *Conditional Random Fields*, followed by manual corrections, but we have not released the code or the training data yet.
- Directory structure:
    - `plays`: Encoding of each corpus play
    - `css`: Stylesheets for rendering the plays
    - `schema`: XML schemas used
    - `utils`: Functions common to encoding several plays

---

- Ce dossier documente la procédure d'encodage pour les premières pièces que nous avons encodées en TEI, pour lesquelles nous avons utilisé des méthodes symboliques (c.à.d. des règles et des lexiques) pour transformer une sortie OCR en TEI. Après ces premières pièces, nous avons adopté pour l'encodage TEI une méthode d'apprentissage automatique (*Conditional Random Fields*) suivie de corrections manuelles, mais le code et les données d'entraînement ne sont pas encore publiés.
- La structure du dossier est la suivante:
    - `plays`: Encodage de chaque pièce
    - `css`: Feuilles de style pour rendre les pièces
    - `schema`: Schémas XML utilisés
    - `utils`: Fonctions communes à l'encodage de plusieurs pièces
