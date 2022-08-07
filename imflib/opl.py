# TODO: Actually make this
# https://smpte-ra.org/sites/default/files/st2067-100a-2014.xsd

import dataclasses, typing, datetime, abc, uuid, re
import xml.etree.ElementTree as et
from imflib import xsd_datetime_to_datetime, xsd_optional_usertext, UserText, Security


class MacroName(str):
	"""A string restricted confined to the opl:MacroNameType schema"""

	PAT_MACRO_NAME_TYPE = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]*$")

	def __new__(cls, input_string:str):
		if not cls.PAT_MACRO_NAME_TYPE.match(input_string):
			raise ValueError("String does not validate against the opl:MacroNameType schema")
		
		return super().__new__(cls, input_string)


@dataclasses.dataclass(frozen=True)
class Macro(abc.ABC):
	"""An abstract OPL Macro"""

	"""
	TODO: 7. Processing Model from st2067-100-2014:
	Each Macro present in the MacroList element shall be executed in full and in the order it appears in the element.
	A first Macro instance that references the output of a second Macro instance shall not appear in the MacroList 
	before the second Macro instance.
	"""
	
	name:MacroName
	"""The unique name of the macro instance"""

	annotation_text:typing.Optional[UserText]=None
	"""Optional description of this macro"""

	@abc.abstractclassmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Macro":
		"""Parse Macro from XML"""
	
		
@dataclasses.dataclass(frozen=True)
class PresetMacro(Macro):
	"""A Preset Macro"""

	"""TODO: Annex B
	An Output Profile List instance that contains a Preset Macro instance shall not contain any other Macro instances.
	Such an Output Profile List instance is called a Simple OPL.
	"""
	
	preset:str=""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"PresetMacro":

		name = MacroName(xml.find("Name",ns).text)
		annotation_text = xsd_optional_usertext(xml.find("Annotation",ns))
		preset = xml.find("Preset",ns).text

		return cls(
			name=name,
			annotation_text=annotation_text,
			preset=preset
		)
		
MACRO_TYPES = {
	"PresetMacroType":PresetMacro
}


@dataclasses.dataclass(frozen=True)
class Alias:
	"""An OPL Alias"""

	# TODO: "Note: two Alias elements shall have the same value."
	# Maybe make this a dict instead

	handle:str	# TODO: These values should both
	alias:str	# be restricted to relative URIs
	
	"""
	TODO:
	Given the Alias element "<Alias handle='macros/image-scaler-1/outputs/images'>MainImage</Alias>",
	the Handle "alias/MainImage" is synonymous with the Handle "macros/image-scaler-1/outputs/images".
	"""
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Alias":
		"""Capture an alias from XML"""
		handle = xml.attrib.get("handle")
		alias = xml.text
		return cls(
			handle=handle,
			alias=alias
		)


@dataclasses.dataclass(frozen=True)
class ExtensionProperty:
	"""An OPL Extension Property"""
	# TODO: Spec loosely defines as lax processing, any namespace. Cool.
	# TODO: Decide upon a better implementation.
	raw_xml:str

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"ExtensionProperty":
		"""Capture an extention property from the list"""
		try:
			raw_xml = et.tostring(xml, encoding="unicode", method="xml").strip()
		except Exception as e:
			raw_xml = f"Unknown extension property: {e}"
		return cls(raw_xml)

@dataclasses.dataclass(frozen=True)
class Opl:
	"""An IMF Output Profile List"""

	id:uuid.UUID
	"""Unique identifier for this OPL; encoded as a urn:UUID [RFC 4122]"""

	cpl_id:uuid.UUID
	"""Existing UUID of the CPL upon which this OPL operates; encoded as a urn:UUID [RFC 4122]"""

	issue_date:datetime.datetime
	"""Datetime this OPL was issued"""

	aliases:set[Alias]
	"""A set of unique `Alias` elements which define additional synonyms for `Handle` s"""

	macros:list[Macro]
	"""An ordered list of `Macro` elements"""
	# TODO: Per st2067-100-2014: "Multiple Macro elements may have the same type but no two Macro elements shall have the same Name value."

	# NOTE: Issuer and creator are optional, unlike CPL/PKL/etc
	issuer:typing.Optional[UserText]=None
	"""The person or company that issued this OPL"""

	extension_properties:list[ExtensionProperty]=dataclasses.field(default_factory=list)
	"""An unordered list of `ExtensionProperty` s which may be used by applications to add descriptive metadata to the OPL"""
	# TODO: Unordered yes; unique... maybe?  So a set instead of a list perhaps?

	creator:typing.Optional[UserText]=None
	"""The facility or system that created this OPL"""

	annotation_text:typing.Optional[UserText]=None
	"""Optional description of this OPL"""

	security:typing.Optional[Security]=None
	"""Signer and signature of authenticity"""

	@classmethod
	def from_file(cls, path:str) -> "Opl":
		"""Parse an existing OPL from a given file path."""
		file_opl = et.parse(path)
		return cls.from_xml(file_opl.getroot(), {"":"http://www.smpte-ra.org/schemas/2067-100/2014"})
	
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Opl":
		"""
		Parse an existing OPL from a given root XMLElementTree Element
		Intended to be called from Opl.from_file(), but you do you.
		"""

		id = uuid.UUID(xml.find("Id", ns).text)
		cpl_id = uuid.UUID(xml.find("CompositionPlaylistId",ns).text)
		annotation_text = xsd_optional_usertext(xml.find("Annotation",ns))
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
		issuer = xsd_optional_usertext(xml.find("Issuer",ns))
		creator = xsd_optional_usertext(xml.find("Creator",ns))

		# Extension properties list
		extension_properties = [prop for prop in xml.findall("ExtensionProperties",ns)]
		
		# Alias set
		alias_list = {alias_list.add(Alias.from_xml(alias,ns)) for alias in xml.find("AliasList",ns)}
		
		# Macro list
		macro_list = list()
		for macro in xml.find("MacroList",ns):
			# TODO: Probably want to move this off to a factory thingy
			# <Macro> should contain an xsi:type attribute maybe
			type_attrib = macro.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type")
			if type_attrib in MACRO_TYPES:
				macro_list.append(MACRO_TYPES.get(type_attrib).from_xml(macro,ns))

		return cls(
			id=id,
			annotation_text=annotation_text,
			issue_date=issue_date,
			issuer=issuer,
			creator=creator,
			cpl_id=cpl_id,
			extension_properties=extension_properties,
			aliases=alias_list,
			macros=macro_list
		)