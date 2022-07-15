# Based on SMPTE 429-8-2007: https://ieeexplore.ieee.org/document/7290438

# NOTE:
# ASSETMAP.xml is the entry point into the package
# AssetMap provides the mapping between PKL UUIDs and file locations on a volume
# The assetmap must exist on each volume it references
# If multiple volumes are referenced, a VOLINDEX.xml file must be present with a unique index on each volume
# The assetmap may contain mappings for more than one package

import dataclasses, typing, datetime
import xml.etree.ElementTree as et
from imflib import xsd_datetime_to_datetime, xsd_optional_string, xsd_optional_integer, xsd_optional_bool, xsd_uuid_is_valid

@dataclasses.dataclass(frozen=True)
class AssetMap:
	"""An Asset Map component of an IMF package"""

	id:str
	"""Unique identifier for this asset map encoded as a urn:UUID [RFC 4122]"""

	annotation_text:str
	"""Optional description of this asset map"""

	creator:str
	"""The facility or system that created this asset map"""

	volume_count:int	# TODO: Per SMPTE 0429-9-2014 update, "Volume Count shall be 1."  So uh...
	"""Total number of volumes referenced by this asset map"""

	issue_date:datetime.datetime
	"""Datetime this asset map was issued"""

	issuer:str
	"""The person or company that issued this asset map"""

	assets:list["Asset"]
	"""The list of mapped `Asset`s"""

	@classmethod
	def from_file(cls, path:str)->"AssetMap":
		"""Parse an existing AssetMap file"""
		file_am = et.parse(path)
		return cls.from_xml(file_am.getroot(),{"":"http://www.smpte-ra.org/schemas/429-9/2007/AM"})
	
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"AssetMap":
		"""Parse the AssetMap from XML"""
		id = xml.find("Id",ns).text
		if not xsd_uuid_is_valid(id):
			raise ValueError(f"The given UUID {id} is not RFC 4122 compliant")
		
		annotation_text = xsd_optional_string(xml.find("AnnotationText",ns))
		creator = xml.find("Creator",ns).text
		volume_count = int(xml.find("VolumeCount",ns).text)
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
		issuer = xml.find("Issuer",ns).text
		assets = [Asset.from_xml(asset,ns) for asset in xml.find("AssetList",ns)]

		return cls(
			id=id,
			annotation_text=annotation_text,
			creator=creator,
			volume_count=volume_count,
			issue_date=issue_date,
			issuer=issuer,
			assets=assets
		)
	
	@property
	def packing_lists(self)->list["Asset"]:
		"""A list of packing lists in this package"""
		return [asset for asset in self.assets if asset.is_packing_list]
	
	@property
	def total_size(self)->int:
		"""Total size of the assets in this map"""
		return sum(asset.total_size for asset in self.assets)

	def get_asset(self, id:str) -> "Asset":
		"""Get an Asset from the AssetMap based on the URN ID"""
		for asset in self.assets:
			if asset.id == id: return asset		
		return None

# TODO: Per SMPTE 0429-9-2014 update, "The VolumeIndex structure is not used."  Look into the existence of any 2007-era spec'd IMFs?
@dataclasses.dataclass(frozen=True)
class VolumeIndex:
	"""A `VolumeIndex` file required only in multi-volume packages"""

	index:int
	"""The index of this volume as referenced by the `AssetMap`"""

	@classmethod
	def from_file(cls, path:str)->"VolumeIndex":
		"""Parse an existing VolumeIndex file"""
		file_am = et.parse(path)
		return cls.from_xml(file_am.getroot(),{"":"http://www.smpte-ra.org/schemas/429-9/2007/AM"})
	
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"AssetMap":
		"""Parse the AssetMap from XML"""
		return cls(
			index = int(xml.find("Index",ns).text)
		)


@dataclasses.dataclass(frozen=True)
class Asset:
	"""An Asset as defined in an IMF AssetMap"""

	id:str
	"""Unique package identifier encoded as a urn:UUID [RFC 4122]"""


	chunks:list["Chunk"]
	"""List of `Chunk`s spanned by the file"""
	
	is_packing_list:typing.Optional[bool]=False
	"""Whether the asset is a Packing List (PKL)"""

	annotation_text:typing.Optional[str]=""
	"""Optional description of this asset"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Asset":
		"""Parse an Asset from an AssetList XML Element"""
		
		id = xml.find("Id", ns).text
		if not xsd_uuid_is_valid(id):
			raise ValueError(f"The given UUID {id} is not RFC 4122 compliant")

		is_packing_list = xsd_optional_bool(xml.find("PackingList",ns))
		chunks = [Chunk.from_xml(chunk, ns) for chunk in xml.find("ChunkList",ns)]
		annotation_text = xsd_optional_string(xml.find("AnnotationText", ns))

		return cls(
			id=id,
			is_packing_list=is_packing_list,
			chunks=chunks,
			annotation_text=annotation_text
		)
	
	@property
	def total_size(self)->int:
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
	"""Relative file path to the chunk"""

	volume_index:int=1 # TODO: Per SMPTE 0429-9-2014 update, "Volume Count shall be 1."
	"""Index of the volume containing the chunk"""

	offset:int=0
	"""Byte offset from the beginning of the assembled `Asset`"""

	size:typing.Optional[int]=None
	"""Size of the chunk data in bytes"""
	# TODO: "If the Length parameter is absent, the length of the chunk shall be that of the asset as expressed by the respective Packing List."

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Chunk":
		"""Parse a chunk of an Asset from a ChunkList"""

		file_path = xml.find("Path",ns).text
		volume_index = xsd_optional_integer(xml.find("VolumeIndex",ns), 1)
		offset = xsd_optional_integer(xml.find("Offset",ns),0)
		size = xsd_optional_integer(xml.find("Length",ns), None)
		
		return cls(
			file_path=file_path,
			volume_index=volume_index,
			offset=offset,
			size=size
		)