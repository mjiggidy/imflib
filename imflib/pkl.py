# Based on SMPTE 429-8-2007
# https://ieeexplore.ieee.org/document/7290849?arnumber=7290849

import dataclasses, typing, datetime
import xml.etree.ElementTree as et
from imflib import xsd_datetime_to_datetime, xsd_optional_string

@dataclasses.dataclass()
class Asset:
	"""An asset packed into this IMF package"""
	
	id:str
	hash:str
	hash_type:str
	size:int
	type:str
	file_name:str=""
	annotation_text:str=""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:dict) -> list["Asset"]:
		"""Create an asset from an XML element"""

		assets = []

		for asset in xml.findall("Asset",ns):
			id = asset.find("Id", ns).text
			hash = asset.find("Hash", ns).text
			hash_type = asset.find("HashAlgorithm", ns).attrib.get("Algorithm").split("#")[-1] # TODO: Only SHA-1 is currently supported. Maybe hard-code this?
			size = int(asset.find("Size", ns).text)
			type = asset.find("Type", ns).text
			file_name = xsd_optional_string(asset.find("OriginalFileName", ns))
			annotation_text = xsd_optional_string(asset.find("AnnotationText", ns))
			assets.append(cls(
				id,
				hash,
				hash_type,
				size,
				type,
				file_name,
				annotation_text
			))

		return assets

@dataclasses.dataclass(frozen=True)
class Pkl:
	"""An IMF PKL Packing List"""

	id:str
	"""Unique package identifier encoded as a urn:UUID [RFC 4122]"""
	
	issue_date:datetime.datetime
	"""Datetime this PKL was issued"""

	issuer:str
	"""The person or company that issued this PKL"""

	creator:str
	"""The facility or system that created this PKL"""

	assets:list["Asset"]
	"""The list of `Asset`s contained in this package"""

	annotation_text:typing.Optional[str]=""
	"""Optional description of the distribution package"""

	group_id:typing.Optional[str]=""
	"""Optional UUID referencing a group of multiple packages to which this package belongs"""

	icon_id:typing.Optional[str]=""
	"""Optional UUID reference to an image asset to be used as an icon"""

	@classmethod
	def from_file(cls, path:str) -> "Pkl":
		"""Parse an existing PKL from a given file path"""

		file_pkl = et.parse(path)
		return cls.from_xml(file_pkl.getroot(), {"":"http://www.smpte-ra.org/schemas/2067-2/2016/PKL"})
	
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Pkl":
		"""Parse a PKL from XML"""

		id = xml.find("Id", ns).text
		issuer = xml.find("Issuer", ns).text
		creator = xml.find("Creator", ns).text
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
		assets = Asset.from_xml(xml.find("AssetList",ns),ns)

		annotation_text = xsd_optional_string(xml.find("AnnotationText", ns))
		group_id = xsd_optional_string(xml.find("GroupId", ns))
		icon_id = xsd_optional_string(xml.find("IconId", ns))

		return cls(
			id=id,
			issuer=issuer,
			creator=creator,
			issue_date=issue_date,
			assets=assets,
			annotation_text=annotation_text,
			group_id=group_id,
			icon_id=icon_id
		)
	
	def get_asset(self, id:str) -> "Asset":
		"""Get an Asset from the PKL based on the URN ID"""
		for asset in self.assets:
			if asset.id == id: return asset		
		return None
	
	@property
	def total_size(self)->int:
		"""Total size of assets in bytes"""
		return sum(a.size for a in self.assets)