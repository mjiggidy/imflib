from imflib.pkl import Pkl
import sys, pathlib

if len(sys.argv) < 2:
	sys.exit("Usage: test_pkl.py path_to_imf [path_to_imf ...]")


for path_imf in sys.argv[1:]:

	path_pkls = list(pathlib.Path(path_imf).glob("PKL_*"))
	print(f"{path_imf} has {len(path_pkls)} PKL(s):")
	for path_pkl in path_pkls:
		pkl = Pkl.fromFile(path_pkl)
		print(f"{path_pkl.name}:")
		print(f"Created on {pkl.issue_date} by {pkl.issuer} using {pkl.creator}")
		print(f"Annotations: {pkl.annotation_text}")
		print(f"Contains {len(pkl.assets)} asset(s) totalling {pkl.total_size/1000/1000/1000:.2f} GB")
		print("---")