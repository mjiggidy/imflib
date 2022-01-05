from imflib.pkl import Pkl
import sys

if len(sys.argv) < 2:
	sys.exit("Usage: test_pkl.py path_to_pkl")

pkl = Pkl.fromFile(sys.argv[1])

print(pkl.id)

for asset in pkl.assets:
	print(f"{asset.file_name.ljust(100)}  {asset.id}")