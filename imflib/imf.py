from imflib import cpl, opl, pkl, assetmap
import pathlib, typing, dataclasses


@dataclasses.dataclass
class Imf:
	"""An IMF package"""

	asset_map:assetmap.AssetMap
	cpl:cpl.Cpl
	pkl:pkl.Pkl
	opl:typing.Optional[opl.Opl] = None

	@classmethod
	def from_path(cls, path_imf:typing.Union[str,pathlib.Path]) -> "Imf":
		"""Parse an existing IMF"""
		
		path_imf = pathlib.Path(path_imf)
		if not path_imf.is_dir():
			raise NotADirectoryError(f"Path does not exist or is not a directory: {path_imf}")
		
		input_assetmap = assetmap.AssetMap.from_file(pathlib.Path(path_imf,"ASSETMAP.xml"))
		if len(input_assetmap.packing_lists) != 1:
			raise NotImplementedError(f"Support for {len(input_assetmap.packing_lists)} PKLs is not yet implemented")
		elif len(input_assetmap.packing_lists[0].chunks) != 1:
			raise NotImplementedError("Support for chunked PKLs is not yet implemented")
		
		input_pkl = pkl.Pkl.from_file(pathlib.Path(path_imf,input_assetmap.packing_lists[0].file_paths[0]))
		
		# TODO: Maybe go off like the PKL or ASSETMAP instead of globbin'
		glob_temp = list(path_imf.glob("CPL*.xml"))
		if not len(glob_temp):
			raise FileNotFoundError("Could not find a CPL in this directory")
		elif len(glob_temp) > 1:
			raise NotImplementedError(f"Support for {len(glob_temp)} CPLs is not yet implemented")
		input_cpl = cpl.Cpl.from_file(str(glob_temp[0]))
		
		# Marry the pkl assets to the CPL
		# BROKEN: I don't remember what I did here before.
		# TODO: Remember what I did there before.
		#for res in input_cpl.resources:
		#	res.setAsset(input_pkl.get_asset(res.file_id))

		glob_temp = list(path_imf.glob("OPL*.xml"))
		if len(glob_temp) > 1:
			raise NotImplementedError(f"Support for {len(glob_temp)} OPLs is not yet implemented")
		if glob_temp:
			input_opl = opl.Opl.from_file(glob_temp[0])
		else:
			input_opl = None
		
		return cls(input_assetmap, input_cpl, input_pkl, input_opl)