__all__ = ["assetmap","pkl","cpl","imf","opl"]

import datetime, re, typing, dataclasses
import xml.etree.ElementTree as et

PAT_UUID = re.compile(r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
PAT_DATE = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}(?:\.\d+)?)(?P<timezone>(?:Z)|([\+\-].+))?$", re.I)

@dataclasses.dataclass(frozen=True)
class UserText:
	"""UserText XSD data type"""

	# <xs:complexType name="UserText">
	# 	<xs:simpleContent>
	# 		<xs:extension base="xs:string">
	# 			<xs:attribute name="language" type="xs:language" use="optional" default="en"/>
	# 		</xs:extension>
	# 	</xs:simpleContent>
	# </xs:complexType>

	text:str=""
	"""Human-readable string"""
	language:str="en"
	"""Language of `text`"""

	def __str__(self):
		return self.text
	
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "UserText":
		"""Parse an xs:UserText type"""

		text = xml.text
		lang = xml.attrib.get("language","en")

		return cls(
			text=text,
			language=lang
		)

# TODO: Placeholder data structure for now, may need to replace with an external dependency
# TODO: Need to even get some IMFs that are signed.  Never seen one.
@dataclasses.dataclass(frozen=True)
class Security:
	"""NOTE: Untested placeholder data class that is unlikely to actually work"""

	signature:et.Element
	"""The digitial signature"""

	signer:et.Element
	"""The unique identity of the entity"""

	@classmethod
	def from_xml(cls, xml_signer:et.Element, xml_signature:et.Element, ns:typing.Optional[dict]=None) -> "Security":
		"""Parse the securty from XML"""
		return cls(
			signature=xml_signature,
			signer=xml_signer
		)




def xsd_datetime_to_datetime(xsd_datetime:str)->datetime:
	"""Convert XML XSD DateTime to python datetime"""
	# XSD DateTime format is:
	# YYYY-MM-DDTHH:MM:SS(.SS)
	#
	# Followed optionally by
	# Z        - UTC
	# +|-HH:MM - Timezone offset from UTC

	match_date = PAT_DATE.match(xsd_datetime)
	if not match_date:
		raise Exception(f"Invalid XSD DateTime: {xsd_datetime}")

	# Reconcile timezone situation
	if match_date.group("timezone") is None or match_date.group("timezone").lower() == 'z':
		tz_delta = datetime.timezone.utc
	else:
		tz_h, tz_m = tuple([float(x) for x in match_date.group("timezone").split(':')])
		tz_delta = datetime.timezone(datetime.timedelta(hours=tz_h, minutes=tz_m))
	
	# Here we go
	return datetime.datetime(
		year        = int(match_date.group("year")),
		month       = int(match_date.group("month")),
		day         = int(match_date.group("day")),
		hour        = int(match_date.group("hour")),
		minute      = int(match_date.group("minute")),
		second      = int(match_date.group("second").split('.')[0]),
		microsecond = int(match_date.group("second").split('.')[1] if '.' in match_date.group("second") else 0),
		tzinfo      = tz_delta
	)

def xsd_optional_string(xml:typing.Optional[et.Element], default_value:str="") -> typing.Union[str,None]:
	"""Return a string that may be optionally defined in the XML"""
	return xml.text if xml is not None else default_value

def xsd_optional_integer(xml:typing.Optional[et.Element], default_value:typing.Optional[int]=None) -> typing.Union[int,None]:
	"""Return an integer that may be optionally defined in the XML"""
	return int(xml.text) if xml is not None and xml.text.isnumeric() else default_value

def xsd_optional_bool(xml:typing.Optional[et.Element], default_value:bool=False) -> bool:
	"""Return a `bool` from an optional `xs:bool`"""
	return (xml.text.lower() == "true") if xml is not None else default_value

def xsd_optional_usertext(xml:typing.Optional[et.Element], default_value:typing.Optional[UserText]=None) -> typing.Union[UserText,None]:
	"""Return an optional `UserText` type"""
	return UserText.from_xml(xml) if xml is not None else default_value

def xsd_uuid_is_valid(uuid:str) -> bool:
	"""Validate a given UUID against RFC 4122"""
	return PAT_UUID.match(uuid)
