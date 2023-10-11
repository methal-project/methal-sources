#coding=utf8

"""
Utilities for play encoding.
"""

from lxml import etree
import os
import pandas as pd
from pandas_ods_reader import read_ods
import re
import sys
from xml.sax import saxutils

sys.path.append("..")

import config as cf
import oconfig as ocf


def read_character_info(fname, sheetname=ocf.character_sheet_name):
    """Read character infos into a dataframe"""
    assert(os.path.exists(fname))
    df = read_ods(fname, sheetname)
    return df


def read_header_info(fname=cf.cast_list_data,
                     sheetname=ocf.header_sheet_name):
    """Read metadata for teiHeader into a dataframe"""
    df = read_ods(fname, sheetname)
    return df


def get_play_metadata_by_id(df, play_id):
    """
    Given a dataframe with metadata for different plays,
    return the row for the given play_id
    """
    dfrow = df.loc[df['workId'] == play_id]
    assert len(dfrow.index) == 1
    return dfrow.iloc[0]


def format_sheet_metadata(txt):
    """Format metadata for teiHeader based on the metadata spreadsheet"""
    txt = txt.replace("^", "")
    txt = re.sub(r"~+", "", txt)
    return txt


def create_resp_stmt(od):
    """
    Create resp_stmt element from an :obj:`OrderedDict`
    """
    keep = [(saxutils.escape(na), saxutils.escape(rs))
            for (na, rs) in od if od[(na, rs)] is True]
    out = []
    for (name, resp) in keep:
        out.append(f"<respStmt><name>{name}</name><resp>{resp}</resp></respStmt>")
    return out


def read_encoding_desc_from_file(fpath=cf.encoding_desc_fpath):
    """
    Read text for the `<encodingDesc>` element from a file.

    Parameters
    ----------
    fpath : str, optional
        Path to the file that contains the string for the `<encodingDesc>` element.
        Default path is given in module :obj:`config`

    Returns
    -------
    str
        The text
    """
    return open(fpath, mode="r", encoding="utf8").read()


def create_tei_header(row, other=None):
    """
    Create teiHeader element based on informations in a dataframe row
    and in an optional dictionary.
    The row can be retrieved with :func:`get_play_metadata_by_id`.
    """
    hdr = etree.Element("teiHeader")
    # structure
    fileDesc = etree.Element("fileDesc")
    #  fileDesc
    titleStmt = etree.Element("titleStmt")
    publicationStmt = etree.Element("publicationStmt")
    sourceDesc = etree.Element("sourceDesc")
    #  titleStmt
    etree.SubElement(titleStmt, "title", type="main").text = \
        format_sheet_metadata(row.titleMain)
    etree.SubElement(titleStmt, "title", type="sub").text = \
        format_sheet_metadata(row.titleSub)
    assert not pd.isnull(row.authorKeyWikidata)
    try:
        author_keystr = " ".join((f"wikidata:{row.authorKeyWikidata}",
                                  f"bnf:{str(int(row.authorKeyBnf))}"))
    except ValueError:
        author_keystr = f"wikidata:{row.authorKeyWikidata}"
    etree.SubElement(titleStmt, "author", key=author_keystr).text = row.author
    for resp in create_resp_stmt(other["respStmt"]):
        titleStmt.append(etree.fromstring(resp))
    #  publicationStmt
    etree.SubElement(publicationStmt, "publisher").text = \
        "LiLPa - Université de Strasbourg"
    availability_str = other["availability"]
    publicationStmt.append(etree.fromstring(availability_str))
    wikidata_id = etree.SubElement(publicationStmt, "idno", type="wikidata")
    wikidata_id.text = row.wikidata
    wikidata_id.attrib["{http://www.w3.org/XML/1998/namespace}base"] = \
        "https://www.wikidata.org/entity/"
    for ele in (titleStmt, publicationStmt):
        fileDesc.append(ele)
    #  sourceDesc
    if other is not None and "bibl" in other:
        row = other["bibl"]
    bibl_digi = etree.Element("bibl", type="digitalSource")
    bibl_orig = etree.Element("bibl", type="originalSource")
    etree.SubElement(bibl_digi, "name").text = "Numistral"
    etree.SubElement(bibl_digi, "idno", type="URL").text = \
        cf.numistral_prefix + row["numistralSource"]
    #   author
    try:
        author2 = row["author"] if not pd.isnull(row["author2"]) \
            and row["author"] == row["author2"] else row["author2"]
    except KeyError:
        author2 = row["author"]
    if pd.isnull(row["authorKeyBnf"]) or pd.isnull(row["authorKeyWikidata2"]):
        authorKeyWikidata2 = row["authorKeyWikidata"]
        author_keystr2 = f"wikidata:{authorKeyWikidata2}"
    else:
        try:
            authorKeyWikidata2 = row["authorKeyWikidata"] if not pd.isnull(["authorKeyWikidata2"]) \
                and row["authorKeyWikidata2"] == row["authorKeyWikidata"] else row["authorKeyWikidata2"]
        except KeyError:
            authorKeyWikidata2 = row["authorKeyWikidata"]
        try:
            authorKeyBnf2 = row["authorKeyBnf"] if not pd.isnull(row["authorKeyBnf2"]) \
                and row["authorKeyBnf2"] == row["authorKeyBnf"] else row["authorKeyBnf2"]
        except KeyError:
            authorKeyBnf2 = row["authorKeyBnf"]
        author_keystr2 = f"wikidata:{authorKeyWikidata2} bnf:{str(int(authorKeyBnf2))}"
    etree.SubElement(bibl_orig, "author", key=author_keystr2).text = \
        format_sheet_metadata(author2)
    #   title
    etree.SubElement(bibl_orig, "title", type="main").text = \
        format_sheet_metadata(row.titleMain)
    etree.SubElement(bibl_orig, "title", type="sub").text = \
        format_sheet_metadata(row.titleSub)
    #  publisher
    try:
        publisher2 = row["publisher"] if pd.isnull(row["publisher2"]) \
            and row["publisher2"] == row["publisher"] else row["publisher2"]
    except KeyError:
        publisher2 = row["publisher"]
    etree.SubElement(bibl_orig, "publisher").text = format_sheet_metadata(publisher2)
    #   dates
    if not pd.isnull(row.premiere):
        etree.SubElement(bibl_orig, "date", type="premiere",
                         when=f"{str(int(row.premiere))}").text = str(int(row.premiere))
    if not pd.isnull(row.print):
        etree.SubElement(bibl_orig, "date", type="print",
                         when=f"{str(int(row.print))}").text = str(int(row.print))
    elif not pd.isnull(row.thisEdition):
        etree.SubElement(bibl_orig, "date", type="print",
                         when=f"{str(int(row.thisEdition))}").text = str(int(row.thisEdition))
    if not pd.isnull(row.written):
        etree.SubElement(bibl_orig, "date", type="written",
                         when=f"{str(int(row.written))}").text = str(int(row.written))
    else:
        bibl_orig.append(etree.Element("date", type="written"))
    bibl_digi.append(bibl_orig)
    sourceDesc.append(bibl_digi)
    # append to teiHeader
    fileDesc.append(sourceDesc)
    hdr.append(fileDesc)
    return hdr


def get_set_by_id(set_fn, set_id):
    """
    Get set element from play sets file using id in metadata/character sheet.
    """
    tree = etree.parse(set_fn)
    play = tree.xpath(f"//play[id='{set_id}']")
    assert len(play) == 1
    set_e = play[0].xpath("./set")[0]
    return set_e


def get_set_from_file(set_fname, front):
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


def simple_dehyphenation(text):
    """
    Delete hyphens and space following them as a naïve way to
    dehyphenate words at line-end.
    """
    text = re.sub(re.compile(r"(\w)- (\w)"), r"\1\2", text)
    text = re.sub(re.compile(r"(e-n)(\w)"), r"\1-\2", text)
    text = re.sub(re.compile(r"(Sainte)(C)"), r"\1-\2", text)
    return text


def strip_speakers(text):
    """Strip trailing or leading whitespace inside speaker element text."""
    text = re.sub(" +</speaker>", "</speaker>", text)
    text = re.sub("<speaker> +", "<speaker>", text)
    text = re.sub(" +([:.])(</speaker>)", r"\1\2", text)
    text = re.sub(r"(\w|>) {2,}(</speaker>)", r"\1 \2", text)
    return text


def add_space_around_stage_directions(text):
    """
    Add a space around *stage* elements inside a *p* in string `text`,
    so that *p* text does not appear stuck to them when rendering with the CSS.
    """
    text = re.sub(r"([^\s])<stage>", r"\1 <stage>", text)
    text = re.sub(r"</stage>([^\s.,;:?!])", r"</stage> \1", text)
    return text


def add_space_around_stage_directions_b(bts):
    """
    Add a space around *stage* elements inside a *p* in bytes `bts`,
    so that *p* text does not appear stuck to them when rendering with the CSS.
    """
    bts = re.sub(br"([^\s])<stage>", br"\1 <stage>", bts)
    bts = re.sub(br"</stage>([^\s.,;:?!])", br"</stage> \1", bts)
    return bts


def check_italics_ratio(pe):
    """
    Return ratio of italics tokens in paragraph element `pe`.
    In some plays this can indicate that it's a character stage direction.
    """
    toks = pe.xpath(".//span[@class='ocrx_word']//text()")
    toks_em = pe.xpath(".//span[@class='ocrx_word']/em/text()")
    return len(toks_em) / len(toks)


def tag_foreign_expressions_with_list(xs, lspath):
    """
    Add seg elements to the string representing xml in `xs`, based on
    list in file at path `fpath`.
    """
    with open(lspath, mode="r", encoding="utf8") as fd:
        lines = [ll.split("\t") for ll in fd]
        exp2lang = [(exp.strip(), lang.strip()) for (exp, lang) in lines]
    for e2l in exp2lang:
        exp, lang = e2l[0], e2l[1]
        # seg ran into p if no spaces around
        xs = re.sub(fr"\b{exp}\b", fr" <seg xml:lang='{lang}'>{exp}</seg> ", xs)
    #xs = re.sub(r" {2,}<seg", r" <seg", xs)
    xs = re.sub(r"( *</seg> +)([.,;:!?])", r"</seg>\2", xs)
    xs = re.sub(r"</seg> {2,}", r"</seg> ", xs)
    return xs


def create_back_with_text(xml_str, back_txt):
    """
    Create a <back> element with the text in `txt` and add it to xml string.

    First removes the text from the body and then adds the back with it.

    Parameters
    ----------
    xml_str : str
        String representing XML
    back_txt : str
        Text to create back with

    Returns
    -------
    str
        The XML string representing TEI file with the back added
    """
    xml_str = xml_str.replace(back_txt, "")
    xml_str = xml_str.replace(
        "</body>", "</body><back><div><p>" + back_txt + "</p></div></back>")
    return xml_str


def change_apos_to_squo_b(sertree):
    """
    Replace (in serialized etree) straight apostrophe with single quote.
    """
    # sertree = re.sub(br"'([srmn])", r"’\1".encode(), sertree)
    # Alsatian pronouns
    sertree = re.sub(br"(?<!=)'([srmn])", r"’\1".encode(), sertree)
    # Alsatian: sott', hab', z'undersch, z'öwersch, participles (g'fahre)
    sertree = re.sub(br"([btzg'])'", r"\1’".encode(), sertree)
    # French clitics, d', qu', c'; Alsatian d'
    sertree = re.sub(re.compile(br"([jmtsdluc])'", re.I), r"\1’".encode(), sertree)

    return sertree


def change_apos_to_squo_str(text):
    """
    Replace in a string straight apostrophe by single quote.
    """
    # Alsatian pronouns
    text = re.sub(r"(?<!=)'([srmn])", r"’\1", text)
    # Alsatian: sott', hab', z'undersch, z'öwersch, participles (g'fahre)
    text = re.sub(r"([btzg'])'", r"\1’", text)
    # French clitics, d', qu', c'; Alsatian d'
    text = re.sub(re.compile(r"([jmtsdluc])'", re.I), r"\1’", text)
    return text


def change_lsquo_to_rsquo_b(sertree):
    """
    Replace (in serialized etree) left single quote with right single quote,
    in contexts where it's likely that a rsquo should be there instead.
    """
    sertree = re.sub(r"‘([srmn])".encode(), r"’\1".encode(), sertree)
    sertree = re.sub(r"t‘ ".encode(), r"t’ ".encode(), sertree)
    return sertree


def change_lsquo_to_rsquo_str(text):
    """
    Replace in string left single quote with right single quote,
    in contexts where it's likely that a rsquo should be there instead.
    """
    text = re.sub(r"‘([srmn])", r"’\1", text)
    text = re.sub(r"t‘ ", r"t’ ", text)
    return text


def general_cleanup_str(text):
    """General cleanup of xml as a string"""
    text = re.sub(r"<lg>\s*</lg>", "", text)
    return text


def general_cleanup_b(bt):
    """General cleanup of xml as bytes"""
    bt = re.sub(b"<lg>\s*</lg>", "", bt)
    bt = re.sub(b"::", ":", bt)
    return bt


def validate_tei_with_relaxng(teifn, rng_path=ocf.tei_rng):
    os.system(f'xmllint --noout --relaxng {rng_path} {teifn}')