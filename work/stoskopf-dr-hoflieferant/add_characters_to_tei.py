#coding=utf8

"""
Process character info for D'r Hoflieferant and add it to the TEI file.
Corrections to the text are also made, at the end.
"""

from lxml import etree
import os
from pandas_ods_reader import read_ods
import re

import config as cf


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


def read_character_info(fname, sheetname="characters"):
    """Read character infos into a dataframe"""
    df = read_ods(fname, sheetname)
    return df


def add_characters(cast_sheet, tei, tei_with_chars):
    """Read character info from *data* dir and add it to TEI"""
    df = read_character_info(cast_sheet)
    add_character_infos_to_tei(df, tei, tei_with_chars)


def create_speaker_to_id_map(map_fname, tree):
    """
    Creates a mapping from speakers in play to their ID in XML `listPerson`.

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
    character_info = tree.xpath("//person|//personGrp", namespaces=NSMAP_READ)
    for char in character_info:
        try:
            c2id["".join(char.xpath("persName//text()"))] = "#{}".format(
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
                elif character.replace("", ":") in c2id:
                    ids.add(c2id["{}:".format(character)])
            s2id[speaker] = " ".join(sorted(ids))
    return s2id


def create_person_id(txt):
    txt = txt.lower()
    txt = txt.replace(" ", "_")
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
    set_ele = etree.fromstring(txt)
    #etree.SubElement(set_ele, "p").text = txt
    front.append(set_ele)
    return front


def format_character_info(info, tag_name):
    """
    Add emph where needed to character names or roleDesc,
    as this information is important in this play
    (italic = French pronunciation or French word).
    """
    french_name_part = r"#([^#]+)#"
    has_french_name_part = re.search(french_name_part, info)
    part_rep = r"<emph rend='italic'>\1</emph>"
    french_name_full = r"#([^#]+)$"
    has_french_name_full = re.search(french_name_full, info)
    if has_french_name_part:
        formatted_name = re.sub(french_name_part, part_rep,
                                info)
        ele_str = "".join((f"<{tag_name}>", formatted_name, f"</{tag_name}>"))
    elif has_french_name_full:
        formatted_name = re.sub(french_name_full, r"<emph rend='italic'>\1</emph>",
                                info)
        ele_str = "".join((f"<{tag_name}>", formatted_name, f"</{tag_name}>"))
    else:
        ele_str = "".join((f"<{tag_name}>", info, f"</{tag_name}>"))
    return ele_str


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
        # listPerson
        if row.grp == 0:
            person = etree.SubElement(listPerson, "person")
        else:
            person = etree.SubElement(listPerson, "personGrp")
        # For attribute names with namespace, see:
        #   - https://mailman-mail5.webfaction.com/pipermail/lxml/20100326/013271.html
        #   - https://github.com/ansible/ansible/issues/31918
        #person.attrib["{http://www.w3.org/XML/1998/namespace}id"] = row.personId.lower()
        person.attrib["{http://www.w3.org/XML/1998/namespace}id"] = create_person_id(row.personId)

        person.attrib['sex'] = ["FEMALE" if row.sex == "F" else "MALE" if row.sex == "M" else "UNKNOWN"][0]
        if row.persName.startswith("~"):
            continue
        # can't use 'occupation' for DraCor
        if "Handwerker" in row.persName:
            # persName = etree.SubElement(person, "occupation")
            persName = etree.SubElement(person, "persName")
        else:
            persName_str = format_character_info(row.persName, "persName")
        # append persName element to person element
        person.append(etree.fromstring(persName_str))
        listPerson.append(person)
        # print(etree.tostring(person))

        # castList
        if row.cl == 0:
            continue
        castItem = etree.SubElement(castList, "castItem")
        castItem.attrib['corresp'] = "#{}".format(create_person_id(row.personId))
        role = etree.SubElement(castItem, "role")
        # append persName element to role element
        role.append(etree.fromstring(persName_str))
        if row.roleDesc is not None:
            role.tail = ", "
        #roleDesc = etree.SubElement(castItem, "roleDesc")
        try:
            roleDesc_str = format_character_info(row.roleDesc, "roleDesc")
            #roleDesc.append(etree.fromstring(roleDesc_str))
            roleDesc = etree.fromstring(roleDesc_str)
            if not roleDesc.text.endswith("."):
                roleDesc.tail = "."
            castItem.append(roleDesc)
        except TypeError:
            pass
        castList.append(castItem)
    if False:
        print(etree.tostring(listPerson, with_tail=True, pretty_print=True))
        print(etree.tostring(castList, with_tail=True, pretty_print=True))
    listPerson.append(
        etree.fromstring(open(os.path.join(cf.datadir, "relations.xml"),
                              mode="r", encoding="utf8").read()))
    # read TEI, remove blank text so that it can pretty print after adding elements
    #   see https://stackoverflow.com/a/7904066
    parser = etree.XMLParser(remove_blank_text=True)
    ttree = etree.parse(teifn, parser).getroot()
    teiHeader = ttree.xpath("//tei:teiHeader", namespaces=NSMAP_READ)[0]
    teiHeader.append(profileDesc)
    # create set
    front = add_set_data(cf.set_data, front)

    # add front with castList and set to body
    teiText = ttree.xpath("//tei:text", namespaces=NSMAP_READ)[0]
    teiText.insert(0, front)

    for node in ttree.xpath("//tei:p", namespaces=NSMAP_READ):
        try:
            node.text = node.text.strip()
        except AttributeError:
            continue

    sp2id = create_speaker_to_id_map(cf.speaker_to_id_infos, ttree)

    for sp in ttree.xpath("//tei:sp", namespaces=NSMAP_READ):
        spkr = "".join(sp.xpath("tei:speaker//text()", namespaces=NSMAP_READ))
        try:
            sp.attrib["who"] = sp2id[spkr]
        except KeyError:
            sp.attrib["who"] = sp2id[re.sub(r"[:.]", "", spkr)]

    # serialize
    sertree = etree.tostring(ttree, xml_declaration=True,
                             encoding="UTF-8", pretty_print=True)

    # why wb, see https://stackoverflow.com/questions/5512811
    with open(teifn_with_characters, "wb") as ofh:
        print("=> {}".format(os.path.basename(teifn_with_characters)))
        # prepare to put back spaces before certain tags
        sertree = re.sub(r"([\w,.:;?!—])(<emph|<stag)".encode(), rb"\1#####\2", sertree)
        # FINAL CORRECTIONS ===================================================
        # add castGroup
        sertree = sertree.replace(b", <roleDesc>Kinder der beiden</roleDesc>.</castItem>",
                                  b",</castItem>")
        sertree = sertree.replace(b"""<castItem corresp="#jeannette"><role>""",
                                  b"""<castGroup><castItem corresp="#jeannette"><role>""")
        sertree = sertree.replace(b"""Lisa Grinsinger</emph></persName></role>,</castItem>""",
                                  b"""Lisa Grinsinger</emph></persName></role>, </castItem><roleDesc>Kinder der beiden</roleDesc></castGroup>""")
        # prevent stage direction running into speech when there's italics
        sertree = re.sub(b"""(\S)(</stage>\)?<emph rend="italic">)(\S)""",
                         br"\1\2 \3", sertree)
        sertree = sertree.replace("""la „Sambre et Meuse“</emph><stage>(Fritz <""".encode(),
                                  """la „Sambre et Meuse“ </emph><stage>(Fritz <""".encode())
        sertree = sertree.replace(b"main de ce brave</emph><stage>(geht",
                                  b"main de ce brave </emph><stage>(geht")
        # remove strange case stuff with italics
        sertree = re.sub(b"""(<stage>\(zu <emph rend="italic">de Rose</emph>\))(</stage>)\s*<emph rend="italic">: </emph>""",
                         br"""\1:\2""", sertree)
        # missing stage direction
        sertree = sertree.replace(b"""(<emph rend="italic">Auguste</emph> und Ehrstein verraten grosse Aufregung)""",
                                  b"""<stage>(<emph rend="italic">Auguste</emph> und Ehrstein verraten grosse Aufregung)</stage>""")
        # missing parenthesis
        sertree = sertree.replace(
            b"""<stage>(zu <emph rend="italic">Grinsinger</emph></stage>""",
            b"""<stage>(zu <emph rend="italic">Grinsinger</emph>)</stage>""")
        # correct apostrophes
        sertree = re.sub(br"'([srmn])", r"’\1".encode(), sertree)
        # tokens that mix italics and normal
        sertree = sertree.replace("""<emph rend="italic">e-n-émotion</emph>""".encode(),
                                  """e-n-<emph rend="italic">émotion</emph>""".encode())
        sertree = sertree.replace("""de-n-Auguste""".encode(),
                                  """de-n-<emph rend="italic">Auguste</emph>""".encode())
        ofh.write(sertree)


if __name__ == "__main__":
    add_characters(cf.cast_list_data, cf.oufn, cf.oufn_with_characters)

    # put back spaces before certain tags
    os.system("sed -i.bak 's/#####/ /g' {}".format(cf.oufn_with_characters))

    # add CSS or not
    if True:
        os.system(
            """sed -i.bak -e 's%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%<?xml-stylesheet type="text/css" href="css/tei-drama.css"?>\\n<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(cf.oufn_with_characters))
        os.system("xmllint --format  {}> bla ; mv bla {}".format(
            cf.oufn_with_characters, cf.oufn_with_characters))
