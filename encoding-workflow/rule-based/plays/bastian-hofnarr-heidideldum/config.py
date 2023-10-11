#coding=utf8

"""Configuration for Hofnarr Heidideldum encoding"""

import os

# play id
play_id = 200

# io
hocr_dir = "sources/hocr"
datadir = "data"
outdir = "out"
oufn_prefix = "hofnarr_heidideldum"
oufn = os.path.join(outdir, "{}.xml".format(oufn_prefix))
oufn_with_characters = os.path.join(outdir, "{}_with_characters.xml".format(oufn_prefix))
oufn_dracor = os.path.join(outdir, "{}_with_characters_dracor.xml".format(oufn_prefix))

# header md
header = "filedesc.txt"
add_encoding_desc = True
encoding_desc_fpath = os.path.join(datadir, "encodingdesc.xml")
numistral_prefix = "https://www.numistral.fr/ark:/12148/"

# front

cast_list_data = os.path.join(datadir, "cast_list_data.ods")
speaker_to_id_infos = os.path.join(datadir, "speaker2id.tsv")
#summary_fpath = os.path.join(hocr_dir, "009.html")
#summary_title = "1. Bild"
# set according to whether a period follows the role description in dramatis personae
add_period_to_role = False
add_period_to_roledesc = False
character_description_pnbr = None


# body
has_acts = True
body_start_filename = 10 # not the page number but file number
body_end_filename = 69 # not the page number but file number
correction_file = "corrections.txt"
stage_direction_corrections = "stage_direction_corrections.txt"
#   min ratio of italics to consider paragraph a character stage dir
min_italics_ratio_char_st = 0.8
foreign_expressions = os.path.join(datadir, "foreign_text.txt")

# validation
dracor_schema = "dracor_schema.rng"

# other options

add_css = True
format_initial_xml = True
validate_rng = True
indent = True