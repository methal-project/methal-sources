#coding=utf8

"""
Process character info for Christowe and add it to the TEI file.
"""

from lxml import etree
import os
import pandas as pd
from pandas_ods_reader import read_ods
import re
from string import punctuation
import sys
from xml.sax import saxutils

sys.path.append("../..")

import add_to_front as af
import config as cf
import oconfig as ocf
import utils.utils as ut


TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"
XML_NAMESPACE = "http://www.w3.org/XML/1998/"
TEI = "{%s}" % TEI_NAMESPACE
XML = "{%s}" % XML_NAMESPACE
# to output, don't add a prefix
NSMAP = {None: TEI_NAMESPACE}#, "xml": XML_NAMESPACE}
# to read TEI, do use the prefix
NSMAP_READ = {"tei": TEI_NAMESPACE,
              "xml": "http://www.foo.com"}

DBG = False


def read_character_info(fname, sheetname=ocf.character_sheet_name):
    """Read character infos into a dataframe"""
    df = read_ods(fname, sheetname)
    return df


def find_character_group_ranges_in_df(df):
    """
    Find the ranges (column _cgrp_) that will be part of  TEI `<castGroup>`
    elements, based on the dataframe with character information.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame

    Returns
    -------
    list
        List of ranges as :obj:`range` objects
    """
    rgs = set(df['cgrp'])
    tups = [(int(tu.split("-")[0]), int(tu.split("-")[1]))
            for tu in rgs if tu is not None]
    full_ranges = [range(tu[0], tu[1]+1) for tu in tups]
    return full_ranges


def check_position_of_id_in_range(id_, rges):
    """
    Check whether an integer is in an integer range, return position indicator.

    Parameters
    ----------
    id_ : int
        Integer to check against a list of ranges
    rges : list
        List of :obj:`range` objects

    Returns
    -------
    int
        Indicator of position of integer in range (if found),
        distinguishing between initial, mid or final. Otherwise
        return -9 when integer is not in range.
        Details below:
          * 0: first position
          * -1: last position
          * 1: mid (between first and last)
          * -9: not found
    """
    place = []
    myrge = [rg for rg in rges if id_ in rg]
    if len(myrge) == 0:
        place.append(-9)
    elif myrge[0].index(id_) == 0:
        place.append(0)
    elif myrge[0].index(id_) == len(myrge[0]) - 1:
        place.append(-1)
    else:
        place.append(1)
    return place[0]


def add_characters(cast_sheet, tei, tei_with_chars):
    """Read character info from _data_ dir and add it to TEI"""
    df = read_character_info(cast_sheet)
    if DBG:
        print(df.head())
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
    #TODO switch docstring to Numpy style

    # read character info off the XML
    c2id = {}
    character_info = tree.xpath("//person|//personGrp", namespaces=NSMAP_READ)
    for char in character_info:
        try:
            c2id["".join(char.xpath("persName//text()"))] = "#{}".format(
                char.attrib["{}id".format(XML.replace("}", "namespace}"))])
        # now allow rows without ID (if needed for castList but not for personList)
        except (IndexError, KeyError):
            pass
            # c2id[char.xpath("occupation/text()")[0]] = "#{}".format(
            #     char.attrib["{}id".format(XML.replace("}", "namespace}"))])
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


def format_character_info(info, tag_name, cf):
    """
    Adds italics and other (simple) format to strings used to build XML elements with,
    for play characters mainly.

    Note
    ----
    Was originally used to tag French words in Alsatian speech in italics, these were
    marked with # in the cast information dataframe. Thence the implementation below.

    Parameters
    ----------
    info : str
        The string to format (a character name, a role description etc.)
    tag_name : str
        Meant to treat persName or roleDesc as tags (others may work)
    cf : module
        Configuration module

    Returns
    -------
    str
        String that expresses the formatted XML element
    """

    if cf.add_period_to_roledesc and tag_name == "roleDesc":
        period = "."
    else:
        period = ""
    french_name_part = r"#([^#]+)#"
    has_french_name_part = re.search(french_name_part, info)
    part_rep = r"<emph rend='italic'>\1</emph>"
    french_name_full = r"#([^#]+)$"
    has_french_name_full = re.search(french_name_full, info)
    if has_french_name_part:
        formatted_name = re.sub(french_name_part, part_rep,
                                info)
        ele_str = "".join((f"<{tag_name}>", formatted_name, f"{period}</{tag_name}>"))
    elif has_french_name_full:
        formatted_name = re.sub(french_name_full, r"<emph rend='italic'>\1</emph>",
                                info)
        ele_str = "".join((f"<{tag_name}>", formatted_name, f"{period}</{tag_name}>"))
    else:
        ele_str = "".join((f"<{tag_name}>", info, f"{period}</{tag_name}>"))
    return ele_str


def add_summary_to_front(sfn, title):
    """
    Adds a div with @type _front_ to the `<front>` element.
    Can be used for a play summary (Inhaltsangabe etc.,
    as seen in _Poetisch Oscar_)

    Parameters
    ----------
    sfn : str
        Filename for hOCR file for the page where summary is found
    title : str
        Will be added to the `<div>` element in a `<head>` element
    Returns
    -------
    str
        A string representing the XML for the div
    """
    tree = etree.parse(sfn)
    txt = " ".join(tree.xpath(".//span[@class='ocrx_word']//text()"))
    txt = re.sub(fr"\s*{title}\s*", "", txt)
    clean_title = ut.simple_dehyphenation(title)
    clean_title = ut.change_apos_to_squo_str(clean_title)
    clean_title = ut.change_lsquo_to_rsquo_str(clean_title)
    clean_title = saxutils.escape(clean_title)
    clean_txt = ut.simple_dehyphenation(txt)
    clean_txt = ut.change_apos_to_squo_str(clean_txt)
    clean_txt = ut.change_lsquo_to_rsquo_str(clean_txt)
    clean_txt = saxutils.escape(clean_txt)
    xstr = "".join((f"<div type='front' xml:lang='ger'><head>{(clean_title)}</head>",
                    f"<p>{saxutils.escape(clean_txt)}</p></div>"))
    return xstr


def create_long_set_for_front(sfn, title, cfg=cf, start_at=None):
    """
    Creates a `<set>` element with long set info, to add to the `<front>`
    element.

    Parameters
    ----------
    sfn : str
        Filename for hOCR file for the page where set information is found
    title : str
        Will be added to the `<set>` element in a `<head>` element
    cfg : module, optional
        A configuration module, used to set the language id for the element
        (given in that configuration) unless the language is Alsatian
    start_at : int, optional.
        Which position (word span element) to start accumulating words from
        in the page at `sfn`.
        The default value is None, which indicates that the entire page content
        needs to be considered.
    Returns
    -------
    str
        A string representing the XML for the div

    Note
    ----
    This is used both for cases where the page contains a title and text (̀start_at̀
    will be None) and cases where only part of the page (from ̀start_at̀ value on)
    is collected in the div. This explains role of ̀start_at̀ in the implementation.

    """
    #TODO: title will be off it has more than one word, right?
    tree = etree.parse(sfn)
    spans = tree.xpath(".//span[@class='ocrx_word']//text()")
    # cases where start collecting at start_at
    if start_at is not None:
        span_start, skip_spans = start_at, 0
    # otherwise start collecting at title index
    else:
        span_start, skip_spans = spans.index(title), 1
    txt = " ".join(
        tree.xpath(".//span[@class='ocrx_word']//text()")[span_start+skip_spans:])
    # when collecting from title index onwards
    if start_at is None:
        txt = re.sub(fr"\s*{title}\s*", "", txt)
        clean_title = ut.simple_dehyphenation(title)
        clean_title = ut.change_apos_to_squo_str(clean_title)
        clean_title = ut.change_lsquo_to_rsquo_str(clean_title)
        clean_title = saxutils.escape(clean_title)
    clean_txt = ut.simple_dehyphenation(txt)
    clean_txt = ut.change_apos_to_squo_str(clean_txt)
    clean_txt = ut.change_lsquo_to_rsquo_str(clean_txt)
    clean_txt = re.sub(r"^\s*:", "", saxutils.escape(clean_txt))
    # xstr = "".join((f"<div type='set' xml:lang='ger'><head>{(clean_title)}</head>",
    #                 f"<p>{saxutils.escape(clean_txt)}</p></div>"))
    if cfg.long_set_language != "gsw":
        langid = f" xml:lang='{cfg.long_set_language}'"
    else:
        langid = ""
    # i.e. there is a title and text
    if start_at is None:
        xstr = "".join((f"<set{langid}><head>{(clean_title)}</head>",
                        f"<p>{saxutils.escape(clean_txt)}</p></set>"))
    # only text after a given span
    else:
        xstr = f"<p>{saxutils.escape(clean_txt)}</p>"
    return xstr


def add_tails_in_cast_list_item(cf, role, roleDesc=None, period_to="roleDesc"):
    """
    Adds a tail to the _role_ or _roleDesc_ elements in a castList,
    based on configuration _cf_

    Parameters
    ----------
    cf : module
        Configuration that defines whether to add periods as tail
    role : lxml.etree._Element
        XML element for the role name
    roleDesc : lxml.etree._Element, optional
        XML element for the role description. Default is `None`
    period_to : {'roleDesc', 'role'}, optional
        Which node to add a period to: `<roleDesc>` (default) or `role`

    Returns
    -------
    None
    """
    assert period_to in ("roleDesc", "role")
    if period_to == "roleDesc":
        role.tail = ", "
        if not roleDesc.text.endswith(".") and cf.add_period_to_roledesc:
            roleDesc.tail = "."
    elif period_to == "role":
        try:
            if not role.text.endswith(".") and cf.add_period_to_role:
                role.tail = "."
        except AttributeError:
            txt = "".join(role.xpath(".//text()"))
            if not txt.endswith(".") and cf.add_period_to_role:
                role.tail = "."


def add_character_infos_to_tei(df, teifn, teifn_with_characters,
                               add_person_list_parents=True,
                               add_cast_list_parents=True,
                               add_cast_list_head=True,
                               custom_cast_list_head=""):
    """
    Add character-related infos from dataframe df to TEI fn.

    Note
    ----
    The function now also adds the `<set>` element (and `<encodingDesc>` element
    and genre information (`<textClass>`) if available).

    It would be better to refactor this so that the main script can import functions
    adding those elements (which are unrelated to characters) independently of
    this function and keep character-related additions in this function.
    """
    # find ranges of characters (as per _persID_) for <castGroup> elements
    cgroups = find_character_group_ranges_in_df(df)
    # create listPerson and castList ==========================================
    #   listPerson
    listPerson = etree.Element("listPerson")
    if add_person_list_parents:
        profileDesc = etree.Element("profileDesc")
        particDesc = etree.Element("particDesc")
        profileDesc.append(particDesc)
        particDesc.append(listPerson)
    #   castList
    castList = etree.Element("castList")
    if add_cast_list_head:
        if len(custom_cast_list_head) == 0:
            etree.SubElement(castList, "head").text = "Persone:"
        else:
            etree.SubElement(castList, "head").text = custom_cast_list_head
    if add_cast_list_parents:
        front = etree.Element("front")
        front.append(castList)

    # populate listPerson and castList ========================================
    last_group_role_desc = None
    for idx, row in df.iterrows():
        # listPerson
        if row.grp == 0:
            person = etree.SubElement(listPerson, "person")
        else:
            person = etree.SubElement(listPerson, "personGrp")
        try:
            person.attrib["{http://www.w3.org/XML/1998/namespace}id"] = create_person_id(row.personId)
            person.attrib['sex'] = ["FEMALE" if row.sex == "F" else "MALE" if row.sex == "M" else "UNKNOWN"][0]
        except AttributeError:
            pass
        if row.persName.startswith("~"):
            continue
        # can't use 'occupation' for DraCor
        if "Handwerker" in row.persName:
            # persName = etree.SubElement(person, "occupation")
            persName = etree.SubElement(person, "persName")
        else:
            persName_str = format_character_info(row.persName, "persName", cf)
        # append persName element to person element
        person.append(etree.fromstring(persName_str))
        listPerson.append(person)
        if DBG:
            print(etree.tostring(person))

        # castList
        if row.cl == 0:
            continue
        #   create castGroup if needed
        id_place = check_position_of_id_in_range(int(row['persId']), cgroups)
        #   castGroup starts: append castItem to the group
        if id_place == 0:
            current_castGroup = etree.SubElement(castList, "castGroup")
            castItem = etree.SubElement(current_castGroup, "castItem")
        #   castGroup mid or end
        elif id_place in(1, -1):
            castItem = etree.SubElement(current_castGroup, "castItem")
        #   no castGroup (id_place is None): append castItem to the list
        else:
            castItem = etree.SubElement(castList, "castItem")
        try:
            castItem.attrib['corresp'] = "#{}".format(create_person_id(row.personId))
        except AttributeError:
            pass

        # role element
        role = etree.SubElement(castItem, "role")
        # append persName element to role element
        role.append(etree.fromstring(persName_str))

        # roleDesc
        roleDesc_group = last_group_role_desc
        if row.roleDesc is not None:
            if "}" in row.roleDesc:
                roles = re.search(r"^([^}]+)}(.+)$", row.roleDesc)
                assert roles and len(roles.groups()) == 2
                roles_c = [rr.strip() for rr in roles.groups()]
                assert len(roles_c) == 2
                indiv_role, group_role = roles_c[0], roles_c[1]
            else:
                #TODO: refactor as artificial to have group_role when no castGroup
                indiv_role, group_role = row.roleDesc, row.roleDesc
            #roleDesc_str = format_character_info(row.roleDesc, "roleDesc")
            roleDesc_indiv_str = format_character_info(indiv_role, "roleDesc", cf)
            roleDesc_group_str = format_character_info(group_role, "roleDesc", cf)
            try:
                if not pd.isnull(row.age) and cf.add_character_age:
                    roleDesc_indiv_str = roleDesc_indiv_str.replace("</roleDesc>", f", {row.age}</roleDesc>")
                    roleDesc_group_str = roleDesc_indiv_str.replace("</roleDesc>", f", {row.age}</roleDesc>")
            except AttributeError:
                pass
            roleDesc_indiv = etree.fromstring(roleDesc_indiv_str)
            # roledesc_str_for_group = roleDesc_group_str + "." if cf.add_period_to_roledesc \
            #     else roleDesc_group_str
            roleDesc_group = etree.fromstring(roleDesc_group_str)
        #   if in a castGroup, first element in group has the roleDesc in data frame
        #   but needs to be added to the castGroup (not castItem) after the last
        #   element in the group
        if id_place == 0:
            last_group_role_desc = roleDesc_group
            if roleDesc_indiv_str != roleDesc_group_str:
                add_tails_in_cast_list_item(cf, role, roleDesc_indiv)
                castItem.append(roleDesc_indiv)
        elif id_place == -1:
            current_castGroup.append(last_group_role_desc)
            last_group_role_desc = None
            # roleDesc for group only filled in first member of castGroup
            # if member has both an individual and group role, these conditions apply
            if ((roleDesc_indiv_str != roleDesc_group_str) or
                    (row.roleDesc is not None and "}" not in row.roleDesc)):
                add_tails_in_cast_list_item(cf, role, roleDesc_indiv)
                castItem.append(roleDesc_indiv)
        elif id_place == 1:
            # "}" is there when id_place is 0
            # condition is a way to add the individual role to mid castItem elements
            # in castGroup
            if row.roleDesc is not None and "}" not in row.roleDesc:
                add_tails_in_cast_list_item(cf, role, roleDesc_indiv)
                castItem.append(roleDesc_indiv)
        #   outside castGroup (general case) append to castItem
        elif id_place == -9:
            # add comma after role name if a description follows
            if row.roleDesc is not None:
                add_tails_in_cast_list_item(cf, role, roleDesc_indiv)
                castItem.append(roleDesc_indiv)
            else:
                # add period after role name (configurable)
                if cf.add_period_to_role:
                    add_tails_in_cast_list_item(cf, role, period_to="role")
        else:
            pass
        #castList.append(castItem)
    if DBG:
        print(etree.tostring(listPerson, with_tail=True, pretty_print=True))
        print(etree.tostring(castList, with_tail=True, pretty_print=True))

    # add relations ===========================================================
    listPerson.append(
        etree.fromstring(open(os.path.join(cf.datadir, "relations.xml"),
                              mode="r", encoding="utf8").read()))

    # add genre classification to profileDesc =================================
    play_md_df = ut.read_header_info()
    play_md = ut.get_play_metadata_by_id(play_md_df, cf.play_id)
    genre = play_md['genre'].lower().strip()
    text_class = etree.SubElement(profileDesc, "textClass")
    genre_keywords = etree.SubElement(text_class, "keywords")
    genre_title = etree.SubElement(genre_keywords, "term", type="genreTitle").text = genre

    # add set =================================================================
    set_ele = ut.get_set_by_id(ocf.play_set_data, cf.play_id)
    #  easier format if create from string
    set_ele_str = etree.tostring(set_ele)
    front.append(etree.fromstring(set_ele_str))

    # add summary or other set info to front ==================================
    long_set_div = etree.fromstring(
        create_long_set_for_front(cf.summary_fpath, cf.summary_title))
    
    front.append(long_set_div)

    # add character description page ==========================================
    #   character description
    af.add_character_description_to_front(front)
    #   set info below it
    div_for_additional_set = etree.SubElement(front, "div", type="set")
    second_set_str = create_long_set_for_front(
        cf.second_set_info_fpath, "", start_at=cf.start_second_set)
    second_set_ele = etree.fromstring(second_set_str)
    div_for_additional_set.append(second_set_ele)


    # merge body+header and front =============================================
    #   see https://stackoverflow.com/a/7904066
    parser = etree.XMLParser(remove_blank_text=True)
    ttree = etree.parse(teifn, parser).getroot()
    teiHeader = ttree.xpath("//tei:teiHeader", namespaces=NSMAP_READ)[0]

    # add profileDesc
    teiHeader.append(profileDesc)

    # add encodingDesc
    if cf.add_encoding_desc:
        encodingDesc_str = ut.read_encoding_desc_from_file()
        teiHeader.append(etree.fromstring(encodingDesc_str))

    # add front with castList and set to body
    ttree.getchildren()[1].insert(0, front)

    #TODO: verify
    for node in ttree.xpath("//tei:p", namespaces=NSMAP_READ):
        try:
            node.text = node.text.strip()
        except AttributeError:
            continue

    # add speaker ids =========================================================
    sp2id = create_speaker_to_id_map(cf.speaker_to_id_infos, ttree)
    if DBG:
        print(sp2id)

    for sp in ttree.xpath("//tei:sp", namespaces=NSMAP_READ):
        spkr = "".join(sp.xpath("tei:speaker//text()", namespaces=NSMAP_READ))
        try:
            sp.attrib["who"] = sp2id[spkr]
        except KeyError:
            sp.attrib["who"] = sp2id[re.sub(r"[:.]", "", spkr)]


    # serialize ===============================================================
    sertree = etree.tostring(ttree, xml_declaration=True,
                             encoding="UTF-8", pretty_print=True)

    sertree = ut.add_space_around_stage_directions_b(sertree)

    # why wb, see https://stackoverflow.com/questions/5512811
    with open(teifn_with_characters, "wb") as ofh:
        print("=> {}".format(os.path.basename(teifn_with_characters)))
        # improve spaces around seg
        sertree = re.sub(b"><seg", b"> <seg", sertree)
        sertree = re.sub(b"(\w)<seg", br"\1 <seg", sertree)
        sertree = re.sub(br"([,.])<seg", br"\1 <seg", sertree)
        # apostrophes to quote
        sertree = ut.change_apos_to_squo_b(sertree)
        sertree = ut.change_lsquo_to_rsquo_b(sertree)
        ofh.write(sertree)


if __name__ == "__main__":
    add_characters(cf.cast_list_data, cf.oufn, cf.oufn_with_characters)

    # add CSS or not
    if True:
        txt = open(cf.oufn_with_characters).read()
        if not "tei-drama.css" in txt:
            os.system(
                """sed -i.bak -e 's%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%<?xml-stylesheet type="text/css" href="../../../css/tei-drama.css"?>\\n<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(cf.oufn_with_characters))
    os.system("xmllint --relaxng {} {} > bla ; mv bla {}".format(
        ocf.tei_rng, cf.oufn_with_characters, cf.oufn_with_characters))
