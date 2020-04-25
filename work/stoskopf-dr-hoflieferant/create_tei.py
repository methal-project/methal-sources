#coding=utf8

"""Create initial version of Hofilieferant TEI based on hOCR sources"""

from lxml import etree
import os
import re
from copy import deepcopy

import config as cf

DBG = False

# main processing -------------------------------------------------------------

parser = etree.HTMLParser()

txt = []

for fn in sorted(os.listdir(cf.hocr_dir)):
    if DBG:
        print(fn)
    # odd and even pages have text starting on a different column
    fn_nbr = int(fn.replace(".html", ""))
    if fn_nbr % 2 > 0:
        min_start = 65
    else:
        min_start = 225
    # only frontmatter before page 15
    if fn_nbr < 15:
        continue
    # page number
    pnbr = -1
    ffn = os.path.join(cf.hocr_dir, fn)
    tree = etree.parse(ffn)
    pars = tree.xpath("//p[@class='ocr_par']")
    for par in pars:
        sp = False
        # get paragraph text ------------------------------
        par_text_l = []

        # get spans *text*, initial version without keeping span style
        # for x in par.xpath(".//span[@class='ocrx_word']"):
        #     if x.text is not None:
        #         par_text_l.append(x.text)
        #     else:
        #         par_text_l.append(x.xpath("./em/text()|./strong/text()")[0])
        # par_text = " ".join(par_text_l)

        # get spans *text* and keep position of spans in italic
        ita_toks = []
        for idx, x in enumerate(par.xpath(".//span[@class='ocrx_word']")):
            if x.text is not None:
                par_text_l.append(x.text)
            else:
                par_text_l.append(x.xpath("./em/text()|./strong/text()")[0])
                ita_toks.append(idx)
        # italic ranges
        par_text = " ".join(par_text_l)
        # #TODO try this https://stackoverflow.com/a/2361991
        ranges = []
        last_idx = 0
        for tidx, tok in enumerate(ita_toks):
            try:
                if tidx == len(ita_toks) - 1:
                    ranges.append((ita_toks[last_idx], ita_toks[tidx]))
                    last_idx = tidx+1
                elif ita_toks[tidx+1] != tok+1:
                    ranges.append((ita_toks[last_idx], ita_toks[tidx]))
                    last_idx = tidx+1
            except IndexError:
                pass
        # tag italic ranges
        par_text_l_copy = deepcopy(par_text_l)
        for rg in ranges:
            par_text_l[rg[0]] = '<emph rend="italic">{}'.format(par_text_l[rg[0]])
            par_text_l[rg[1]] = '{}</emph>'.format(par_text_l[rg[1]])
        par_text_bkp = par_text
        par_text = " ".join(par_text_l)

        # get line and span *elements* ----------------------
        par_lines = par.xpath(".//span[@class='ocr_line']")
        spans = [x for x in par.xpath(".//span[@class='ocrx_word']")]
        # acts --------------------------------------------
        act_reg = re.compile(r"((I+)\.?\s+Aufzug\.)", re.DOTALL)
        has_act = re.search(act_reg, par_text)
        if has_act:
            prev_div = "" if len(has_act.group(2)) < 2 else "</div>"
            txt.append('{}<div type="act"><head>{}</head>'.format(
                prev_div, has_act.group(1)))
            continue
        # page number -------------------------------------
        pb_reg = re.compile(r"[–—-]\s*([0-9]+)\s*[–—-]")
        has_nbr = re.search(pb_reg, " ".join(par_text_l))
        if has_nbr:
            pnbr = has_nbr.group(1)
            txt.append("<pb n='{}'/>".format(int(pnbr)))
            continue
        # stage directions at act start --------------------
        x_size_reg = re.compile(r"x_size ([0-9]+)")
        has_x_size = re.search(x_size_reg, par_lines[0].attrib["title"])
        assert has_x_size
        x_size_first_line = int(has_x_size.group(1))
        if x_size_first_line <= 36:
            txt.extend(["<stage><p>", par_text, "</p></stage>"])
            continue
        # check for speaker -------------------------------
        try:
            w1s = int(spans[0].attrib["title"].split()[1])
            w2s = int(spans[1].attrib["title"].split()[1])
            #TODO this test not very good, no comparison with second LINE but word
            # len <=-3 cos words like 'de' or 'Dr.' very short and test fails
            if (w1s <= min_start < w2s) or (w1s <= min_start and len(par_text_l[0]) <= 3):
                sp = True
        except IndexError:
            continue
        #   paragraph starts with speaker
        if sp:
            # speaker takes one token
            if par_text_l[0][-1] == ":":
                txt.append("<sp><speaker>{}</speaker><p>".format(par_text_l[0]))
                idx = 0
            # speaker takes > 1 token, accumulate
            else:
                speaker_text = ["<sp><speaker>{}".format(par_text_l[0])]
                idx = 1
                while idx < len(par_text_l) and par_text_l[idx][-1] != ":":
                    speaker_text.append(par_text_l[idx])
                    idx += 1
                try:
                    speaker_text.append(par_text_l[idx])
                except IndexError:
                    pass
                speaker_text.append("</speaker><p>")
                txt.append(" ".join(speaker_text))
            txt.append(" ".join([lt for lt in par_text_l[idx + 1:]]))
            txt.append("</p></sp>")
        # paragraph at page start (does not start with speaker)
        else:
            exc_pages = (33, 59, 63, 64, 69, 71, 77, 78, 86, 89, 105, 108)
            if int(pnbr) in exc_pages and "Aufzug" not in par_text:
                pass
                txt[-1] = txt[-1].replace("</p></sp>", "")
                txt[-2] = txt[-2].replace("</p></sp>", "")
                txt.append(par_text)
                txt.append("</p></sp>")
            # end of act
            elif int(pnbr) in (46, 78):
                txt.append("<stage>{}</stage>".format(par_text))
            else:
                if DBG:
                    print("## {} ##\n  {}\n".format(pnbr, par_text))
    if int(pnbr) == cf.last_pb_nbr:
        txt.append("<stage>Schluss.</stage>")
        txt.append("</div>")

# correct errors created by procedure above -----------------------------------

#  general pb around page break
corr_pb = "(?:24|28|44|50|68|74|92)"
corr_reg = re.compile(
    r"""(</p>\s*</sp>)\s*(<pb n=['"]{}["']/>)\s*<sp>\s*<speaker>(.+?)</speaker><p>\s*(</p>\s*</sp>)""".format(corr_pb))

old_txt = txt
txt = re.sub(corr_reg, r" \2 \3\1", "\n".join(txt))
txt = re.sub("<p>\n", "<p>", txt)
txt = re.sub("\n</p>", "</p>", txt)

#  page 50
txt = re.sub(r"""</p>\s*</sp>\s*(<pb n=['"]50['"]/>)\s*<sp>\s*<speaker>""", r" Halt! Ich will eins anprowiere. (zieht eins wohl-\1", txt)
txt = re.sub(r"""</speaker>\s*<p>(Grinsinger, officier d'académie\. Frau)""", r" \1 ", txt)

# three speakers on p. 40
txt = re.sub(r"""(Ei, Ihr <emph rend=["']italic["']>cousin</emph> üs Leipzig.\s*</p></sp>)""",
             r"""\1{}""".format("".join(["<sp><speaker>Lisa, Jeannette, Durand:</speaker>",
                                         """<p>D'r <emph rend="italic">cousin</emph> üs Leipzig ? !</p></sp>"""])), txt)

# mixed content on p. 34
txt = txt.replace("au nit for de-n-", "au nit for de-n-Auguste.")

# add stage directions --------------------------------------------------------

txt_before_stg = txt
stg_reg = re.compile(r"(\([^)<]+\))\s*(:?)", re.DOTALL)
txt = re.sub(stg_reg, r" <stage>\1\2</stage> ", txt)

txt = txt.replace("<stage>(von links die Scene mit ansehend: </speaker>",
                  "<stage>(von links die Scene mit ansehend):</stage> </speaker>")

# stage direction inside speaker goes outside speaker
stg_sp_reg = re.compile("""(<speaker>[^<]*)(<stage>[^<]+</stage>)([^<]*</speaker>)""",
                        re.DOTALL)

txt_before_stg_sp = txt
txt = re.sub(stg_sp_reg, r"\1 \3 \2", txt)

# modifications to stage directions after adding emph tokens
stg2 = re.compile("""(\([^<()]*?<emph rend="italic">[^<()]+</emph>.*?\))""")
txt = re.sub(stg2, r"<stage>\1</stage>", txt)

txt = re.sub("""(<emph rend="italic">)([^<]+)(</speaker><p>)""",
             r"""\1\2</emph>\3""", txt)

txt = re.sub(r"""(<emph rend="italic">)([^<]+)(</stage>)""",
             r"""\1\2</emph>\3<emph rend="italic">""", txt)

txt = re.sub(r"""(<p>)([^<]+)(</emph>)""", r"""\1<emph rend="italic">\2\3""", txt)

#  clean blanks
txt = re.sub(" *</speaker>", "</speaker>", txt)

# manual corrections to stage directions
stg_corrs = [(ll.strip().split("\t")[0], ll.strip().split("\t")[1])
         for ll in open(os.path.join(cf.datadir, cf.stage_direction_corrections),
         mode="r", encoding="utf8") if not ll.startswith("#")]

for scorr in stg_corrs:
    txt = txt.replace(scorr[0], scorr[1])

# corrections to speakers -----------------------------------------------------
sp_reg = re.compile(
    """<speaker>([^\n]*)<stage>([^\n]*<emph rend="italic">[^>]+>)([^<]*)</stage>([^\n—]*)</speaker>""")
sp_rep = r"""<speaker>\1</speaker> <stage>\2\3\4</stage>"""
txt = re.sub(sp_reg, sp_rep, txt)

# italic within speaker
sp_reg_2 = re.compile(
    """<speaker>([^\n]*)([^\n]*<emph rend="italic">[^>]+>)\s*<stage>([^<]*)</stage>([^\n—]*)</speaker>""")
sp_rep_2 = r"""<speaker>\1\2</speaker> <stage>\3\4</stage>"""
txt = re.sub(sp_reg_2, sp_rep_2, txt)

# empty paragraph after and speech within speaker
sp_reg_3 = re.compile(
    r"""<speaker>([^\n]*)<stage>([^\n]*<emph rend="italic">[^>]+>)([^<]*)</stage>([^\n]*)</speaker>""")
sp_rep_3 = r"""<speaker>\1</speaker> <stage>\2\3</stage><p>\4</p>"""
txt = re.sub(sp_reg_3, sp_rep_3, txt)

# speakers that end with semicolon
semicolon_reg = r"""<speaker>([^;]+);(.+?)</speaker>"""
semicolon_rep = r"<speaker>\1</speaker><p>\2</p>"
txt = re.sub(semicolon_reg, semicolon_rep, txt)

# specific manual corrections -------------------------------------------------
txt = txt.replace("<p/></sp>", "</p></sp>")
txt = txt.replace("wenn’s heisst:</speaker>", "wenn’s heisst:")
txt = txt.replace("wenn’s heisst:<p>", "wenn’s heisst:")

txt = txt.replace("zu treffen?<p></p></sp>", "zu treffen?</p></sp>")
#  p. 84 (svrl stage directions and emph within speaker)
txt = re.sub(r"<speaker>Fritz Grinsinger\s*<stage>\(winkt",
             "<speaker>Fritz Grinsinger</speaker>  <p><stage>(winkt", txt)
txt = re.sub(r"<stage>\(sinkt auf den Stuhl.\)</stage></speaker>",
             "<stage>(sinkt auf den Stuhl.)</stage></p>", txt)
# p. 20
st_p_20 = r"""(<speaker>Madame Grinsinger)\s*<stage>(.+?)</speaker>"""
rep_p_20 = r"""\1</speaker> <p><stage>\2</p>"""
txt = re.sub(st_p_20, rep_p_20, txt)

# p. 86
st_p_86 = re.compile(r"(<stage>\(Alles stimmt lebhaft mit ein. \(Tusch.\))</stage>( Fritz.+)</p>")
rep_p_86 = r"</p>\1\2</stage>"
txt = re.sub(st_p_86, rep_p_86, txt)

#   from replacement list in a file -----------------------
txt_bf_corrs = txt
corrs = [(ll.strip().split("\t")[0], ll.strip().split("\t")[1])
         for ll in open(os.path.join(cf.datadir, cf.correction_file),
         mode="r", encoding="utf8") if not ll.startswith("#")]
for corr in corrs:
    txt = txt.replace(corr[0], corr[1])


# problems after adding emph -----------------------------------------------
#   pb, p. 40
pb40_reg = re.compile(r"""</p>\s*</sp>\s*(<pb n=["']40["']/>)\s*<sp>\s*<speaker>([^\n]+)</speaker>""", re.DOTALL)
pb40_rep = r" \1 \2</p>"
txt = re.sub(pb40_reg, pb40_rep, txt)
#   pb, p. 88 (stage direction across page break)
pb88_reg = re.compile(
    r"""(\([^<]+)</p>\s*</sp>\s*(<pb n=['"]88["']/>)\s*<sp>\s*<speaker>([^<]+)</speaker>\s*""")
pb88_rep = r"</p> <stage>\1 \2 \3</stage>"
txt = re.sub(pb88_reg, pb88_rep, txt)

#   other problems after adding emph
#   p. 79
p79_reg = re.compile(r"""(<speaker>de Rose:)(... <emph.+derniers\.</emph>)</speaker>""")
p79_rep = r"\1</speaker><p>\2</p>"
txt = re.sub(p79_reg, p79_rep, txt)

#   p. 83
p83_reg = re.compile(r"""(<speaker>Marie) (\(schnell.+?</emph>)([^<]+)</speaker>""")
p83_rep = r"\1</speaker> <stage>\2</stage> <p>\3</p>"
txt = re.sub(p83_reg, p83_rep, txt)

#   p. 50
txt = txt.replace(":<emph", ": <emph")

# hyphenation ----------------------------------------------------------------

txt = re.sub(re.compile(r"(\w)- (\w)"), r"\1\2", txt)
txt = txt.replace("Lichtund Luftbad", "Licht- und Luftbad")

# strip space within elements

txt = re.sub(r"(\w|>) {2,}(</(?:stage|p|speaker)>)", r"\1 \2", txt)
txt = re.sub(r"(<(?:stage|p|speaker)>) {2,}", r"\1 ", txt)
txt = txt.replace(" </speaker>", "</speaker>")
txt = txt.replace("<speaker> ", "<speaker>")
txt = re.sub(" +([:.])(</speaker>)", r"\1\2", txt)
txt = re.sub(r" {2,}<stage>", " <stage>", txt)
txt = re.sub(r"</stage> {2,}", " </stage> ", txt)

# remove space before punctuation
txt = re.sub(r"(>) +([,.;:])", r"\1\2", txt)

# get punctuation out of emph if it's the last character
emph_depunct = r"(\w)([,.;:?!)——]+)(</emph>)"
txt = re.sub(emph_depunct, r"\1\3\2", txt)
txt = txt.replace('<emph rend="italic">(', '(<emph rend="italic">')

# remove empty emph tag
txt = txt.replace("""<emph rend="italic"/>""", "")

# add tei header --------------------------------------------------------------
hdpath = os.path.join(cf.datadir, cf.header)
with open(hdpath, mode="r", encoding="utf8") as fh:
    hdtext = fh.read()

txt = "\n".join(["<TEI><teiHeader>", hdtext, "</teiHeader><text><body>", txt, "</body></text></TEI>"])


# write out -------------------------------------------------------------------

# txt -----------------------------------------------------
ofn = cf.oufn
with open("{}.txt".format(ofn), encoding="utf8", mode="w") as of:
    of.write(txt)

# xml -----------------------------------------------------
# xtree = etree.fromstring("".join(("<body>", "".join(txt), "</body>")))
# xtree = etree.fromstring("".join(("<body>", "".join([txt]), "</body>")))
# ser = etree.tostring(xtree, xml_declaration=True, pretty_print=True, encoding="UTF-8")

xml_str = txt
parser_x = etree.XMLParser(remove_blank_text=True)
elem = etree.XML(xml_str, parser=parser_x)
ser = etree.tostring(elem, xml_declaration=True, pretty_print=True, encoding="UTF-8")
ser = ser.replace(b"<p/>", b"")

with open("{}".format(ofn), mode="wb") as of:
    of.write(ser)
os.system("xmllint --noblanks {} > bli ; xmllint --format bli > bla ; mv bla {} ; rm bli".format(
    ofn, ofn))

# add pi at end
os.system(
    """sed -i.bak -e 's%<TEI>%<TEI xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0">%g' {}""".format(ofn))
