import dataclasses, typing, datetime, re
import xml.etree.ElementTree as et
from imflib import xsd_datetime_to_datetime

@dataclasses.dataclass(frozen=True)
class AssetMap:
	"""An Asset Map component of an IMF package"""
	id:str
	annotation_text:str
	creator:str
	volume_count:int	# TODO: Make dynamic property based on asset chunks?
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
		annotation_text = xml.find("AnnotationText",ns).text if xml.find("AnnotationText",ns) is not None else ""	# None instead of empty string...?
		creator = xml.find("Creator",ns).text
		volume_count = int(xml.find("VolumeCount",ns).text)
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
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



@dataclasses.dataclass(frozen=True)
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
	def file_paths(self)->list[str]:
		"""All file paths associated with this asset"""
		return [chunk.file_path for chunk in self.chunks]




@dataclasses.dataclass(frozen=True)
class Chunk:
	"""A chunk of an Asset"""
	file_path:str
	volume_index:int
	offset:int
	size:int

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Chunk":
		"""Parse a chunk of an Asset from a ChunkList"""
		chunks = []
		for chunk in xml.findall("Chunk",ns):
			path = chunk.find("Path",ns).text
			volume_index = int(chunk.find("VolumeIndex",ns).text) if chunk.find("VolumeIndex",ns) is not None else 1
			offset = int(chunk.find("Offset",ns).text) if chunk.find("Offset",ns) is not None else 0
			size = int(chunk.find("Length",ns).text) if chunk.find("Length",ns) is not None else 0
			chunks.append(cls(path, volume_index, offset, size))
		return chunks