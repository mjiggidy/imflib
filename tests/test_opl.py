import sys, pathlib
from imflib import opl

def main(paths:list[str]):
	"""Parse an OPL for secret testings"""

	for path_opl in paths:
		file_opl = opl.Opl.from_file(path_opl)
		print(file_opl)

if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit(f"Usage: {pathlib.Path(__file__).name} OPL_filepath.xml")
	
	main(sys.argv[1:])