from imflib import cpl
from posttools import timecode
import sys, pathlib

if len(sys.argv) < 2:
	sys.exit("Usage: test_cpl.py path_to_imf [path_to_imf ...]")

for path_imf in sys.argv[1:]:
	for path_cpl in pathlib.Path(path_imf).glob("CPL_*.xml"):
		print(cpl.Cpl.fromFile(path_cpl))