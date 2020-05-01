"""Configuration for Hoflieferant encoding"""

import os

# io
hocr_dir = "sources/hOCR_html"
datadir = "data"
oufn_prefix = "hoflieferant"
oufn = "{}.xml".format(oufn_prefix)
oufn_with_characters = "{}_with_characters.xml".format(oufn_prefix)
oufn_dracor = "{}_with_characters_dracor.xml".format(oufn_prefix)

# header md
header = "filedesc.txt"

# front
cast_list_data = os.path.join(datadir, "cast_list_data.tsv.ods")
speaker_to_id_infos = os.path.join(datadir, "speaker2id.tsv")
set_data = os.path.join(datadir, "set_data.txt")

# body
correction_file = "corrections.txt"
stage_direction_corrections = "stage_direction_corrections.txt"
last_pb_nbr = 108

# validation
dracor_schema = "dracor_schema.rng"
