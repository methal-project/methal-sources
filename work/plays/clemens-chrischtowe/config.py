#coding=utf8

"""Configuration for Christowe encoding"""

import os

# play id
play_id = 201

# io
hocr_dir = "sources/hocr"
datadir = "data"
outdir = "out"
oufn_prefix = "chrischtowe"
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
add_character_age = False
speaker_to_id_infos = os.path.join(datadir, "speaker2id.tsv")
summary_fpath = os.path.join(hocr_dir, "07.html")
#   in Clemens plays there's often a second spot with character and set info
second_set_info_fpath = os.path.join(hocr_dir, "08.html")
#   word index to add to 'second set'
start_second_set = -30

summary_title = "Scènerie:"
character_description_pnbr = 4
# set according to whether a period follows the role description in dramatis personae
add_period_to_role = True
add_period_to_roledesc = True
long_set_language = "gsw"

# body
body_start_filename = 9 # not the page number but file number
body_end_filename = 27 # not the page number but file number
correction_file = "corrections.txt"
stage_direction_corrections = "stage_direction_corrections.txt"
#   min ratio of italics to consider paragraph a character stage dir
min_italics_ratio_char_st = 0.8
foreign_expressions = os.path.join(datadir, "foreign_text.txt")

# back
back_text = "Diss Wihnachtsgedicht „’s Chrischtkindel“ isch vum Strossburjer Dichter Stöber"

# validation
dracor_schema = "dracor_schema.rng"

# other options

format_initial_xml = True
add_css = True
validate_rng = True
indent = True

