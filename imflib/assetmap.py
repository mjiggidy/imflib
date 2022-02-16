import dataclasses, datetime, typing, pathlib
import xml.etree.ElementTree as et

@dataclasses.dataclass()
class AssetMap:
	"""An Asset Map component of an IMF package"""
	id:str
	annotation_text:str
	creator:str
	volume_count:int	# TODO: Make dynamic property?
	issue_date:datetime.datetime
	issuer:str
	assets:list["Asset"]

	@classmethod
	def fromFile(cls, path:str)->"AssetMap":
		"""Parse an existing AssetMap file"""
		file_am = et.parse(path)
		return cls.fromXml(file_am.getroot(),{"":"http://www.smpte-ra.org/schemas/429-9/2007/AM"})
	
	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"AssetMap":
		"""Parse the AssetMap from XML"""
		id = xml.find("Id",ns).text
		annotation_text = xml.find("AnnotationText",ns).text if xml.find("AnnotationText",ns) is not None else ""
		creator = xml.find("Creator",ns).text
		volume_count = int(xml.find("VolumeCount",ns).text) if isinstance(xml.find("VolumeCount",ns),int) else 0
		issue_date = datetime.datetime.fromisoformat(xml.find("IssueDate",ns).text) if xml.find("IssueDate",ns) is not None else datetime.datetime()
		issuer = xml.find("Issuer",ns).text
		assets = Asset.fromXml(xml.find("AssetList",ns), ns)

		return cls(id, annotation_text, creator, volume_count,issue_date, issuer, assets)
	
	@property
	def packing_lists(self)->list["Asset"]:
		"""A list of packing lists in this package"""
		return [asset for asset in self.assets if asset.is_packing_list]
	
	@property
	def total_size(self)->int:
		"""Total size of the assets in this map"""
		return sum(asset.size for asset in self.assets)



@dataclasses.dataclass()
class Asset:
	"""An Asset as defined in an IMF AssetMap"""
	id:str
	is_packing_list:bool
	chunks:list["Chunk"]

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->list["Asset"]:
		"""Parse an Asset from an AssetList XML Element"""
		assets = []
		for asset in xml.findall("Asset",ns):
			id = asset.find("Id",ns).text
			is_packing_list = (asset.find("PackingList",ns) is not None) and (asset.find("PackingList",ns).text.lower() == "true")
			chunks = Chunk.fromXml(asset.find("ChunkList",ns),ns)
			assets.append(cls(id, is_packing_list, chunks))
		return assets
	
	@property
	def size(self)->int:
		"""Total size of this asset in bytes"""
		return sum(chunk.size for chunk in self.chunks)
	
	@property
	def file_paths(self)->list[pathlib.Path]:
		"""All file paths associated with this asset"""
		return [chunk.file_path for chunk in self.chunks]




@dataclasses.dataclass()
class Chunk:
	"""A chunk of an Asset"""
	file_path:pathlib.Path
	volume_index:int
	offset:int
	size:int

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Chunk":
		"""Parse a chunk of an Asset from a ChunkList"""
		chunks = []
		for chunk in xml.findall("Chunk",ns):
			path = pathlib.Path(chunk.find("Path",ns).text)
			volume_index = int(chunk.find("VolumeIndex",ns).text)
			offset = int(chunk.find("Offset",ns).text)
			size = int(chunk.find("Length",ns).text)
			chunks.append(cls(path, volume_index, offset, size))
		return chunks