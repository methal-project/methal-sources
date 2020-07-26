"""
Information to parse play hOCR source or text extracted from it, in TEI conversion.
"""

import re

# play elements
# page break, to create <pb> element
pb_reg = re.compile(r"[–—-]\s*([0-9]+)\s*[–—-]")
# text to create <sp> element
sp_reg = re.compile(r"^([^:]+:)(.+)")
# text to create <stage> element
stage_reg = re.compile(r"(\([^)]+\):?)")

# hocr attributes
x_size_reg = re.compile(r"x_size ([0-9]+)")
bbox_reg = re.compile(r"bbox ([0-9]+)")
