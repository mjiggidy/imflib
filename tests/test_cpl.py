from imflib.cpl import Cpl, MainImageSequence
from posttools import timecode
import sys

if len(sys.argv) < 2:
	sys.exit("Usage: test_cpl.py path_to_cpl")

cpl = Cpl.fromFile(sys.argv[1])

resources = list()

for segment in cpl.segments:
	for sequence in segment.sequences:
		if isinstance(sequence, MainImageSequence):
			for resource in sequence.resources:
				resources.append(resource)

tc_running = timecode.Timecode(0, cpl.edit_rate)

for res in resources:
	print(tc_running, res.file_id)
	tc_running += res.duration