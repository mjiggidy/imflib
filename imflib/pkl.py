import xml.etree.ElementTree as et
import pathlib, sys, dataclasses, typing

@dataclasses.dataclass
class Asset:
	"""An asset packed into this IMF package"""
	name:str
	size:int
	type:str
	urn:str

class Pkl:
	"""An IMF PKL Packing List"""

	ns = {"pkl":"http://www.smpte-ra.org/schemas/2067-2/2016/PKL"}
	
	def __init__(self):
		self._assets = list()

	@classmethod
	def fromFile(cls, path:str) -> "Pkl":
		"""Parse an existing PKL"""

		pkl = cls()

		file_pkl = et.parse(path)
		root = file_pkl.getroot()

		assetlist = root.find("pkl:AssetList",cls.ns)

		for asset in assetlist:
			name = asset.find("pkl:OriginalFileName",cls.ns).text
			size = int(asset.find("pkl:Size",cls.ns).text)
			type = asset.find("pkl:Type",cls.ns).text
			urn = asset.find("pkl:Id",cls.ns).text
			pkl.addAsset(Asset(name, size, type, urn))
		
		return pkl
	
	def addAsset(self, asset:"Asset"):
		"""Add an asset this package"""
		self._assets.append(asset)
	
	@property
	def assets(self) -> typing.List[Asset]:
		return list(self._assets)
