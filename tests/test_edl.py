"""Extremely poorly written test to get a changes-only EDL out of an IMF for purposes unknown"""

from typing import TextIO
from imflib import cpl, pkl
from posttools import timecode
import sys, pathlib

edl_padding_reel = 48
edl_padding_event = 3

def formatEvent(event:cpl.Resource, asset:pkl.Asset, event_number:int, tc_start_timeline: timecode.Timecode, stream=TextIO):
	"""Print a formatted event"""
	print(f"{str(event_number).zfill(edl_padding_event)}  {pathlib.Path(asset.file_name).stem.ljust(edl_padding_reel)}  V  C  {event.in_point} {event.out_point} {tc_start_timeline} {tc_start_timeline + event.duration}", file=stream)
	print(event)
	print(asset.file_name, event.in_point, event.out_point)

def edlFromImf(path_imf:pathlib.Path):
	
	glob_temp = list(path_imf.glob("CPL*.xml"))
	if len(glob_temp) != 1:
		sys.exit(f"{len(glob_temp)} CPLs found")

	input_cpl = cpl.Cpl.fromFile(str(glob_temp[0]))

	glob_temp = list(path_imf.glob("PKL*.xml"))
	if len(glob_temp) != 1:
		sys.exit(f"{len(glob_temp)} PKLs found")

	input_pkl = pkl.Pkl.fromFile(str(glob_temp[0]))

	cpl_title = input_cpl.title
	tc_current = input_cpl.tc_start

	edl_count_event = 1

	edl_outpath = pathlib.Path(path_imf).with_suffix(".edl")

	with edl_outpath.open('w') as edl_stream:
		print(f"TITLE: {cpl_title}", file=edl_stream)
		print(f"FCM: {'DROP FRAME' if input_cpl.tc_start.mode == timecode.Timecode.Mode.DF else 'NON-DROP FRAME'}", file=edl_stream)

		for segment in input_cpl.segments:
			for sequence in segment.sequences:
				if isinstance(sequence, cpl.MainImageSequence):
					for resource in sequence.resources:
						asset = input_pkl.getAsset(resource.file_id)
						if asset:
							formatEvent(resource, asset, edl_count_event, tc_current, edl_stream)
						tc_current += resource.duration
						edl_count_event += 1

	print(f"Changes-only EDL written to {edl_outpath}")

if len(sys.argv) < 2:
	sys.exit(f"Usage: {pathlib.Path(__file__).name} imf_folder_path")

for path in sys.argv[1:]:
	path_imf = pathlib.Path(path)
	if not path_imf.is_dir():
		sys.exit(f"{path_imf} is not a valid directory")
	edlFromImf(path_imf)