# Encodage de *In's Ropfer's Apothek*

- Appliquer `ropfer_hocr2tei.xsl` sur les fichiers dans `RopferStoskopf_hOCR`, ce qui crée le fichier `RopferStoskopfTEI/stoskopf-ropfer.xml`. Il s'agit d'un fichier avec la structure TEI de base, mais qui manque encore l'identification de plusieurs éléments (p. ex. les didascalies)
- Exécuter `python ropfer_tei_final.py`, qui crée le fichier TEI final dans `RopferStoskopfTEI/stoskopf-ropfer_final.xml`. Le script se sert de données (liste de personnages etc.) disponibles dans le dossier `data`.
