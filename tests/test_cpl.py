from imflib import cpl
from posttools import timecode
import sys, pathlib

if len(sys.argv) < 2:
	sys.exit("Usage: test_cpl.py path_to_imf [path_to_imf ...]")

for path_imf in sys.argv[1:]:
	for path_cpl in pathlib.Path(path_imf).glob("CPL_*.xml"):
		imf_cpl = cpl.Cpl.from_file(path_cpl)
		print(f"{path_cpl}")
		print(f"CPL Name: {imf_cpl.title}")
		if imf_cpl.annotation: print(imf_cpl.annotation)
		print(f"Timecode: {imf_cpl.timecode_range}")

		reslist = list(imf_cpl.resources)
		print(f"Contains {len(list(reslist))} resources in {len(list(imf_cpl.sequences))} sequences across {len(list(imf_cpl.segments))} segment(s):")
		print(f"  {len([res for res in reslist if isinstance(res,cpl.ImageResource)])} videos, {len([res for res in reslist if isinstance(res, cpl.AudioResource)])} audio")
		
		for idx_seg, seg in enumerate(imf_cpl.segments):
			print(f"    SEGMENT {idx_seg+1}:")
			
			for idx_seq, seq in enumerate(seg.sequences):
				print(f"    | SEQUENCE {idx_seq+1} ({type(seq).__name__}):    {seq.timecode_range}")

				for idx_res, res in enumerate(seq.resources):
					print(f"    |- RESOURCE {str(idx_res+1).rjust(3)} ({type(res).__name__}):    {res.timecode_range}    {res.edit_range}  {'x' + str(res.repeat_count) if res.repeat_count else ''}")

		print("---")