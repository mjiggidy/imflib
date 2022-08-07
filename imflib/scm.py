# Based on SMPTE 2067-9-2018: https://ieeexplore.ieee.org/document/8387023

import xml.etree.ElementTree as et
import typing, dataclasses, uuid, datetime
from imflib import UserText, Security
from imflib import xsd_optional_usertext, xsd_datetime_to_datetime, xsd_optional_security

@dataclasses.dataclass(frozen=True)
class SidecarAsset:
	"""A SMPTE ST 2017-9-2018 Sidecar Asset-to-CPL Mapping"""

	id:uuid.UUID
	"""UUID of the Sidecar Asset"""
	# TODO: "Its value shall be the Id used by the Packing List to reference the Asset, 
	# as defined in Section 7.3.1 of SMPTE ST 2067-2." (7.3.1)

	associated_cpl_ids:set[uuid.UUID]
	"""Unique list of CPL UUIDs associated with this asset"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "SidecarAsset":
		"""Parse a Sidecar Asset from XML"""

		id = uuid.UUID(xml.find("Id",ns).text)
		cpl_ids = {uuid.UUID(x.text) for x in xml.findall("AssociatedCPLList/CPLId",ns)}

		return cls(
			id=id,
			associated_cpl_ids=cpl_ids
		)


@dataclasses.dataclass(frozen=True)
class SidecarCompositionMap:
	"""A SMPTE ST 2017-9-2018 Sidecar Composition Map"""

	# TODO: "Each such Sidecar Composition Map instance shall only reference Sidecar Assets
	# contained in the same IMP.  Compositions referenced by a Sidecar Composition Map instance 
	# are not necessarily contained in the same IMP." (8.0)

	id:uuid.UUID
	"""UUID of this SCM"""
	# TODO: "Any two Sidecar Composition Maps may have equal Id values 
	# if and only if the two Sidecar Composition Maps are identical." (7.2.1)

	issue_date:datetime.datetime
	"""Datetime this SCM was issued"""

	assets:typing.List[SidecarAsset]
	"""A list of sidecar assets"""
	# TODO: "The child Id element value of each SidecarAsset shall be unique 
	# within the SidecarAssetList. (7.2.3)

	issuer:typing.Optional[UserText]=None
	"""The person or company that issued this SCM"""
	
	annotation:typing.Optional[UserText]=None
	"""Human-readable description of this SCM"""

	additional_properties:list[et.Element]=dataclasses.field(default_factory=list)
	"""Additional properties defined in this SCM"""

	security:typing.Optional[Security]=None
	"""XML signer and signature"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "SidecarCompositionMap":
		"""Parse an SCM from XML"""

		id = uuid.UUID(xml.find("Id",ns).text)
		
		annotation = xsd_optional_usertext(xml.find("Properties/Annotation",ns))
		issue_date = xsd_datetime_to_datetime(xml.find("Properties/IssueDate",ns).text)
		issuer = xsd_optional_usertext(xml.find("Properties/Issuer",ns))

		# TODO: Need a better way
		known_properties = {
			xml.find("Properties/Annotation",ns),
			xml.find("Properties/IssueDate",ns),
			xml.find("Properties/Issuer",ns)
		}
		additional_properties = [x for x in xml.findall("Properties/*",ns) if x not in known_properties]
		assets = [SidecarAsset.from_xml(a,ns) for a in xml.findall("SidecarAssetList/SidecarAsset",ns)]
		securtity = xsd_optional_security(xml.find("Signer",ns),xml.find("Signature",ns))

		return cls(
			id=id,
			annotation=annotation,
			issue_date=issue_date,
			issuer=issuer,
			additional_properties=additional_properties,
			assets=assets,
			security=securtity
		)

	@classmethod
	def from_file(cls, path:str) -> "SidecarCompositionMap":
		"""Parse an existing SCM from a given file path"""
		xml_scm = et.parse(path)
		return cls.from_xml(xml_scm.getroot(), {
			"":     "http://www.smpte-ra.org/ns/2067-9/2018",
			"scm":  "http://www.smpte-ra.org/ns/2067-9/2018",
			"dcml": "http://www.smpte-ra.org/schemas/433/2008/dcmlTypes/",
			"ds":   "http://www.w3.org/2000/09/xmldsig#",
			"xs":   "http://www.w3.org/2001/XMLSchema"
			}
		)