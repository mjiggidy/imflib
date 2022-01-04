from imflib import cpl, pkl
from posttools import timecode
import sys, pathlib

if len(sys.argv) < 2:
	sys.exit(f"Usage: {pathlib.Path(__file__).name} imf_folder_path")

path_imf = pathlib.Path(sys.argv[1])

if not path_imf.is_dir():
	sys.exit(f"{path_imf} is not a valid directory")

glob_temp = list(path_imf.glob("CPL*.xml"))
if len(glob_temp) != 1:
	sys.exit(f"{len(glob_temp)} CPLs found")

input_cpl = cpl.Cpl.fromFile(str(glob_temp[0]))

glob_temp = list(path_imf.glob("PKL*.xml"))
if len(glob_temp) != 1:
	sys.exit(f"{len(glob_temp)} PKLs found")

input_pkl = pkl.Pkl.fromFile(str(glob_temp[0]))

print(input_pkl.assets)


tc_current = timecode.Timecode(0, input_cpl.edit_rate)

for segment in input_cpl.segments:
	for sequence in segment.sequences:
		if isinstance(sequence, cpl.MainImageSequence):
			for resource in sequence.resources:
				asset = input_pkl.getAsset(resource.file_id)
				if asset:
					print(f"{tc_current}\t{tc_current + resource.duration}\t{asset.file_name}")
				tc_current += resource.duration