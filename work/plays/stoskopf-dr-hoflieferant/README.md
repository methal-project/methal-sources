# Encodage de *D'r Hoflieferant*

- Exécuter `encode.sh`, qui appelera les scripts pertinents.
  - `create_tei.py` crée la version TEI de base
  - `add_characters_to_tei.py` ajoute les éléments `castList`, `listPerson` et `listRelation` au `front`.
  - `dracorizer.py` crée une version compatible avec le schéma de la plate-forme DraCor.
- Les scripts se servent de données (liste de personnages etc.) disponibles dans le dossier `data`.
