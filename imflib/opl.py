# TODO: Actually make this
# https://smpte-ra.org/sites/default/files/st2067-100a-2014.xsd

import dataclasses, typing, datetime, abc
import xml.etree.ElementTree as et
from . import xsd_optional_string, xsd_datetime_to_datetime



@dataclasses.dataclass(frozen=True)
class Macro(abc.ABC):
	"""An abstract OPL Macro"""
	
	name:str
	annotation_text:str

	@abc.abstractclassmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Macro":
		"""Parse Macro from XML"""
	
		
@dataclasses.dataclass(frozen=True)
class PresetMacro(Macro):
	"""A Preset Macro"""
	
	preset:str

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"PresetMacro":

		name = xml.find("Name",ns).text
		annotation_text = xsd_optional_string(xml.find("Annotation",ns))
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
	# TODO: Spec loosely defines as lax processing, any namespace. Cool.
	# TODO: Decide upon a better implementation.
	raw_xml:str

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Alias":
		"""Capture an alias from the list"""
		try:
			raw_xml = et.tostring(xml, encoding="unicode", method="xml").strip()
		except Exception as e:
			raw_xml = f"Unknown alias: {e}"
		return cls(raw_xml)

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

	id:str
	annotation_text:str
	issue_date:datetime.datetime
	issuer:str
	creator:str
	cpl_id:str

	extension_properties:list[ExtensionProperty]
	alias_list:list[Alias]
	macro_list:list[Macro]


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

		id = xml.find("Id", ns).text
		annotation_text = xsd_optional_string(xml.find("Annotation",ns))
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
		issuer = xsd_optional_string(xml.find("Issuer",ns))
		creator = xsd_optional_string(xml.find("Creator",ns))
		cpl_id = xml.find("CompositionPlaylistId",ns).text

		# Extension properties
		extension_properties = list()
		for extension_properties in xml.findall("ExtensionProperties",ns):
			for prop in extension_properties:
				extension_properties.append(ExtensionProperty.from_xml(prop,ns))
		
		# Alias list
		alias_list = list()
		for alias in xml.find("AliasList",ns):
			alias_list.append(Alias.from_xml(alias,ns))
		
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
			alias_list=alias_list,
			macro_list=macro_list
		)