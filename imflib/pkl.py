import datetime
import xml.etree.ElementTree as et
import dataclasses, typing, re
from imflib import xsd_datetime_to_datetime

pat_nsextract = re.compile(r'^\{(.+)\}')

@dataclasses.dataclass()
class Asset:
	"""An asset packed into this IMF package"""
	id:str
	file_name:str
	size:int
	type:str

	@classmethod
	def fromXml(cls, xml:et.Element, ns:dict) -> list["Asset"]:
		"""Create an asset from an XML element"""

		assets = []
		for asset in xml.findall("Asset",ns):
			id = asset.find("Id", ns).text
			file_name = asset.find("OriginalFileName", ns).text
			size = int(asset.find("Size", ns).text)
			type = asset.find("Type", ns).text
			assets.append(cls(id, file_name, size, type))
		return assets

@dataclasses.dataclass(frozen=True)
class Pkl:
	"""An IMF PKL Packing List"""

	id:str
	issuer:str
	creator:str
	issue_date:datetime.datetime
	assets:list["Asset"]
	annotation_text:str
	group_id:str
	icon_id:str

	@classmethod
	def fromFile(cls, path:str) -> "Pkl":
		"""Parse an existing PKL"""

		file_pkl = et.parse(path)
		return cls.fromXml(file_pkl.getroot(), {"":"http://www.smpte-ra.org/schemas/2067-2/2016/PKL"})
	
	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Pkl":
		"""Parse a PKL from XML"""

		id = xml.find("Id", ns).text
		issuer = xml.find("Issuer", ns).text
		creator = xml.find("Creator", ns).text
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
		assets = Asset.fromXml(xml.find("AssetList",ns),ns)

		annotation_text = xml.find("AnnotationText", ns).text if xml.find("AnnotationText", ns) is not None else ""
		group_id = xml.find("GroupId", ns).text if xml.find("GroupId", ns) is not None else ""
		icon_id = xml.find("IconId", ns).text if xml.find("IconId", ns) is not None else ""

		return cls(id, issuer, creator, issue_date, assets, annotation_text,group_id,icon_id)
	
	def getAsset(self, id:str) -> "Asset":
		for asset in self.assets:
			if asset.id == id: return asset		
		return None
	
	@property
	def total_size(self)->int:
		"""Total size of assets in bytes"""
		return sum(a.size for a in self.assets)