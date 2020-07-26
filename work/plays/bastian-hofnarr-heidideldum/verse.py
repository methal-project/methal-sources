"""
To treat lines in verse in play encoding. Hofnarr Heidideldum version.

Note: Treatment of these lines is expected to vary from play to play.
"""

import re
import sys

sys.path.append("../..")

import play_parsing as pp


def find_ocr_line_bbox_start_and_text(pe):
    """
    For <p> element `pe`, return (bbox start, text) tuple list for its ocr_lin
    descendants.
    """
    line_eles = pe.xpath(".//span[@class='ocr_line' or @class='ocr_header']")
    lstart2text = []
    for le in line_eles:
        lstart = int(re.search(pp.bbox_reg, le.attrib["title"]).group(1))
        ltxt = " ".join(le.xpath(".//span[@class='ocrx_word']/text()"))
        lstart2text.append((lstart, ltxt))
    return lstart2text


def find_verse_column_for_page(fn, pes, idx):
    """
    Find start column for verse lines in a given page in a given play.

    Column can be restricted according to a range of indices for <p> elements
    in the page (`p[@class='ocr_par']` elements whose `ocr_line` descendants
    contain verse.

    This is done to based verse line tagging on the bbox start value of
    `span[@class=ocr_line]` elements in plays where the hOCR contains
    verse in them

    Note
    ----
    This is based on manual inspection of the hOCR files for each play and
    implementation is expected to change for each play.

    Parameters
    ----------
    fn : str
        Filename (used to figure out page number)
    pes : list
        List of :obj:`etree._Element` elements
    idx : int

    Returns
    -------
    int
        The column number where verse starts in the page
    """
    # pnbr is page number for <pb> element, not html file  number
    pnbr = int(re.sub(".html", "", fn)) - 3
    #   page numbers to skip, give a high offset
    #   (some ocr_line would be mistaken for verse otherwise)
    if pnbr in [15]:
        poem_offset = 9999
    #   p. 37, 39 and 41 verse lines start early,
    #   on p. 39 only last ocr_par is verse
    elif (pnbr == 37 or (pnbr == 39 and idx == len(pes) - 1) or
          pnbr == 41 and idx < 8):
        poem_offset = 169
    #   p. 36 and 66 verse earlier than in other even pages
    elif int(pnbr) % 2 > 0 or pnbr == 36 or (pnbr == 66 and idx >= len(pes) - 4):
        poem_offset = 248
    else:
        poem_offset = 330
    return poem_offset


def create_verse_elements_for_ocr_line(lineinfos, verse_offset, xlist):
    """
    Adds `<l>` tags around relevant lines in last element of `xlist`.

    To tag verse lines, based on the position on their first column
    and on content cues, in hOCR output where verse lines are in
    `span[@class='ocr_line']`.

    Note
    ----
        Implementation may change from play to play.

    Parameters
    ----------
    lineinfos : list
        List of tuples (start, text) with line bbox start and line text.
        Created by :function:`find_ocr_line_bbox_start_and_text`.
    verse_offset : int
        Minimum bbox start value to consider that the line is a verse line.
    xlist : list
        List of strings representing XML. Modified by the function.

    Returns
    -------
    None
    """
    for start, text in lineinfos:
        if (start >= verse_offset and len(text.strip()) > 0
                and not (xlist[-1].strip().startswith("<stage") or
                xlist[-1].strip().endswith("</stage>") or
                (xlist[-1].strip().startswith("(") and xlist[-1].strip().endswith(")")) or
                "<div>" in xlist[-1] or
                "<head>" in xlist[-1] or
                (xlist[-1].startswith("<pb n=") and xlist[-1].endswith("/>")) or
                re.search(pp.pb_reg, xlist[-1]) or
                "büschbere" in xlist[-1])):
            xlist[-1] = xlist[-1].replace(text, f"<l>{text}</l>")


def create_verse_elements_for_ocr_par(pes, working_idx, pnbr, xlist):
    """
    Adds `<l>` tags around relevant lines in last element of `xlist`.

    To tag verse lines, based on the position on their first word
    and on content cues, in hOCR output where verse lines are in a
    `p[@class='ocr_par']` element each

    Note
    ----
        Implementation may change from play to play.
        Unused in *Hofnarr H*, last used (similar implementation) in
        *Poetisch Oscar*

    Parameters
    ----------
    pes : list
        List of :obj:`etree._Element` elements
    working_idx : int
        Index for paragraph element to work with within `pes`
    pnbr : int
        Page number, used to define expected start column for verse lines
    xlist :
        List of strings representing XML. Modified by the function.

    Returns
    -------
    None
    """
    ll = ["<lg>"]
    mype = pes[working_idx]
    mype_spans = mype.xpath(".//span[@class='ocrx_word']")
    mype_txt = " ".join(mype.xpath(".//span[@class='ocrx_word']//text()"))
    # poetry lines start after column 200 and start with uppercase
    #   (this is play-specific)
    offset = 248 if pnbr % 2 > 0 else 330
    while int(mype_spans[0].attrib["title"].split()[1]) > offset and mype_txt[0].isupper():
        ll.append(f"""<l>{mype_txt}</l>""")
        working_idx += 1
        mype = pes[working_idx]
        mype_spans = mype.xpath(".//span[@class='ocrx_word']")
        mype_txt = " ".join(mype.xpath(".//span[@class='ocrx_word']//text()"))
    ll.append("</lg>")
    xlist[-1] = xlist[-1].replace("</p></sp>", "".join(("\n".join(ll), "</p></sp>")))
    return working_idx