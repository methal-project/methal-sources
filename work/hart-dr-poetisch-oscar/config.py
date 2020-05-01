#coding=utf8

"""Configuration for Hoflieferant encoding"""

import os

# play id
play_id = 6

# io
hocr_dir = "sources/hocr_html"
datadir = "data"
outdir = "out"
oufn_prefix = "oscar"
oufn = os.path.join(outdir, "{}.xml".format(oufn_prefix))
oufn_with_characters = os.path.join(outdir, "{}_with_characters.xml".format(oufn_prefix))
oufn_dracor = os.path.join(outdir, "{}_with_characters_dracor.xml".format(oufn_prefix))

# header md
header = "filedesc.txt"

# front
cast_list_data = os.path.join(datadir, "cast_list_data.ods")
speaker_to_id_infos = os.path.join(datadir, "speaker2id.tsv")
summary_fpath = os.path.join(hocr_dir, "00000007.html")
summary_title = "Inhaltsangabe."

# body
body_start_page = 8
correction_file = "corrections.txt"
stage_direction_corrections = "stage_direction_corrections.txt"
#   min ratio of italics to consider paragraph a character stage dir
min_italics_ratio_char_st = 0.8
foreign_expressions = os.path.join(datadir, "foreign_text.txt")

# validation
dracor_schema = "dracor_schema.rng"
