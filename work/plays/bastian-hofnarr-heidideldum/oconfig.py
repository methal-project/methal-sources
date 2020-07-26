#coding=utf8

from collections import OrderedDict as OD
import os

# TEI schema path
tei_rng = os.path.abspath(os.path.join("schema", "my-tei.rng"))

# licenses
availability = {
    "ccby": "".join(["<availability>",
                     "<licence><ab>CC BY 2.0</ab>",
                     '<ref target="https://creativecommons.org/licenses/by/2.0/">Licence</ref>',
                     "</licence></availability>"])
}

respStmt = OD([
    (("Audrey Deck", "OCR and its correction, TEI encoding"), True),
    (("Delphine Bernhard", "TEI encoding"), True),
    (("Pablo Ruiz", "TEI encoding"), True)
])

character_sheet_name = "personnages"
header_sheet_name = "pieces"
play_set_dir = "sets"
play_set_data = os.path.abspath(os.path.join(play_set_dir, "sets.xml"))
dedication_fn = os.path.abspath("../../other/dedications.xml")