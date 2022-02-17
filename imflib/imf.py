from imflib import cpl, pkl, assetmap
import pathlib, typing, dataclasses


@dataclasses.dataclass
class Imf:
	"""An IMF package"""

	asset_map:assetmap.AssetMap
	cpl:cpl.Cpl
	pkl:pkl.Pkl

	@classmethod
	def fromPath(cls, path_imf:typing.Union[str,pathlib.Path]) -> "Imf":
		"""Parse an existing IMF"""
		
		if not isinstance(path_imf, pathlib.Path):
			path_imf = pathlib.Path(path_imf)
		if not path_imf.is_dir():
			raise NotADirectoryError(f"Path does not exist or is not a directory: {path_imf}")
		
		input_assetmap = assetmap.AssetMap.fromFile(pathlib.Path(path_imf,"ASSETMAP.xml"))
		if len(input_assetmap.packing_lists) != 1:
			raise NotImplementedError(f"Support for {len(input_assetmap.packing_lists)} PKLs is not yet implemented")
		elif len(input_assetmap.packing_lists[0].chunks) != 1:
			raise NotImplementedError("Support for chunked PKLs is not yet implemented")
		
		input_pkl = pkl.Pkl.fromFile(pathlib.Path(path_imf,input_assetmap.packing_lists[0].file_paths[0]))
		
		glob_temp = list(path_imf.glob("CPL*.xml"))
		if len(glob_temp) != 1:
			raise FileNotFoundError("Could not find a CPL in this directory")

		input_cpl = cpl.Cpl.fromFile(str(glob_temp[0]))


		# Marry the pkl assets to the CPL
		for res in input_cpl.resources:
			res.setAsset(input_pkl.getAsset(res.file_id))
		
		return cls(input_assetmap, input_cpl, input_pkl)