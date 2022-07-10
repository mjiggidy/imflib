import datetime
import xml.etree.ElementTree as et
import dataclasses, typing
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
	issuer:str
	creator:str
	issue_date:datetime.datetime
	assets:list["Asset"]
	annotation_text:str=""
	group_id:str=""
	icon_id:str=""

	@classmethod
	def from_file(cls, path:str) -> "Pkl":
		"""Parse an existing PKL"""

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
			id,
			issuer,
			creator,
			issue_date,
			assets,
			annotation_text,
			group_id,
			icon_id
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