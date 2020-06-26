"""
To treat lines in verse in play encoding. Chrischtowe version.

Note: Treatment of these lines is expected to vary from play to play.
"""

import re
import sys

sys.path.append("../..")

import play_parsing as pp


def find_ocr_line_bbox_start_and_text(pe):
    """
    For <p> element `pe`, return (bbox start, text) tuple list for its ocr_line
    descendants.
    """
    line_eles = pe.xpath(".//span[@class='ocr_line']")
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
    contain verse).

    This is done to base verse line tagging on the bbox start value of
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
    tuple
        Two values:
            - The column number where verse starts in the page
            - The final colum for verse lines (None unless needed)
    """
    # pnbr is page number for <pb> element, not html file  number
    pnbr = int(re.sub(".html", "", fn)) - 4
    #   page numbers to skip, give a high offset
    #   (some ocr_line would be mistaken for verse otherwise)
    poem_end = 9999
    if pnbr in [11]:
        poem_offset = 324
    elif pnbr in [12]:
        poem_offset = 318
    elif pnbr in [13]:
        poem_offset = 284
    elif pnbr in [14]:
        poem_offset = 300
        poem_end = 850
    elif pnbr in [21]:
        poem_offset = 240
    elif pnbr in [22]:
        poem_offset = 304
    else:
        poem_offset = 9999
    return poem_offset, poem_end


def create_verse_elements_for_ocr_line(xlist, lineinfos, verse_offset, verse_end=None):
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
    xlist : list
        List of strings representing XML. Modified by the function.
    lineinfos : list
        List of tuples (start, text) with line bbox start and line text.
        Created by :function:`find_ocr_line_bbox_start_and_text`.
    verse_offset : int
        Minimum bbox start value to consider that the line is a verse line.

    Returns
    -------
    None
    """
    # collect lines that pass the conditions to count as verse
    verse_lines = []
    for lidx, (start, text) in enumerate(lineinfos):
        if (start >= verse_offset and len(text.strip()) > 0
                and not (xlist[-1].strip().startswith("<stage") or
                xlist[-1].strip().endswith("</stage>") or
                (xlist[-1].strip().startswith("(") and xlist[-1].strip().endswith(")")) or
                "<div>" in xlist[-1] or
                "<head>" in xlist[-1] or
                (xlist[-1].startswith("<pb n=") and xlist[-1].endswith("/>")) or
                re.search(pp.pb_reg, xlist[-1]) or
                "büschbere" in xlist[-1])):
            verse_lines.append(text)
    # iterate over collected lines adding <l> elements to each
    # (and perhaps <lg> or other around them)
    for vidx, vtext in enumerate(verse_lines):
        # keep track of indices to be able to add an element around the <l> series
        # e.g. see commented lines below if need to add an <lg>
        if vidx == 0:
            #xlist[-1] = xlist[-1].replace(vtext, f"</p><lg><l>{vtext}</l>")
            xlist[-1] = xlist[-1].replace(vtext, f"</p><l>{vtext}</l>")
        elif vidx == len(verse_lines) - 1:
            #xlist[-1] = xlist[-1].replace(vtext, f"<l>{vtext}</l></lg><p>")
            xlist[-1] = xlist[-1].replace(vtext, f"<l>{vtext}</l><p>")
        else:
            xlist[-1] = xlist[-1].replace(vtext, f"<l>{vtext}</l>")


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
    # verse lines start with uppercase after column 248 in odd pages and 330 in even
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
