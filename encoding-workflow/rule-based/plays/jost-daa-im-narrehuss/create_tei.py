# coding=utf8

"""
Encode E Daa im Narrehüs in TEI based on hOCR output.
"""

from importlib import reload
from lxml import etree
import os
import re
import roman
import sys

sys.path.append("../..")

import add_characters as ac
import config as cf
import oconfig as ocf
import play_parsing as pp
import utils.utils as ut
#import verse

DBG = False


def get_par_text(pe):
    """Extract text from par element `pe`"""
    toks = pe.xpath(".//span[@class='ocrx_word']//text()")
    return " ".join(toks)


def create_pb(ma, xl):
    xl.append(("<pb n='{}'/>".format(int(ma.group(1)))))


def create_sp(ma, xl, pidx=None):
    """
    Create sp element, tagging stage directions.
    `ma` is a match object with the speaker string as group 1 and the
    p text as group 2. `pidx` is the paragraph index in its page.
    """
    speaker = f"<speaker>{ma.group(1).strip()}</speaker>"
    ptext = f"<p>{ma.group(2).strip()}</p>"
    speaker_has_stage = re.search(pp.stage_reg, speaker)
    clean_speaker = speaker
    if speaker_has_stage:
        clean_speaker = re.sub(pp.stage_reg, "", speaker)
        clean_speaker = clean_speaker.strip().replace(
            "</speaker>",
            f"</speaker><stage>{speaker_has_stage.group(1)}</stage>")
    clean_p = re.sub(pp.stage_reg, r"<stage>\1</stage>", ptext).strip()
    xl.append(f"<sp>{clean_speaker}{clean_p}</sp>")


def attach_text_to_last_sp(text, xml_list):
    """
    Attach to the last sp/p paragraph text that don't start with a speaker.
    The last sp/p index depends on whether a pb element intervenes or not.
    """
    if "<pb n" in xml_list[-1]:
        clean_text = re.sub(pp.stage_reg, r"<stage>\1</stage>", text)
        xml_list[-2] = xml_list[-2].replace("</p></sp>", "")
        xml_list[-2] = " ".join((xml_list[-2], xml_list[-1], f" {clean_text}</p></sp>"))
        xml_list.pop()
    else:
        xml_list[-1] = xml_list[-1].replace("</p></sp>", "")
        clean_text = re.sub(pp.stage_reg, r" <stage>\1</stage> ", text)
        xml_list[-1] = " ".join((xml_list[-1], f" {clean_text}</p></sp>"))


def process_paragraph(pe, pes, xl, idx, actual_idx, fn):
    """
    Trigger a processing for each type of paragraph depending on cues in it.

    Note
    ----
    Mixes play-specific and generic processing.

    Parameters
    ----------
    pe : :obj:`lxml._Element`
        Paragraph to start processing at
    pes : list
        List of :obj:`lxml._Element` for each `<p>` on file `fn`
    xl : list
        List of strings representing XML. The result of processing the `<p>`
        element is appended to it.
    idx : int
        Index of the `<p>` in its page (based on xpath that retrieves them)
    actual_idx : int
        Processing starts at index `idx` but may cover several paragraphs,
        updating the value of `actual_idx`, which is returned so that further
        processing picks up there.
    fn : str
        Filename, used to determine page number

    Returns
    -------
    int
        Index of next paragraph that needs to be processed
    """
    increment = True
    txt = get_par_text(pes[actual_idx])

    # for verse line treatment
    #lstart2text = verse.find_ocr_line_bbox_start_and_text(pe)
    #poem_offset, poem_end = verse.find_verse_column_for_page(fn, pes, actual_idx)

    is_div_scene_head = re.search(re.compile("([0-9]+)\. Scène\."), txt)
    is_div_act_head = re.search(re.compile("([IVX]+)\. AKT\."), txt)
    has_pb = re.search(pp.pb_reg, txt)
    has_sp = re.search(pp.sp_reg, txt)

    # final line (play-specific)
    #   skip printer line
    #if "Buckdruckerei" in txt:
    #   return actual_idx + 1
    if re.match(r"ende\.", txt.strip().lower()):
        xl.append(f"<stage>{txt}</stage></div>")

    # act start
    elif is_div_act_head:
        if int(roman.fromRoman(is_div_act_head.group(1))) > 1:
            # close act and also scene
            xl.append(f"</div></div><div type='act'><head>{txt}</head>")
        else:
            xl.append(f"<div type='act'><head>{txt}</head>")
    
    # scene start
    elif is_div_scene_head:
        if int(is_div_scene_head.group(1)) > 1:
            xl.append(f"</div><div type='scene'><head>{txt}</head>")
        else:
            xl.append(f"<div type='scene'><head>{txt}</head>")

    # page breaks
    elif has_pb:
        create_pb(has_pb, xl)
    
    # sp
    elif has_sp:

        create_sp(has_sp, xl, idx)
    
    # sp
    else:
        if DBG:
            print("Texte : ", txt)

        # character stage directions
        x_size = float(re.search(pp.x_size_reg, pe.xpath(".//span[@class='ocr_line']")[0].attrib["title"]).group(1))
        if DBG:
            print(x_size)
        if x_size < 27 and ((not ":" in txt) or ("Qouic" in txt) or (txt.startswith("Jetz singe mr noch"))):
            xl.append(f"<stage>{txt}</stage>")
        # speech across page break
        else:
            attach_text_to_last_sp(txt, xl)

    # verse treatment
    #verse.create_verse_elements_for_ocr_line(xl, lstart2text, poem_offset)

    if DBG:
        pnbr = int(fn.replace(".html", "")) - 3
        print("  ## {} ##".format(pnbr), txt)

    if increment:
        actual_idx += 1
    return actual_idx


def manual_cleanups(st):
    # around pb[@n="8"]
    st = re.sub(r"</p>\s*</sp>\s*(<pb n=.8.\s*/>)\s*<sp>\s*<speaker>", r" \1 ", st)
    st = re.sub(r"</speaker>\s*<p>\s*(«\sSage mir)", r" \1", st)
    # around pb[@n="15"]
    st = re.sub(r"</p>\s*</sp>\s*(<pb n=.15.\s*/>)\s*<sp>\s*<speaker>([^<]+)</speaker>",
                r" \1 \2", st)
    st = re.sub(r"<p>\s*(Mon Dieu.\s*Au noch die S)", r" \1", st)
    # added pr 2020-10-23
    st = st.replace("d’ Cabine", "d’Cabine")
    st = st.replace("<stage>(trätt wietig vor lütt):</stage>",
                    "<stage>(trätt wietig vor ; lütt):</stage>")
    st = st.replace("ich nitt here ! .", "ich nitt here !")
    return st


def create_xml(xml_list):
    # breakpoint()
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
    #print(hdr_str)
    # all
    global xml_str
    xml_str = "\n".join(
        ['<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">', hdr_str.decode(), "<text><body><div>", body_text, "</div></body></text></TEI>"])
    if cf.has_acts:
        xml_str = xml_str.replace("<body><div>", "<body>")
        xml_str = xml_str.replace("</body>", "</div></body>")
    # create back element
    #xml_str = ut.create_back_with_text(xml_str, cf.back_text)
    parser_x = etree.XMLParser(remove_blank_text=True)
    if DBG:
        print(xml_str)
    elem = etree.XML(xml_str, parser=parser_x)
    ser = etree.tostring(elem, xml_declaration=True, pretty_print=True, encoding="UTF-8")
    ser = ut.change_apos_to_squo_b(ser)
    # remove empty <p>
    ser = re.sub(b"<p/>", b"", ser)
    return ser


def write_out(otree):
    with open("{}".format(cf.oufn), mode="wb") as of:
        of.write(otree)
    #if cf.format_initial_xml:
        # os.system("xmllint --noblanks {} > bli ; xmllint --format bli > bla ; mv bla {} ; rm bli".format(
        #os.system("xmllint {} > bli ; xmllint --format bli > bla ; mv bla {} ; rm bli".format(
        #    cf.oufn, cf.oufn))
        #os.system(
        #    """sed -i.bak -e 's%<TEI>%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(
        #        cf.oufn))
        #os.system(
        #    """sed -i.bak -e 's%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%<?xml-stylesheet type="text/css" href="../../../css/tei-drama.css"?>\\n<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(
        #        cf.oufn))
        #os.system(f"xmllint --noout {cf.oufn}")


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
                # more than one p may be processed in one process_paragraph call
                # which is why todo_idx is returned: the next call picks up there
                todo_idx = process_paragraph(par, pars, xl, idx, todo_idx, fn)
        except IndexError:
            # last paragraph
            continue
    # create xml object and serialize
    ser_xml = create_xml(xl)
    write_out(ser_xml)
    # create file with characters
    ac.add_characters(cf.cast_list_data, cf.oufn, cf.oufn_with_characters)
    # validation
    if cf.add_css:
        txt = open(cf.oufn_with_characters).read()
        if not "tei-drama.css" in txt:
            os.system(
                """sed -i.bak -e 's%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%<?xml-stylesheet type="text/css" href="../../../css/tei-drama.css"?>\\n<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(
                    cf.oufn_with_characters))
    if cf.validate_rng:
        ut.validate_tei_with_relaxng(cf.oufn_with_characters, rng_path=ocf.tei_rng)
    if cf.indent:
        # os.system(f"xmllint --format {cf.oufn_with_characters} > .t ; mv .t {cf.oufn_with_characters}")
        # os.system(f"xmlindent {cf.oufn_with_characters} -i 2 -l 120 > .t ; mv .t {cf.oufn_with_characters}")
        os.system(f"tidy --indent auto -wrap 114 -xml {cf.oufn_with_characters} 2> /dev/null | "
                  rf"perl -p -e 's/<\/seg>(\w)/<\/seg> \1/g' | "
                  rf"perl -p -e 's/(\w)<stage>/\1 <stage>/g' | "
                  # use \p{L} to catch accented characters
                  rf"perl -p -e 's/<\/stage>([\p{{L}}’„])/<\/stage> \1/g' | "
                  rf"perl -p -e 's/utf-8/UTF-8/g' > .t ; "
                  f"mv .t {cf.oufn_with_characters}")