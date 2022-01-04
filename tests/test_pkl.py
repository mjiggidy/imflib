from imflib.pkl import Pkl
import sys

pkl = Pkl.fromFile(sys.argv[1])

for asset in pkl.assets:
	print(f"{asset.name.ljust(100)}  {asset.urn}")