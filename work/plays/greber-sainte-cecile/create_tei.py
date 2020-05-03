# coding=utf8

"""
Encode Sainte-Cecile in TEI based on hOCR output.
"""

from importlib import reload
from lxml import etree
import os
import re
import sys

sys.path.append("../..")

import add_characters as ac
import config as cf
import oconfig as ocf
import utils.utils as ut

DBG = True

# constants
pb_reg = re.compile(r"[–—-]\s*([0-9]+)\s*[–—-]")
sp_reg = re.compile(r"^([^:]+:)(.+)")
stage_rg = re.compile(r"(\([^)]+\):?)")
x_size_reg = re.compile(r"x_size ([0-9]+)")


def get_par_text(pe):
    """Extract text from par element `pe`"""
    toks = pe.xpath(".//span[@class='ocrx_word']//text()")
    return " ".join(toks)


def create_pb(ma, xl):
    xl.append(("<pb n='{}'/>".format(int(ma.group(1)))))


def create_sp(ma, xl, idx):
    """
    Create sp element, tagging stage directions.
    `ma` is a match object with the speaker string as group 1 and the
    p text as group 2. `idx` is the paragraph index in its page.
    """
    speaker = f"<speaker>{ma.group(1).strip()}</speaker>"
    ptext = f"<p>{ma.group(2).strip()}</p>"
    speaker_has_stage = re.search(stage_rg, speaker)
    clean_speaker = speaker
    if speaker_has_stage:
        clean_speaker = re.sub(stage_rg, "", speaker)
        clean_speaker = clean_speaker.strip().replace(
            "</speaker>",
            f"</speaker><stage>{speaker_has_stage.group(1)}</stage>")
    clean_p = re.sub(stage_rg, r"<stage>\1</stage>", ptext).strip()
    xl.append(f"<sp>{clean_speaker}{clean_p}</sp>")


def check_italics_ratio(pe):
    """
    Return ratio of italics tokens in paragraph element `pe`.
    In this play this can indicate that it's a character stage direction.
    """
    toks = pe.xpath(".//span[@class='ocrx_word']//text()")
    toks_em = pe.xpath(".//span[@class='ocrx_word']/em/text()")
    return len(toks_em) / len(toks)


def tag_poetry_lines(par_eles, working_idx, xml_list):
    """Tags poetry lines that appear centered on the page"""
    ll = ["<lg>"]
    mype = par_eles[working_idx]
    mype_spans = mype.xpath(".//span[@class='ocrx_word']")
    mype_txt = " ".join(mype.xpath(".//span[@class='ocrx_word']//text()"))
    # poetry lines start after column 200 and start with uppercase
    while int(mype_spans[0].attrib["title"].split()[1]) > 200 and mype_txt[0].isupper():
        ll.append(f"""<l>{mype_txt}</l>""")
        working_idx += 1
        mype = par_eles[working_idx]
        mype_spans = mype.xpath(".//span[@class='ocrx_word']")
        mype_txt = " ".join(mype.xpath(".//span[@class='ocrx_word']//text()"))
    ll.append("</lg>")
    xml_list[-1] = xml_list[-1].replace("</p></sp>", "".join(("\n".join(ll), "</p></sp>")))
    return working_idx


def attach_text_to_last_sp(text, xml_list):
    """
    Attach to the last sp/p paragraph text that don't start with a speaker.
    The last sp/p index depends on whether a pb element intervenes or not.
    """
    if "<pb n" in xml_list[-1]:
        clean_text = re.sub(stage_rg, r"<stage>\1</stage>", text)
        xml_list[-2] = xml_list[-2].replace("</p></sp>", "")
        xml_list[-2] = " ".join((xml_list[-2], xml_list[-1], f" {clean_text}</p></sp>"))
        xml_list.pop()
    else:
        xml_list[-1] = xml_list[-1].replace("</p></sp>", "")
        clean_text = re.sub(stage_rg, r" <stage>\1</stage> ", text)
        xml_list[-1] = " ".join((xml_list[-1], f" {clean_text}</p></sp>"))


def process_paragraph(pe, pes, xl, idx, actual_idx, fn):
    """
    Trigger a processing for each type of paragraph depending on cues in it.
    """
    increment = True
    txt = get_par_text(pes[actual_idx])
    is_div_head = re.search(re.compile("([0-9]+)\. Scene"), txt)
    has_pb = re.search(pb_reg, txt)
    has_sp = re.search(sp_reg, txt)


    # final line
    #   skip printer line
    if "Buckdruckerei" in txt:
       return actual_idx + 1
    if re.match(r"ende\.", txt.strip().lower()):
        xl.append(f"<stage>{txt}</stage></div>")

    # scene start
    elif is_div_head:
        if int(is_div_head.group(1)) > 1:
            xl.append(f"</div><div type='scene'><head>{txt}</head>")
        else:
            xl.append(f"<div type='scene'><head>{txt}</head>")

    # page breaks
    elif has_pb:
        create_pb(has_pb, xl)

    # sp
    elif has_sp and not (has_sp.string.startswith("Fanfare") or
                has_sp.string.startswith("neglischiert") or
                has_sp.string.startswith("fünfhundert") or
                has_sp.string.startswith("isch au besser do")):
        create_sp(has_sp, xl, idx)
    else:
        # character stage directions
        x_size = float(re.search(x_size_reg, pe.xpath(".//span[@class='ocr_line']")[0].attrib["title"]).group(1))
        if x_size < 25 and not ":" in txt:
            xl.append(f"<stage type='character'>{txt}</stage>")
        # speech across page break
        else:
            attach_text_to_last_sp(txt, xl)
        if DBG:
            pnbr = int(fn.replace(".html", "")) - 5
            print("  ## {} ##".format(pnbr), txt)

    if increment:
        actual_idx += 1
    return actual_idx


def manual_cleanups(st):
    st = st.replace("Karcher (schmales Männchen von ungefähr 45 Jahren, ganz in schwarz gekleidet, Gehrock, Filzhut ; spricht trocken und etwas zaghaft ; macht überhaupt einen schüchternen Eindruck:</speaker>",
                    "Karcher</speaker> <stage>(schmales Männchen von ungefähr 45 Jahren, ganz in schwarz gekleidet, Gehrock, Filzhut ; spricht trocken und etwas zaghaft ; macht überhaupt einen schüchternen Eindruck:</stage> ")
    st = st.replace("</p>Cécile  <stage>(zärtlich)</stage>  Barthelmeh !!",
                    "<sp><speaker>Cécile</speaker> <stage>(zärtlich)</stage> <p>Barthelmeh !!</p></sp>")
    st = re.sub(r"""(uff e Sainte-Cécile.)\s*(Sophie:)(</p>\s*</sp>)(\s*<sp>\s*)(<speaker>Enishänsel):""",
                r"\1\3\4\5, \2", st)
    return st


def create_xml(xml_list):
    # body
    body_text = "".join(xml_list)
    body_text = ut.simple_dehyphenation(body_text)
    body_text = ut.strip_speakers(body_text)
    # body_text = ut.tag_foreign_expressions_with_list(body_text, cf.foreign_expressions)
    body_text = ut.add_space_around_stage_directions(body_text)
    body_text = ut.change_apos_to_squo_str(body_text)
    body_text = ut.change_lsquo_to_rsquo_str(body_text)
    body_text = ut.general_cleanup_str(body_text)
    body_text = manual_cleanups(body_text)
    # teiHeader
    #   workbook also contains header info (and characters)
    md_all = ut.read_header_info(cf.cast_list_data)
    md = ut.get_play_metadata_by_id(md_all, cf.play_id)
    hdr = ut.create_tei_header(md, other={"respStmt": ocf.respStmt,
                                          "availability": ocf.availability["ccby"]})
    hdr_str = etree.tostring(hdr)
    # all
    global xml_str
    xml_str = "\n".join(
        ["<TEI>", hdr_str.decode(), "<text><body>", body_text, "</body></text></TEI>"])
    parser_x = etree.XMLParser(remove_blank_text=True)
    elem = etree.XML(xml_str, parser=parser_x)
    ser = etree.tostring(elem, xml_declaration=True, pretty_print=True, encoding="UTF-8")
    ser = ut.change_apos_to_squo_b(ser)
    return ser


def write_out(otree):
    with open("{}".format(cf.oufn), mode="wb") as of:
        of.write(otree)
    # os.system("xmllint --noblanks {} > bli ; xmllint --format bli > bla ; mv bla {} ; rm bli".format(
    os.system("xmllint {} > bli ; xmllint --format bli > bla ; mv bla {} ; rm bli".format(
        cf.oufn, cf.oufn))
    os.system(
        """sed -i.bak -e 's%<TEI>%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(
            cf.oufn))
    os.system(
        """sed -i.bak -e 's%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%<?xml-stylesheet type="text/css" href="../../../css/tei-drama.css"?>\\n<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(
            cf.oufn))
    os.system(f"xmllint --noout {cf.oufn}")


if __name__ == "__main__":
    for mdl in cf, ocf, ut, ac:
        reload(mdl)
    # list to keep strings that represent xml
    xl = []
    for fn in sorted(os.listdir(cf.hocr_dir)):
        if not fn.endswith("html"):
            continue
        if (int(fn.replace(".html", "")) < cf.body_start_filename or
                int(fn.replace(".html", "")) > cf.body_end_filename):
            continue
        ffn = os.path.join(cf.hocr_dir, fn)
        print(fn)
        tree = etree.parse(ffn)
        pars = tree.xpath("//p[@class='ocr_par']")
        todo_idx = 0
        # iterate over paragraphs and process each
        try:
            for idx, par in enumerate(pars):
                todo_idx = process_paragraph(par, pars, xl, idx, todo_idx, fn)
        except IndexError:
            # last paragraph
            continue
    # create xml object and serialize
    ser_xml = create_xml(xl)
    write_out(ser_xml)
    if True:
        # create file with characters
        ac.add_characters(cf.cast_list_data, cf.oufn, cf.oufn_with_characters)
        txt = open(cf.oufn_with_characters).read()
        if not "tei-drama.css" in txt:
            os.system(
                """sed -i.bak -e 's%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%<?xml-stylesheet type="text/css" href="../../../css/tei-drama.css"?>\\n<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(
                    cf.oufn_with_characters))
        ut.validate_tei_with_relaxng(cf.oufn_with_characters, rng_path=ocf.tei_rng)
        # os.system(f"xmllint --format {cf.oufn_with_characters} > .t ; mv .t {cf.oufn_with_characters}")
        # os.system(f"xmlindent {cf.oufn_with_characters} -i 2 -l 120 > .t ; mv .t {cf.oufn_with_characters}")
        os.system(f"tidy --indent auto -wrap 114 -xml {cf.oufn_with_characters} | "
                  rf"perl -p -e 's/<\/seg>(\w)/<\/seg> \1/g' | "
                  rf"perl -p -e 's/(\w)<stage>/\1 <stage>/g' | "
                  rf"perl -p -e 's/<\/stage>([\w’„])/<\/stage> \1/g' | "
                  rf"perl -p -e 's/utf-8/UTF-8/g' > .t ; "
                  f"mv .t {cf.oufn_with_characters}")
