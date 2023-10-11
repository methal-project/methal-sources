#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
From XSLT output for Ropfer's Apothek to final TEI.

(Adds stage directions via language identification, adds character info, etc.)

Created on Sun Dec 22 16:48:39 2019

@author: ruizfabo
"""

import langid
from lxml import etree
import pandas as pd
from pandas_ods_reader import read_ods
import os
import re
import shutil
from string import punctuation
import sys


import manual_corrections as mc

# IO

infn = "/home/ruizfabo/te/stra/re/theatre_alsacien/ressources/ropfer/RopferStoskopfTEI/stoskopf-ropfer.xml"
oufn = os.path.splitext(infn)[0] + "_temp.xml"
oufn_c = os.path.splitext(infn)[0] + "_final.xml"

# Config
datadir = "data"
cast_data = os.path.join(datadir, "cast_list_data.tsv.ods")
set_data = os.path.join(datadir, "set_data.txt")
filedesc_data = os.path.join(datadir, "filedesc.txt")
speaker_corrections = os.path.join(datadir, "speaker_corrections.txt")
speaker_to_id_infos = os.path.join(datadir, "speaker2id.tsv")
manual_corrections = os.path.join(datadir, "manual_corrections.txt")
missing_stage_directions = os.path.join(datadir, "missing_stage_directions.txt")

# Constants

sp_close = re.compile(r"</p>")
speaker_close = re.compile(r"</speaker>")

head_re_others = re.compile(r"(<head>[^<1]+</head>)")
head_re_first = re.compile(r"(<head>[^<]+1\.[^<]+</head>)")

#stage_dir_cands_re = re.compile(r"\([^)<\n]+\):?")
stage_dir_cands_re = re.compile(r"\([^)<]+\):?")

bad_speaker_re = re.compile(r"<speaker>\s*-\s*[0-9]+\s*-\s*</speaker>")
bad_speaker_re_2 = re.compile(r"(<speaker>)\s*-\s*[0-9]+\s*-\s*(\w+)(</speaker>)")

blank_sp_re = re.compile(
        r"\s*<sp>\s*<p>\s*</p>\s*</sp>\s*",
        re.DOTALL)

# http://lxml.de/tutorial.html#namespaces
TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"
XML_NAMESPACE = "http://www.w3.org/XML/1998/"
TEI = "{%s}" % TEI_NAMESPACE
XML = "{%s}" % XML_NAMESPACE
# to output, don't add a prefix
NSMAP = {None: TEI_NAMESPACE}#, "xml": XML_NAMESPACE}
# to read TEI, do use the prefix
NSMAP_READ = {"tei": TEI_NAMESPACE,
              "xml": "http://www.foo.com"} # xml one just for adding metrics to author files
                                       # cos based on an xml:id element

#TODO QName for attributes with prefix
# https://stackoverflow.com/questions/25132998/how-to-add-namespace-prefix-to-attribute-with-lxml-node-is-with-other-namespace


def add_acts(txt):
    """
    Add act divisions.
    
    Note: Clue is <head> 1. Aufzug. </head>
    """
    txt = re.sub(head_re_first,
                 r"""<div type="act">\1""", txt.strip())
    txt = re.sub(head_re_others,
                 r"""</div>\n<div type="act">\1\n""", txt)
    txt = re.sub("</body>", r"""</div>\n</body>""", txt)
    return txt


def add_p(txt):
    """Add the p elements for each sp"""
    txt = txt.replace("</speaker>", "</speaker><p>") 
    txt = txt.replace("</sp>", "</p></sp>")
    txt = txt.replace(" </p>", "</p>")
    # delete some wrong elements
    txt = re.sub("(</speaker>)<p>(\s+<speaker>)", r"\1\2", txt)
    txt = txt.replace("ın", "in")
    return txt


def remove_bad_speakers(txt):
    """Remove speakers who are actually a page number"""
    txt = re.sub(bad_speaker_re, '', txt)
    txt = re.sub(bad_speaker_re_2, r"\1\2\3", txt)
    txt = txt.replace("<speaker> ", "<speaker>")
    txt = txt.replace("</speaker> ", "</speaker>")
    txt = re.sub("\s*</speaker>", "</speaker>", txt)
    return txt


def remove_blank_sp(txt):
    """Remove contexts in regex applied"""
    txt = re.sub(blank_sp_re, '', txt)
    return txt


def correct_apostrophes(txt):
    """Correct apostrophes"""
    txt = re.sub("d''(\w)", r"d’\1", txt)
    txt = txt.replace("'", "’")
    txt= txt.replace("‘s", "’s")
    txt= txt.replace("‘r", "’r")
    txt= txt.replace("‘n", "’n")
    txt= txt.replace("‘m", "’m")
    return txt


def correct_quotation_marks(txt):
    """Correct quotation marks"""
    txt = txt.replace(",,", "„")
    txt = txt.replace("'’", "“")
    txt = txt.replace("''", "“")
    txt = txt.replace("’’", "“")
    # „Ventrebleu!"
    txt = re.sub(re.compile("(„[^' ]+)(?:\"|[’‘']{2})"), r"\1“", txt)
    #“Parfaitement“, p. 49
    txt = re.sub(re.compile("“([^„“ ]+“)"), r"„\1", txt)
    # ,‚Pardon, patron!“
    # the character is SINGLE LOW-9 QUOTATION MARK, not a comma
    txt = re.sub(re.compile(",‚([^„“\n]+“)"), r"„\1", txt)
    return txt


def prepare_spellcheck_dicos(dicos):
    """Read series of spellcheck dictionaries into a set"""
    #TODO: Add Alsatian vocabulary from RESTAURE corpus
    words = set()
    for dico in os.listdir(dicos):
        with open(os.path.join(dicos, dico), mode="r", encoding="utf8") as fd:
            words.update(set([wo.strip() for wo in fd]))
    return words
    

def remove_hyphenation(txt, dico=None):
    """
    Remove hyphens at line-end if they are there to break up word.
    Keep hyphens that belong in word (e.g. *Baden-Baden*)
    """
    finder = "((?:^|\W)\w+)-\s(\w+(?:\W|$))"
    txt2 = txt
    deleted = 0
    for match in re.finditer(finder, txt2):
        # Steh- Kragen case
        if "{}{}".format(match.group(1).strip(), match.group(2).lower().strip()) in dico:
            txt = "".join((txt[:match.start()-deleted],
                           "".join((match.group(1), match.group(2).lower())),
                           txt[match.end()-deleted:]))
            deleted += 2
        # Bade- Bade
        elif match.group(2)[0].isupper() \
            or "{}-{}".format(match.group(1).strip(), match.group(2).strip()) in dico:
            txt = "".join((txt[:match.start()-deleted],
                           "".join((match.group(1), "-", match.group(2))),
                           txt[match.end()-deleted:]))
            deleted += 1
        # General case
        else:
            txt = "".join((txt[:match.start()-deleted],
                           "".join((match.group(1), match.group(2))),
                           txt[match.end()-deleted:]))
            deleted += 2
        # equal sign
    txt = txt.replace("= ", "=")
    return txt


def remove_dummy_elements(txt):
    """Remove placeholder elements from the example TEI template"""
    txt = re.sub(re.compile('<p>Some text.+?</figure>', re.DOTALL), "", txt)
    return txt


def add_german_stage_directions(txt):
    """
    Treat German text within parenthesis as a stage direction.
    """
    candidates = re.findall(stage_dir_cands_re, txt)
    for cand in candidates:
        stdir = cand
        if langid.classify(cand)[0] == "de":
            stdir = "".join(["<stage>",
                             cand,
                             "</stage>"])
        if stdir != cand:
            txt = txt.replace(cand, stdir)
    txt = re.sub("(?:<stage>)+", "<stage>", txt)
    txt = re.sub("(?:</stage>)+", "</stage>", txt)
    txt = re.sub("</stage>:</stage>", ":</stage>", txt)
    txt = re.sub(":{2,}", ":", txt)
    txt = re.sub("\(ab\)", "<stage>(ab)</stage>", txt)
    # strip stage element text
    txt = re.sub("<stage> ", "<stage>", txt)
    txt = re.sub("<stage>", " <stage>", txt)
    txt = re.sub(" </stage>", "</stage>", txt)
    # remove doubled stage element
    txt = re.sub("<stage>\s*<stage>", " <stage>", txt)
    txt = re.sub("</stage>\s*</stage>", "</stage>", txt)
    # problems when line after page-break rendered as stage by xslt
    txt = re.sub(re.compile(
        '</p>\s*</sp>\s*(<pb n="(?:54|89|97|56|66|73|76|83)"/>)\s*<stage>(.+?</stage>)',
        re.DOTALL),
        r"\1\2</p></sp>", txt)
    #TODO verify if this covers pages 73, 76, 83
    txt = re.sub(re.compile(
        '</p>\s*</sp>\s*(<pb n="(?:9)"/>)\s*<stage>(.+?)</stage>',
        re.DOTALL),
        r"\1\2</p></sp>", txt)
    # pages 41 and 94
    txt = re.sub(re.compile(
        """(\((?:Sie geht aufgeregt|Man zieht den Schlafenden)[^<\n]+)</p>(\s*)</sp>\s*(<pb n="(?:41|94)"/>)(\s*)<stage>(.+?)</stage>""",
        re.DOTALL),
        r"<stage>\1\2\3\4\5</stage></p></sp>", txt)
    return txt


def rearrange_delivery_stage_directions(txt):
    """
    Place stage directions finishing with *:* directly under sp.
    
    These stage directions are usually *delivery* directions and
    are better placed outside the *p* element of the *sp*. 
    
    **Example**
    
    .. code-block:: xml
        </speaker>
              <p><stage>(zu Jules):</stage>    
    """
    ctxt = """(</speaker>\s*)(<p>\s*)(<stage>\([^)]+\):</stage>)"""
    txt = re.sub(ctxt, r"\1 \3 \2", txt)
    return txt


def add_spaces_around_stage_directions(txt):
    """
    Add spaces around *stage* element.
    
    The stage element was manipulated via string operations
    rather than only with xml libraries. Some of the manipulations
    may have resulted in the actual text of the stage direction no
    longer being separated from the rest of text by a space.

    **Example**
    
    .. code-block:: xml
        worden!<stage>(Grosses Erstaunen der Anwesenden.)</stage></p>
    """
    ctxt = re.compile("(<stage>.+?</stage>)", re.DOTALL)
    txt = re.sub(ctxt, r" \1 ", txt)
    txt = re.sub("> <", "><", txt)
    return txt


def bring_back_bad_stage_to_sp_1(txt):
    """
    Correct some speeches in Alsatian tagged as <stage> by XSLT (longest context)
    """
    #TODO: move regex to module level
    candidates = re.findall(
            re.compile(
                    r"(</p></sp>\s*(<pb n=\"[0-9]+\"/>\s*<stage>[^<]+)</stage>)", re.DOTALL), txt)
    #import pdb;pdb.set_trace()
    for cand in candidates:
        #if "werikslytt" in cand[0]:
        #    import pdb;pdb.set_trace()
        if "'r" in cand[1]  or 'un ' in cand[1]:
            closed_cand = "".join([cand[1], "</p></sp>"])
            new_cand = closed_cand.replace("<stage>", " ")
            txt = txt.replace(cand[0], new_cand)
    return txt


def bring_back_bad_stage_to_sp_2(txt):
    """
    Correct some speeches in Alsatian tagged as <stage> by XSLT (second-longest context)
    """
    #TODO: move regex to module level
    candidates = re.findall(
            re.compile(
                    r"(</sp>\s*(<pb n=\"[0-9]+\"/>\s*<stage>[^<]+)</stage>)", re.DOTALL), txt)
    #import pdb;pdb.set_trace()
    for cand in candidates:
        if "'r" in cand[1] or 'un ' in cand[1]:
            closed_cand = "".join([cand[1], "</sp>"])
            closed_cand = closed_cand.replace("<stage>", " ")
            txt = txt.replace(cand[0], closed_cand)
    return txt


def read_character_info(fname, sheetname="characters"):
    """Read character infos into a dataframe"""
    df = read_ods(fname, sheetname)
    return df


def read_correction_file(fname):
    """
    Retrieve and returns infos for correcting speaker elements

    Args:
        fname (str): Name of file with correction infos
    """
    corrections = list()
    with open(fname, mode='r', encoding='utf8') as fd:
        for line in fd:
            if line.startswith("#") or len(line.strip()) == 0:
                continue
            ko, ok = line.strip("\n").split("\t")
            if len(ko) == 0 or len(ok) == 0:
                sys.exit(2)
            corrections.append((ko, ok))
    return corrections


def apply_speaker_corrections(corrs, txt):
    """
    Apply speaker element corrrections and return corrected text.

    Args:
        corrs (list):  Iterable with (wrong, correct) pairs
        txt (str): Text serialization of the XML file to correct
    """
    for co in corrs:
        # txt = txt.replace(co[0], co[1])
        txt = re.sub(co[0], co[1], txt)
    return txt


def add_set_data(set_fname, front):
    """
    Add set info to front of TEI.
    
    Args:
        set_fname (str): Name of file with set info
        front (etree.Element): front element to add info to
    """
    with open(set_fname, mode='r', encoding='utf8') as fd:
        txt = fd.read().strip()
    set_ele = etree.Element("set")
    etree.SubElement(set_ele, "p").text = txt
    front.append(set_ele)
    return front  


def add_file_desc(fdesc_fname, txt):
    """
    Add the fileDesc element to the text for the XML play (`txt`)
    The text for the element is in file `fdesc_fname`
    """
    with open(fdesc_fname, mode='r', encoding='utf8') as fd:
        fdesc = fd.read()
    txt = re.sub(re.compile(r"<fileDesc.+?/fileDesc>", re.DOTALL),
                 fdesc, txt)
    return txt


def rename_alle_old(txt):
    """
    Renames 'Alle' speakers so that can properly assign an ID to the sp.
    
    ID will be based on the series of speakers who are on stage at that point.
    """
    for idx, match in enumerate(re.finditer(
            "(<speaker>)\s*(Alle:)\s*(</speaker>)", txt)):
        txt = "".join((txt[:match.start()],
                       "{}{}{}{}".format(
                           match.group(1), match.group(2),
                           idx+1, match.group(3)),
                       txt[match.end():]))
    return txt


def rename_alle(txt):
    """
    Renames 'Alle' speakers so that can properly assign an ID to the sp.
    
    ID will be based on the series of speakers who are on stage at that point.
    """
    searchme = "<speaker>\s*Alle:\s*</speaker>"
    for idx, match in enumerate(re.findall(searchme, txt)):
        txt = re.sub(searchme, "<speaker>Alle:{}</speaker>".format(idx+1),
                     txt, count=1)
    return txt


def apply_manual_correction_list(txt, cl=manual_corrections):
    """
    Apply corrections from a list created by manual revision of the TEI.
    
    Args:
        txt (str): text to correct
        cl (str): path to file with correction list. Default comes
        from module level variables (`manual_corrections`).
    """
    ko2ok = read_correction_file(cl)
    for pair in ko2ok:
        ctxt = re.escape(pair[0]) \
            if "(" in pair[0] or ")" in pair[0] else pair[0]
        txt = re.sub(ctxt, pair[1], txt)
    return txt


def tag_missing_stage_directions(txt, ms=missing_stage_directions):
    """
    Apply corrections from a list created by manual revision of the TEI.
    
    Args:
        txt (str): text to correct
        ms (str): path to file with correction list. Default comes
        from module level variables (`missing_stage_directions`).
    """
    adds = set([ll.strip() for ll in open(ms, mode="r", encoding="utf8")
                if not ll.startswith("#")])
    for item in adds:
        txt = re.sub(
            re.escape(item),
            "".join((" <stage>", item, "</stage> ")), txt)
    txt = txt.replace("</stage> : ", ":</stage> ")
    return txt


def create_speaker_to_id_map(map_fname, tree):
    """
    Creates a mapping from speakers in play to their ID in XML `personList`.
    
    Args:
        map_fname (str): path to file containing speakers in play
        tree (etree.ElementTree): XML tree for play, with character info
    
    Note:
        In `map_fname`, speakers map to the value of persName in the XML `persList`.
        The function crosses information to map speakers to xml:id via `persName`.
        The plan was to use `occupation` if no `persName` is available, but the
        DraCor schema does not allow this, so `persName` will be used.         
    """
    
    # read character info off the XML
    c2id = {}
    character_info = tree.xpath("//person", namespaces=NSMAP_READ)
    for char in character_info:
        try:
            c2id[char.xpath("persName/text()")[0]] = "#{}".format(
                char.attrib["{}id".format(XML.replace("}", "namespace}"))])
        except IndexError:
            c2id[char.xpath("occupation/text()")[0]] = "#{}".format(
                char.attrib["{}id".format(XML.replace("}", "namespace}"))])
    # cross info with the speakers/speaker groups attested in play, from map_fname
    s2id = {}
    with open(map_fname, mode='r', encoding='utf-8') as fd:
        for line in fd:
            ids = set()
            if line.startswith("#"):
                continue
            sl = line.strip().split("\t")
            speaker, infos = sl[0], sl[1]
            characters = infos.split(";")
            for character in characters:
                if character in c2id:
                    ids.add(c2id[character])
                elif character.replace(":", "") in c2id:
                    ids.add(c2id[character.replace(":", "")])
                elif character.replace(":", "") in c2id:
                    ids.add(c2id["{}:".format(character)])
            s2id[speaker] = " ".join(sorted(ids))
    return s2id


def add_character_infos_to_tei(df, teifn, teifn_with_characters,
                               add_person_list_parents=True,
                               add_cast_list_parents=True,
                               add_cast_list_head=True,
                               custom_cast_list_head=""):
    """Add character-related infos from dataframe df to TEI fn"""
    # listPerson
    listPerson = etree.Element("listPerson")
    if add_person_list_parents:
        profileDesc = etree.Element("profileDesc")
        particDesc = etree.Element("particDesc")
        profileDesc.append(particDesc)
        particDesc.append(listPerson)
    # castList
    castList = etree.Element("castList")
    if add_cast_list_head:
        if len(custom_cast_list_head) == 0:
            etree.SubElement(castList, "head").text = "Personen."
        else:
            etree.SubElement(castList, "head").text = custom_cast_list_head
    if add_cast_list_parents:
        front = etree.Element("front")
        front.append(castList)
        
    for idx, row in df.iterrows():
        # personList
        person = etree.SubElement(listPerson, "person")
        # For attribute names with namespace, see:
        #   - https://mailman-mail5.webfaction.com/pipermail/lxml/20100326/013271.html
        #   - https://github.com/ansible/ansible/issues/31918
        person.attrib["{http://www.w3.org/XML/1998/namespace}id"] = row.personId.lower()
        
        person.attrib['sex'] = ["FEMALE" if row.sex == "F" else "MALE" if row.sex == "M" else "UNKNOWN"][0]
        # can't use 'occupation' for DraCor
        if "Handwerker" in row.persName:
            #persName = etree.SubElement(person, "occupation")
            persName = etree.SubElement(person, "persName")
        else:
            persName = etree.SubElement(person, "persName")
        persName.text = row.persName
        listPerson.append(person)
        #print(etree.tostring(person))
        # castList
        #   Handwerker not in cast list
        if "Handwerker" in row.persName:
            continue
        castItem = etree.SubElement(castList, "castItem")
        castItem.attrib['corresp'] = row.personId.lower()
        role = etree.SubElement(castItem, "role")
        role.text = row.persName        
        role.tail = ", "
        roleDesc = etree.SubElement(castItem, "roleDesc")
        roleDesc.text = row.roleDesc
        roleDesc.tail = "."
        castList.append(castItem)
    if False:
        print(etree.tostring(listPerson, with_tail=True, pretty_print=True))
        print(etree.tostring(castList, with_tail=True, pretty_print=True))
    # read TEI, remove blank text so that it can pretty print after adding elements
    #   see https://stackoverflow.com/a/7904066
    parser = etree.XMLParser(remove_blank_text=True)
    ttree = etree.parse(teifn, parser).getroot()
    # add personList to teiHeader
    teiHeader = ttree.xpath("//tei:teiHeader", namespaces=NSMAP_READ)[0]
    teiHeader.append(profileDesc)
    # create set
    front = add_set_data(set_data, front)
    
    # add front with castList and set to body
    teiText = ttree.xpath("//tei:text", namespaces=NSMAP_READ)[0]
    teiText.insert(0, front)
    
    for node in ttree.xpath("//tei:p", namespaces=NSMAP_READ):
        try:
            node.text = node.text.strip()
        except AttributeError:
            continue

    sp2id = create_speaker_to_id_map(speaker_to_id_infos, ttree)
    
    for sp in ttree.xpath("//tei:sp", namespaces=NSMAP_READ):
        spkr = sp.xpath("tei:speaker/text()", namespaces=NSMAP_READ)[0]
        try:
            sp.attrib["who"] = sp2id[spkr]
        except KeyError:
            sp.attrib["who"] = sp2id[spkr.replace(":", "")]           

    # serialize
    sertree = etree.tostring(ttree, xml_declaration=True,
                             encoding="UTF-8", pretty_print=True)
    sertree = mc.correct_serialized_xml(sertree)
    
    # why wb, see https://stackoverflow.com/questions/5512811
    with open(teifn_with_characters, "wb") as ofh:
        print("=> {}".format(os.path.basename(teifn_with_characters)))
        ofh.write(sertree)


def add_characters(cast_sheet, tei, tei_with_chars):
    """Read character info from *data* dir and add it to TEI"""
    df = read_character_info(cast_sheet)
    add_character_infos_to_tei(df, tei, tei_with_chars)   
    

def add_dracor_pi(tei_with_chars):
    """
    Add reference to DraCor schema.
    
    Note:
        Easier as done than using `lxml` library.
    """
    #TODO move to a function and config
    proci = """<?xml-model href="https://dracor.org/schema.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>\n"""   
    shutil.copy(tei_with_chars, ".temp")
    tei_with_chars_dracor = tei_with_chars.replace(
        ".xml", "_dracor.xml")
    with open(".temp", mode="r", encoding="utf8") as fd:
        lines = fd.readlines()
        lines.insert(1, proci)
    with open(tei_with_chars_dracor, mode="w", encoding="utf8") as of:
        of.write(re.sub(re.compile(
            "<respStmt.+respStmt>", re.DOTALL),
            "", "".join(lines)))
    os.remove(".temp")
    
    
def add_basic(ifn, ofn):
    """Add basic cleanup"""
    with open(ifn, mode="r", encoding="utf8") as fh:
        txt = fh.read()

    # Text-based ------------------------------------------
    txt = remove_dummy_elements(txt)
    # structural tags
    txt = add_p(txt)
    txt = add_acts(txt)
    # speakers
    txt = remove_bad_speakers(txt)
    txt = remove_blank_sp(txt)
    # stage directions
    txt = bring_back_bad_stage_to_sp_1(txt)
    txt = bring_back_bad_stage_to_sp_2(txt)
    txt = add_german_stage_directions(txt)
    txt = rearrange_delivery_stage_directions(txt)
    # punctuation
    txt = correct_apostrophes(txt)
    txt = correct_quotation_marks(txt)
    
    # Correct complex speakers
    sc = read_correction_file(speaker_corrections)
    txt = apply_speaker_corrections(sc, txt)

    # Header info     
    txt = add_file_desc(filedesc_data, txt)
    
    txt = rename_alle(txt)

    # hyphenation
    dicts = prepare_spellcheck_dicos("data/dicos")
    txt = remove_hyphenation(txt, dico=dicts)
    
    # corrections coming from manual revision go at end
    txt = apply_manual_correction_list(txt)   
    txt = tag_missing_stage_directions(txt)
    
    # final manual corrections to stage directions
    txt = mc.correct_stage_directions(txt)

    #   unused
    #txt = add_spaces_around_stage_directions(txt)

    with open(ofn, mode="w", encoding="utf8") as ofh:
        ofh.write(txt)

    # XML-based -------------------------------------------
    # Add character infos    
    add_characters(cast_data, oufn, oufn_c)

    # Add ref to DraCor schema
    add_dracor_pi(oufn_c)

if __name__ == "__main__":
    add_basic(infn, oufn)
