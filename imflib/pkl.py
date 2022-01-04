import xml.etree.ElementTree as et
import dataclasses, typing, re

pat_nsextract = re.compile(r'^\{(.+)\}')

@dataclasses.dataclass
class Asset:
	"""An asset packed into this IMF package"""
	id:str
	file_name:str
	size:int
	type:str

	@classmethod
	def fromXml(cls, asset:et.Element, ns:dict) -> "Asset":
		"""Create an asset from an XML element"""
		id = asset.find("pkl:Id", ns).text
		file_name = asset.find("pkl:OriginalFileName", ns).text
		size = int(asset.find("pkl:Size", ns).text)
		type = asset.find("pkl:Type", ns).text
		
		return cls(id, file_name, size, type)


class Pkl:
	"""An IMF PKL Packing List"""

	
	def __init__(self, id:typing.Optional[str]=None):

		self._id = id
		self._assets = list()

	@classmethod
	def fromFile(cls, path:str) -> "Pkl":
		"""Parse an existing PKL"""

		ns = dict()

		file_pkl = et.parse(path)
		root = file_pkl.getroot()

		# Extract namespace from root tag
		ns = {"pkl": pat_nsextract.match(root.tag).group(1)}
		
		id = root.find("pkl:Id", ns).text
		assetlist = root.find("pkl:AssetList", ns)
		
		pkl = cls(id)

		for asset in assetlist:
			pkl.addAsset(Asset.fromXml(asset, ns))
		
		return pkl
	
	def addAsset(self, asset:"Asset"):
		"""Add an asset this package"""
		self._assets.append(asset)
	
	def getAsset(self, id:str) -> "Asset":
		for asset in self.assets:
			if asset.id == id: return asset		
		None
	
	@property
	def assets(self) -> typing.List[Asset]:
		return list(self._assets)

	@property
	def id(self) -> str:
		return str(self._id)