from imflib import cpl, pkl
import pathlib, typing, dataclasses

@dataclasses.dataclass
class Imf:
	"""An IMF package"""

	cpl:cpl.Cpl
	pkl:pkl.Pkl

	@classmethod
	def fromPath(cls, path_imf:typing.Union[str,pathlib.Path]) -> "Imf":
		"""Parse an existing IMF"""
		
		if not isinstance(path_imf, pathlib.Path):
			path_imf = pathlib.Path(path_imf)
		if not path_imf.is_dir():
			raise NotADirectoryError(f"Path does not exist or is not a directory: {path_imf}")
		
		glob_temp = list(path_imf.glob("CPL*.xml"))
		if len(glob_temp) != 1:
			raise FileNotFoundError("Could not find a CPL in this directory")

		input_cpl = cpl.Cpl.fromFile(str(glob_temp[0]))

		glob_temp = list(path_imf.glob("PKL*.xml"))
		if len(glob_temp) != 1:
			raise FileNotFoundError("Could not find a PKL in this directory")

		input_pkl = pkl.Pkl.fromFile(str(glob_temp[0]))
		
		return cls(input_cpl, input_pkl)