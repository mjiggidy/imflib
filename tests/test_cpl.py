from imflib import cpl
from posttools import timecode
import sys, pathlib

if len(sys.argv) < 2:
	sys.exit("Usage: test_cpl.py path_to_imf [path_to_imf ...]")

for path_imf in sys.argv[1:]:
	for path_cpl in pathlib.Path(path_imf).glob("CPL_*.xml"):
		imf_cpl = cpl.Cpl.fromFile(path_cpl)
		print(f"{path_cpl}")
		print(f"CPL Name: {imf_cpl.title}")
		if imf_cpl.annotation: print(imf_cpl.annotation)
		print(f"Start Timecode: {imf_cpl.tc_start}")

		reslist = list(imf_cpl.resources)
		print(f"Contains {len(list(reslist))} resources in {len(list(imf_cpl.sequences))} sequences across {len(list(imf_cpl.segments))} segment(s):")
		print(f"  {len([res for res in reslist if isinstance(res,cpl.ImageResource)])} videos, {len([res for res in reslist if isinstance(res, cpl.AudioResource)])} audio")

		print("---")