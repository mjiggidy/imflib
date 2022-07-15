from imflib import assetmap
import sys, pathlib

if not len(sys.argv) > 1:
	sys.exit("Usage: text_assetmap.py path_to_imf [path_to_imf ...]")

for path_imf in sys.argv[1:]:
	path_assetmap = pathlib.Path(path_imf,"ASSETMAP.xml")

	am = assetmap.AssetMap.from_file(path_assetmap)

	asset_pkl = am.packing_lists

	if not asset_pkl:
		print("No packing list found")
	else:
		for pkl in asset_pkl:
			print(f"{path_imf.split('/')[-1]}")
			print(f"Created on {am.issue_date} by {am.issuer} using {am.creator}.")
			print(f"Contains {len(am.packing_lists)} packing list(s) and {len(am.assets)-len(am.packing_lists)} assets totalling {am.total_size/1024/1024/1024:.02f} GB:")
			for asset in am.assets:
				print(f"  {asset.id}  {', '.join(asset.file_paths)} ({len(asset.chunks)} chunks)")
		print("---")