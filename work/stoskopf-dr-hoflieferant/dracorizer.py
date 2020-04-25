"""
Prepare play for DRACOR.
"""

import config as cf
import os
import re

with open(cf.oufn_with_characters, mode="r", encoding="utf8") as fh:
    txt = fh.read()

newtxt = re.sub(re.compile(r"<respStmt.+/respStmt>", re.DOTALL), "", txt)
newtxt = re.sub(r"<\?xml-stylesheet.+?>", "", newtxt)
newtxt = re.sub(r"""(<\?xml version='1.0' encoding='UTF-8'\?>)""",
                r"""\1\n<?xml-model href="https://dracor.org/schema.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>""",
                newtxt)
newtxt = re.sub(r"""<author key="bnf:\d+ """, '<author key="', newtxt)

with open(cf.oufn_dracor, mode="w", encoding="utf8") as ofh:
    print("=> (dracor) {}".format(cf.oufn_dracor))
    ofh.write(newtxt)

os.system(f"wget -O {cf.dracor_schema} \"https://dracor.org/schema.rng\"")
os.system(f"xmllint --noout --relaxng {cf.dracor_schema} {cf.oufn_dracor}")
os.system(f"xmllint --format {cf.oufn_dracor} > .t ; mv .t {cf.oufn_dracor}")
os.system(f"rm {cf.dracor_schema}")
