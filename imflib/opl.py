# TODO: Actually make this
# https://smpte-ra.org/sites/default/files/st2067-100a-2014.xsd

import dataclasses, typing
import xml.etree.ElementTree as et

@dataclasses.dataclass(frozen=True)
class Opl:
	"""An IMF Output Profile List"""

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

		