#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:55:22 2020

@author: ruizfabo
"""

import re
from string import punctuation


def correct_stage_directions(txt):
    """
    Final corrections to stage directions.
    
    Note:
        To be called after other functions affecting stage-directions.
    """
    txt = re.sub('\(Er klopft an die<pb n="73"/>\s*Türe\)',
                 r"<stage>\0</stage> ", txt)
    txt = re.sub('e-n-Irrtum beruht!</stage></p></sp>',
                 'e-n-Irrtum beruht!</p></sp>', txt)
    txt = re.sub(r"""</stage></p></sp> „Sincères félicitations.“ — Mini Dochter isch(\s*)üwrigens au so guet wie verlobt.</stage>""",
                 r"</stage> „Sincères félicitations.“ — Mini Dochter isch\1üwrigens au so guet wie verlobt.</p></sp>",
                 txt)
    txt = re.sub(r"""Schweiss von der Stirne.\)</stage></p></sp>\s*„Que j’ai(\s*)chaud!“</stage>""",
                 r"""Schweiss von der Stirne.)</stage> „Que j’ai\1chaud!“</p></sp>""", txt)
    txt = re.sub(r"(</stage>)</p></sp>([^<]+)</stage>", r"\1\2</p></sp>", txt)
    return txt


def correct_serialized_xml(stree):
    """
    Corrections to the final serialized XML before writing to file.
    """
    #  speakers
    stree = stree.replace(b"Alle:1", b"Alle:")
    stree = stree.replace(b"Alle:2", b"Alle:")
    stree = re.sub(b"<p>und (?!wenn)", b"<p>", stree)
    #    cast
    stree = re.sub(b"(<castItem corresp=.)(.+?)(.>)",
                     br"\1#\2\3", stree)
    #  stage directions
    stree = re.sub(b"<stage>", b" <stage>", stree)
    stree = re.sub(b"</stage>", b"</stage> ", stree)
    stree = re.sub(b"> <", b"><", stree)
    stree = re.sub(b"</stage> {2,}", b"</stage> ", stree)
    stree = re.sub("(\w|[{}—]) {{2,}}<stage>".format(punctuation).encode(),
                     br"\1 <stage>", stree)
    stree = re.sub(b"<stage>Madame Ropfer <stage>",
                     b"<speaker>Madame Ropfer</speaker> <stage>",
                     stree)
    stree = re.sub(b"mit de Kleider umzugehn!</stage>",
                     b"mit de Kleider umzugehn!", stree)
    stree = re.sub("</stage> ([{}])".format(punctuation).encode(),
                     br"</stage>\1", stree)
    stree = re.sub(re.compile(
                     b"(<speaker>Madame Ropfer</speaker>)(\s*<stage>[^<]+</stage>)(\s*Awer Antoine! E\s*so mit de Kleider umzugehn!)"),
                     r"""<sp who="#emilie">\n{}\1\n{}\2<p>\3</p></sp>""".format(" "*10, " "*10).encode(),
                     stree)   
    #  punctuation
    stree = re.sub(b"(\w)\.\.\.", br"\1 ...", stree)
    stree = re.sub(b'\."', ".“".encode(), stree)
    stree = re.sub("„Oh“ oui, maman, ce sera charmant!“".encode(),
                   "„Oh oui, maman, ce sera charmant!“".encode(),
                   stree)
    stree = re.sub(b"Maul-und Klauen", b"Maul- und Klauen", stree)
    stree = re.sub("‚,Mon Dieu!“".encode(), "„Mon Dieu!“".encode(), stree)
    #  replace n-dash with m-dash
    stree = re.sub("—".encode(), "—".encode(), stree)
    stree = re.sub("(\S)―(\S)".encode(), r"\1 ― \2".encode(), stree)
    stree = re.sub(b" -<", " ―<".encode(), stree)
    stree = re.sub(b" - ", " ― ".encode(), stree)
    #  quotation marks
    stree = re.sub("(> ?)„ ".encode(), r"\1„".encode(), stree)
    stree = re.sub("“ \. ".encode(), "“. ".encode(), stree)
    #  spaces around page-breaks
    stree = re.sub(br'(\S)(<pb n="[0-9]+"/>)(\S)',
                     br"\1 \2 \3", stree)
    stree = re.sub(br'(\S)(<pb n="[0-9]+"/>)(\n)',
                      br"\1 \2\3", stree)
    #   exception: when there's a hyphen separating both parts of word
    stree = re.sub(b'- (<pb n="[0-9]+"/>)\s+', br"\1", stree)

    # final stage directions exceptions
    stree = re.sub(b'<p><stage>\(in grosser Aufregung durch die Mitte\):</stage> ',
                   b'<stage>(in grosser Aufregung durch die Mitte):</stage><p> ',
                   stree)
    stree = re.sub('(\(Er klopft an die <pb n="73"/>[\n ]*Türe.\))'.encode(),
                   br"<stage>\1</stage>", stree)
    stree = re.sub(b'(\(Gibt[\n ]+Anatol die Hand.\))',
                   br"<stage>\1</stage>", stree)
    stree = re.sub(b'(\(Auf[\n ]+Jules deutend\))',
                   br"<stage>\1</stage>", stree)
    stree = re.sub(br'(\(Will den Koffer\s*ergreifen.\))',
                   br"<stage>\1</stage>", stree)
    stree = re.sub('(\(st[^s]+sst[\n ]+hastig in den M[^r]+rser\))'.encode(),
                   br"<stage>\1</stage>", stree)
    stree = re.sub(b'<stage><stage>\(weinerlich\)</stage>:</stage>',
                   b'<stage>(weinerlich):</stage>', stree)
    stree = re.sub(re.compile(b'(Ropfer durch die Mitte ab\. .+?ganz verdutzt an\.\))', re.DOTALL),
                   br"<stage>(\1</stage>", stree)
    stree = re.sub(b"""(\(Er nimmt den Gehrock, der auf dem Stuhl <pb n="68"/>\s*liegt und mustert ihn.\))""",
                   br"<stage>\1</stage>", stree)
    
    # final exceptions
    stree = re.sub("dit hättsch s’ Schosephin".encode(),
                   "dü hättsch s’ Schosephin".encode(), stree)
    stree = re.sub(br"(\(Umarmt[\n ]+Marie)",
                   br"<stage>\1)</stage>", stree)
    stree = re.sub(br"so\s*passel", br"so passe!", stree)

    # remove extra spaces inside headings
    stree = re.sub(br"\s+(</(?:head)>)", br"\1", stree)
    stree = re.sub(br"(<(?:head)>)\s+", br"\1", stree)
    
    stree = re.sub("LiLPa ― Université de Strasbourg".encode(),
                     "LiLPa - Université de Strasbourg".encode(),
                     stree)
    return stree


