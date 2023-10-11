# coding=utf8

"""
Encode Christowe in TEI based on hOCR output.
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
import play_parsing as pp
import utils.utils as ut
import verse

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
    lstart2text = verse.find_ocr_line_bbox_start_and_text(pe)
    poem_offset, poem_end = verse.find_verse_column_for_page(fn, pes, actual_idx)

    is_div_head = re.search(re.compile("([0-9]+)\. Ufftritt"), txt)
    has_pb = re.search(pp.pb_reg, txt)
    has_sp = re.search(pp.sp_reg, txt)

    # final line (play-specific)
    #   skip printer line
    #if "Buckdruckerei" in txt:
    #   return actual_idx + 1
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
    elif has_sp :

        create_sp(has_sp, xl, idx)
    
    # sp
    else:
        if DBG:
            print("Texte : ", txt)

        # character stage directions
        x_size = float(re.search(pp.x_size_reg, pe.xpath(
            ".//span[@class='ocr_line' or @class='ocr_header']")[0].attrib["title"]).group(1))
        if DBG:
            print(x_size)
        if x_size < 27 and ((not ":" in txt) or ("Qouic" in txt) or (txt.startswith("Jetz singe mr noch"))):
            xl.append(f"<stage type='character'>{txt}</stage>")
        # speech across page break
        else:
            attach_text_to_last_sp(txt, xl)

    # verse treatment
    verse.create_verse_elements_for_ocr_line(xl, lstart2text, poem_offset)

    if DBG:
        pnbr = int(fn.replace(".html", "")) - 3
        print("  ## {} ##".format(pnbr), txt)

    if increment:
        actual_idx += 1
    return actual_idx


def manual_cleanups(st):
    # correct cases with colon in the text (not as a speaker separator) -------
    st = st.replace("<sp><speaker>Xaverel:</speaker><p>Wann de so anfangsch, no bloss i druff.",
                    "<sp><speaker>Xaverel:</speaker><p>Wann de so anfangsch, no bloss i druff.</p></sp>")
    st = st.replace("<sp><speaker>Marikel:</speaker><p>Wann dü nitt miesli stille bisch —",
                    "<sp><speaker>Marikel:</speaker><p>Wann dü nitt miesli stille bisch —</p></sp>")
    st = st.replace("<sp><speaker>Schorschel:</speaker><p> <stage>(fladdiert)</stage> Grossbabbe, ich druckt di äu lieb — awer no muesch äu e natt’s verzehle — wäisch diss vum Katzemisel. <stage>(druckt de Grossbabbe.)</stage>",
                    "<sp><speaker>Schorschel:</speaker><p> <stage>(fladdiert)</stage> Grossbabbe, ich druckt di äu lieb — awer no muesch äu e natt’s verzehle — wäisch diss vum Katzemisel. <stage>(druckt de Grossbabbe.)</stage></p></sp>")
    st = st.replace("<sp><speaker>Do isch d’ Philome bläich worre wie e Suppedaller, sie isch in d’ Stubb nin, hett’s Commode ufgerisse un da — ihr Schatz isch nimmi do gewann, alles Gold un Silwer futsch. Do isch se bedrüebt un voll Kummer un Anleje unter de Quätschelbäum gsässe un hett gejommert:</speaker><p>",
                    "Do isch d’ Philome bläich worre wie e Suppedaller, sie isch in d’ Stubb nin, hett’s Commode ufgerisse un da — ihr Schatz isch nimmi do gewann, alles Gold un Silwer futsch. Do isch se bedrüebt un voll Kummer un Anleje unter de Quätschelbäum gsässe un hett gejommert: ")
    st = st.replace("<sp><speaker>Do hett’s widder anfange ze rüsche in de Äscht, e paar Quätschle sinn erab kejt un die Stimm hett gsäit:</speaker><p>",
                    "Do hett’s widder anfange ze rüsche in de Äscht, e paar Quätschle sinn erab kejt un die Stimm hett gsäit: ")
    st = st.replace("</p></sp>  Vor Scham un Ärjer, ass se widder e Dummhäit gemacht hett",
                    " Vor Scham un Ärjer, ass se widder e Dummhäit gemacht hett")
    st = st.replace("</p></sp>  „Dü hesch nitt ghöert uf gueti Wort, Drum isch din Gold un Richtum furt.“</p></sp>",
                    "„Dü hesch nitt ghöert uf gueti Wort, Drum isch din Gold un Richtum furt.“")
    st = st.replace("</p></sp><sp><speaker>Do hett der Vöjel e Fader keje lonn,",
                    " Do hett der Vöjel e Fader keje lonn,")
    st = st.replace("</speaker><p>„Nimm die Fäder un steck se in de Bodde,",
                    " „Nimm die Fäder un steck se in de Bodde,")
    st = st.replace("<p>Ihr liewi Kinder, ich hab gsähn ass ihr alli brav sinn, un de brave Kinder duet’s Chrischtkindel allewill helfe un biestehn. Denn durch diss ass ihr zuem Chrischtkindel immer gebett hänn,</p></sp>",
                    "<p>Ihr liewi Kinder, ich hab gsähn ass ihr alli brav sinn, un de brave Kinder duet’s Chrischtkindel allewill helfe un biestehn. Denn durch diss ass ihr zuem Chrischtkindel immer gebett hänn, ")
    st = st.replace("<sp><speaker>hett’s ejch de Babbe widder gebrocht un Glüeck un Säje wurd vun jetz an in ejerem Hiesel herrsche, bliewe allewil brav un folgsam, un ’s Chrischtkindel wurd ejch nie verlonn. Jetz singe mr noch:</speaker><p>„Stille Nacht, heilige Nacht.“</p></sp>",
                    " hett’s ejch de Babbe widder gebrocht un Glüeck un Säje wurd vun jetz an in ejerem Hiesel herrsche, bliewe allewil brav un folgsam, un ’s Chrischtkindel wurd ejch nie verlonn. Jetz singe mr noch: „Stille Nacht, heilige Nacht.“</p></sp>")
    # missing stage directions ------------------------------------------------
    st = st.replace("(Alli lueje gespannt uf Düer, erin kummt ’s Chrischtkindel mit-eme Dannebaum un dr Hanstrapp.",
                    "<stage>(Alli lueje gespannt uf Düer, erin kummt ’s Chrischtkindel mit-eme Dannebaum un dr Hanstrapp.)</stage>")
    st = st.replace("<speaker>Alli singe:</speaker>",
                    "<speaker>Alli</speaker><stage>(singe:)</stage>")
    # manually created paragraphs, inside Grossbabbe's narration --------------
    #   around verse, verse.create_verse_elements_for_ocr_line already adds <p> and </p>
    #   otherwise need to create them manually
    #   0
    st = re.sub(r"Uf-em Grab vum Katzemiesel",
                r"</p><p>\g<0>", st)
    #  around verse
    st = re.sub(r"un wie e Stimm säit\s*:",
                r"\g<0>", st)
    #   1
    st = re.sub(r"Do isch d’ Philome bläich worre",
                r"\g<0>", st)
    st = re.sub(r"i vor Hunger stärwe.“ ",
                r"\g<0></p>", st)
    #   2
    st = re.sub(r"Do hett’s widder anfange",
                r"<p>\g<0>", st)
    st = re.sub(r"ganz gewöehnlichi Quätschle gsinn\.",
                r"\g<0></p>", st)
    #  3
    st = re.sub(r"Vor Scham un Ärjer",
                r"<p>\g<0>", st)
    # around verse
    st = re.sub(r"dar hett no gsunge\s*:",
                r"\g<0>", st)
    #  4
    # around verse
    st = re.sub(r"„O dü liewer Vöjel“",
                r"\g<0>", st)
    st = re.sub(r"gizich ware.“",
                r"\g<0></p>", st)
    #  5
    st = re.sub(r"Do hett der Vöjel e Fader",
                r"<p>\g<0>", st)
    st = re.sub(r"im Glück d’ Arme nitt.“",
                r"\g<0></p>", st)
    #  6
    st = re.sub(r"Do drüwer hett d’ Philome",
                r"<p>\g<0>", st)
    st = re.sub(r"Pelzkapp drüss.",
                r"\g<0>", st)

    #  7 (around the page break) 
    st = re.sub(r"(<pb n=.13./>)", r"</p> \1 <p>", st)

    # highlight title for final poem
    st = re.sub(r"<p>\s*(<stage>\(saat uf :\)</stage>)\s*(’s Chrischtkindel\.)\s*</p>",
                r"\1<p><span type='head' rend='bold'>\2</span></p>", st)

    # remove extra p around pb
    st = re.sub(r"<p>\s*(<pb n=.22./>)\s*</p>", r"\1", st)

    # note: doesn't work here but in the bytes version at end
    st = st.replace("<p/>", "")

    # general correction when adding verse (needed in Hofnarr H)
    st = re.sub("</p></sp>\s*<l>", "<l>", st)
    st = re.sub("</p></sp> +([^<])", r"\1", st)
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
    #print(hdr_str)
    # all
    global xml_str
    xml_str = "\n".join(
        ['<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">', hdr_str.decode(),
         "<text><body><div type='act'>", body_text, "</div></body></text></TEI>"])
    # create back element
    xml_str = ut.create_back_with_text(xml_str, cf.back_text)
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
    if cf.format_initial_xml:
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
