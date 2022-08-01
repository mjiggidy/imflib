from imflib import cpl
import sys, pathlib

if len(sys.argv) < 2:
	sys.exit("Usage: test_cpl.py path_to_cpl [path_to_cpl ...]")

for path_cpl in sys.argv[1:]:
	print("\n---\n")
	print(f"{path_cpl}")
	
	try:
		imf_cpl = cpl.Cpl.from_file(path_cpl)
	except Exception as e:
		print(f"Skipping: {e}")
		continue
	
	print(f"CPL Name: {imf_cpl.title}")
	print(f"Issued {imf_cpl.issue_date} by {imf_cpl.issuer} using {imf_cpl.creator}")
	print(f"Has edit rate: {imf_cpl.edit_rate}")
	if imf_cpl.annotation: print(f"Has annotation: {imf_cpl.annotation}")
	if imf_cpl.tc_start: print(f"Has start timecode: {imf_cpl.tc_start}")
	if imf_cpl.total_runtime: print(f"Has total runtime: {imf_cpl.total_runtime}")
	if imf_cpl.content_originator: print(f"Contains {imf_cpl.content_kind or ''} content from {imf_cpl.content_originator}")
	if imf_cpl.content_versions:
		print(f"Has content versions:")
		for version in imf_cpl.content_versions:
			print(f"\t{version}")
	if imf_cpl.locales:
		print(f"Has locales:")
		for locale in imf_cpl.locales:
			print(f"\t{locale}")
	if imf_cpl.extension_properties:
		print("Has extensions:")
		for ext in imf_cpl.extension_properties:
			print(f"\t{ext}")
	if imf_cpl.essence_descriptors:
		print("Has essence descriptors:")
		for ess in imf_cpl.essence_descriptors:
			print(f"\t{ess}")
	
	

	continue

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