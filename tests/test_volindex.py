import sys, pathlib
from imflib import assetmap

def get_volindex(path_volindex:str) -> int:
	"""Get the volume index from VOLINDEX.xml"""

	volindex = assetmap.VolumeIndex.from_file(path_volindex)
	return volindex.index

if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit(f"Usage: {pathlib.Path(__file__)} path/to/VOLINDEX.xml [another/path/to/VOLINDEX.xml ...]")

	for path_volindex in sys.argv[1:]:
		try:
			print(f"Volume index for {pathlib.Path(path_volindex).parent} is {get_volindex(path_volindex)}")
		except Exception as e:
			print(f"{path_volindex}: {e}")