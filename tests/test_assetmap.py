from imflib import assetmap
import sys, pathlib

if not len(sys.argv) > 1:
	sys.exit("Usage: text_assetmap.py path_to_imf [path_to_imf ...]")

for path_imf in sys.argv[1:]:
	path_assetmap = pathlib.Path(path_imf,"ASSETMAP.xml")

	am = assetmap.AssetMap.fromFile(path_assetmap)

	asset_pkl = am.packing_lists

	if not asset_pkl:
		print("No packing list found")
	else:
		for pkl in asset_pkl:
			print("Total size:",am.total_size)
			print(pkl.file_paths)