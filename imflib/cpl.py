import xml.etree.ElementTree as et
import dataclasses, typing, re, abc, datetime
from posttools import timecode
from imflib import xsd_datetime_to_datetime, xsd_optional_string

pat_nsextract = re.compile(r'^\{(?P<uri>.+)\}(?P<name>[a-z0-9]+)',re.I)

@dataclasses.dataclass(frozen=True)
class Resource(abc.ABC):
	"""A resource within a sequence"""

	id:str
	intrinsic_duration:int
	
	annotation:typing.Optional[str]
	edit_rate:"EditRate"
	entry_point:typing.Optional[int]
	source_duration:typing.Optional[int]
	repeat_count:typing.Optional[int]

@dataclasses.dataclass(frozen=True)
class TrackFileResource(Resource):
	"""A file-based resource"""
	source_encoding:str
	track_file_id:str

	key_id:typing.Optional[str]
	hash:typing.Optional[str]
	hash_algorithm:typing.Optional[str]

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"ImageResource":

		# BaseResource
		id = xml.find("Id",ns).text
		intrinsic_duration = int(xml.find("IntrinsicDuration",ns).text)
		# BaseResource Optional
		annotation = xsd_optional_string(xml.find("Annotation",ns))
		edit_rate = EditRate.fromXml(xml.find("EditRate",ns), ns) if xml.find("EditRate",ns) is not None else None
		entry_point = int(xml.find("EntryPoint",ns).text) if xml.find("EntryPoint",ns) is not None else None
		source_duration = int(xml.find("SourceDuration",ns).text) if xml.find("SourceDuration",ns) is not None else None
		repeat_count = int(xml.find("RepeatCount",ns).text) if xml.find("RepeatCount",ns) is not None else 0

		# TrackFileResource
		source_encoding = xml.find("SourceEncoding",ns).text
		track_file_id = xml.find("TrackFileId",ns).text
		# TrackResource Optional
		key_id = xsd_optional_string(xml.find("KeyId",ns))
		hash = xsd_optional_string(xml.find("Hash",ns))
		hash_algorithm = xsd_optional_string(xml.find("HashAlgorithm",ns))


		return cls(id=id,
		intrinsic_duration=intrinsic_duration,
		annotation=annotation,
		edit_rate=edit_rate,
		entry_point=entry_point,
		source_duration=source_duration,
		repeat_count=repeat_count,
		source_encoding=source_encoding,
		track_file_id=track_file_id,
		key_id=key_id,
		hash=hash,
		hash_algorithm=hash_algorithm)

@dataclasses.dataclass(frozen=True)
class ImageResource(TrackFileResource):
	"""A main image resource"""

	edit_units:str = "fps"

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "ImageResource":
		res = super().fromXml(xml,ns)
		# I am surprised this just works
		return res
	
@dataclasses.dataclass(frozen=True)
class AudioResource(TrackFileResource):
	"""A main audio resource"""

	edit_units:str = "Hz"

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "AudioResource":
		res = super().fromXml(xml,ns)
		return res


@dataclasses.dataclass(frozen=True)
class Sequence:
	"""A sequence within a segment"""
	id:str
	track_id:str
	resources:typing.List[Resource]

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "Sequence":
		"""Parse from XML"""

		if xml.tag.endswith("MainImageSequence"):
			return MainImageSequence.fromXml(xml, ns)
		
		elif xml.tag.endswith("MainAudioSequence"):
			return MainAudioSequence.fromXml(xml, ns)
		
		# TODO: Implement additional
		else:
			raise Exception(f"Nope. {xml.tag}")

class MainImageSequence(Sequence):
	"""An XSD MainImageSequenceType from IMF Core Constraints"""

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "MainImageSequence":
		"""Parse from XML"""
		
		id = xml.find("Id",ns).text
		track_id = xml.find("TrackId",ns).text
		
		resource_list = list()
		for resource in xml.find("ResourceList",ns).findall("Resource",ns):
			resource_list.append(ImageResource.fromXml(resource, ns))

		return cls(id=id, track_id=track_id, resources=resource_list)

class MainAudioSequence(Sequence):
	"""Main audio sequence of a segment"""
	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "MainImageSequence":
		"""Parse from XML"""
		id = xml.find("Id",ns).text
		track_id = xml.find("TrackId",ns).text
		
		resource_list = list()
		for resource in xml.find("ResourceList",ns).findall("Resource",ns):
			resource_list.append(AudioResource.fromXml(resource, ns))

		return cls(id=id, track_id=track_id, resources=resource_list)

@dataclasses.dataclass(frozen=True)
class Segment:
	"""A CPL segment"""
	id:str
	sequences:typing.List[Sequence]
	annotation:typing.Optional[str]=""

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]) -> "Segment":

		id = xml.find("Id",ns).text
		annotation = xsd_optional_string(xml.find("Annotation",ns))

		sequence_list = list()

		for sequence in xml.find("SequenceList", ns):
			sequence_list.append(Sequence.fromXml(sequence,ns))

		return cls(
			id=id,
			sequences=sequence_list,
			annotation=annotation
		)
	
	@property
	def resources(self) -> typing.List[Resource]:
		reslist = list()
		for seq in self.sequences:
			reslist.extend(seq.resources)
		return reslist

@dataclasses.dataclass(frozen=True)
class ContentVersion:
	"""A content version"""

	id:str
	label:str
	additional:typing.Any=None	# TODO: Investigate handling of xs:any tags, ambiguous in spec

	@classmethod
	def fromXml(cls, xml:et.ElementTree, ns:typing.Optional[dict]=None)->"ContentVersion":
		id = xml.find("Id",ns).text
		label = xml.find("LabelText",ns).text
		return cls(id, label)

@dataclasses.dataclass(frozen=True)
class EssenceDescriptor:
	"""A description of an essence"""

@dataclasses.dataclass(frozen=True)
class ContentMaturityRating:
	"""Content maturity rating and info"""
	agency:str
	rating:str
	audiences:typing.Optional[list[str]]=None

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict])->"ContentMaturityRating":
		"""Parse a ContentMaturtyRatingType from a ContentMaturityRatingList"""
		agency = xml.find("Agency",ns).text
		rating = xml.find("Rating",ns).text

		audience_list = list()
		for aud in xml.findall("Audience",ns):
			# TODO: Retain scope attribute?
			audience_list.append(aud.text)
		
		return cls(agency, rating, audience_list)

@dataclasses.dataclass(frozen=True)
class Locale:
	"""Localization info"""

	annotation:typing.Optional[str]=None
	languages:typing.Optional[list[str]]=None
	regions:typing.Optional[list[str]]=None
	content_maturity_ratings:typing.Optional[list[ContentMaturityRating]]=None

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Locale":
		"""Parse a LocaleType from a LocaleListType"""
		annotation = xsd_optional_string(xml.find("Annotation",ns))
		
		languages = []
		for lang_list in xml.findall("LanguageList",ns):
			for lang in lang_list.findall("Language",ns):
				languages.append(lang.text)
		
		regions = []
		for reg_list in xml.findall("RegionList",ns):
			for reg in reg_list.findall("Region",ns):
				regions.append(reg.text)

		ratings = []
		for r_list in xml.findall("ContentMaturityRatingList",ns):
			for rating in r_list.findall("ContentMaturityRating",ns):
				ratings.append(ContentMaturityRating.fromXml(rating, ns))
			
		return cls(annotation, languages, regions, ratings)
		


@dataclasses.dataclass(frozen=True)
class ExtensionProperty:
	"""Application extension"""
	# TODO: Spec loosely defines as lax processing, any namespace. Cool.
	# TODO: Decide upon a better implementation.
	raw_xml:str

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"ExtensionProperty":
		"""Capture an extention property from the list"""
		try:
			raw_xml = et.tostring(xml, encoding="unicode", method="xml").strip()
		except Exception as e:
			raw_xml = f"Unknown extension property: {e}"
		
		return cls(raw_xml)



# TODO: UNTESTED
@dataclasses.dataclass(frozen=True)
class Signer:
	"""Signing info"""
	raw_xml:str

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Signer":
		"""ds:KeyInfoType from XML"""

		ns.update({"ds":"http://www.w3.org/2000/09/xmldsig#"})

		try:
			raw_xml = et.tostring(xml, encoding="unicode", method="xml").strip()
		except Exception as e:
			raw_xml = f"Unknown signer type: {e}"
		return cls(raw_xml)

		

@dataclasses.dataclass(frozen=True)
class Signature:
	"""ds:Signature"""

	raw_xml:str

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Signer":
		"""ds:KeyInfoType from XML"""

		ns.update({"ds":"http://www.w3.org/2000/09/xmldsig#"})
		try:
			raw_xml = et.tostring(xml, encoding="unicode", method="xml").strip()
		except Exception as e:
			raw_xml = f"Unknown signature type: {e}"
		return cls(raw_xml)

@dataclasses.dataclass(frozen=True)
class EditRate:
	"""A rational edit rate"""
	
	edit_rate:tuple[int,int]

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "EditRate":
		"""Parse EditRateType from XML"""
		return cls(tuple(int(x) for x in xml.text.split(' ')))
	
	@property
	def decimal(self) -> float:
		"""Edit rate as a float"""
		return float(self.edit_rate[0]) / float(self.edit_rate[1])

	def __float__(self) -> float:
		return self.decimal
	
	def __str__(self) -> str:
		return str(round(self.decimal)) if self.decimal.is_integer() else str(round(self.decimal,2))
		
		
@dataclasses.dataclass(frozen=True)
class Cpl:
	"""An IMF Composition Playlist"""

	id:str
	issue_date:datetime.datetime
	title:str
	edit_rate:EditRate
	_segments:list["Segment"]
	
	annotation:str=""
	issuer:str=""
	creator:str=""
	content_originator:str=""
	content_kind:str=""
	runtime:str=""

	tc_start:timecode.Timecode=None
	content_versions:list["ContentVersion"]=None
	locales:list["Locale"]=None

	# Still need
	essence_descriptors:list["EssenceDescriptor"]=None
	extension_properties:list["ExtensionProperty"]=None
	signer:Signer=None
	signature:Signature=None

	@staticmethod
	def timecode_from_composition(xml:et.Element, ns:typing.Optional[dict]=None)->timecode.Timecode:
		"""Return a Timecode object from an XSD CompositionTimecodeType"""
		tc_addr = xml.find("TimecodeStartAddress",ns).text
		tc_rate = int(xml.find("TimecodeRate",ns).text)
		tc_drop = xml.find("TimecodeDropFrame",ns).text == 1
		return timecode.Timecode(tc_addr, tc_rate, timecode.Timecode.Mode.DF if tc_drop else timecode.Timecode.Mode.NDF)
	
	@classmethod
	def fromFile(cls, path:str) -> "Cpl":
		"""Parse an existing CPL"""
		file_cpl = et.parse(path)
		return cls.fromXml(file_cpl.getroot(), {"":"http://www.smpte-ra.org/schemas/2067-3/2016"})
	
	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Cpl":
		
		id = xml.find("Id",ns).text
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
		title = xml.find("ContentTitle",ns).text

		annotation = xsd_optional_string(xml.find("Annotation",ns))
		issuer = xsd_optional_string(xml.find("Issuer",ns))
		creator = xsd_optional_string(xml.find("Creator",ns))
		content_originator = xsd_optional_string(xml.find("ContentOriginator",ns))
		content_kind = xsd_optional_string(xml.find("ContentKind",ns))

		# Rate and timecode
		edit_rate = EditRate.fromXml(xml.find("EditRate",ns), ns)
		tc_start = cls.timecode_from_composition(xml.find("CompositionTimecode",ns),ns) if xml.find("CompositionTimecode",ns) is not None \
			else timecode.Timecode("00:00:00:00",float(edit_rate))

		# Runtime is just hh:mm:ss and not to be trusted
		runtime = xsd_optional_string(xml.find("TotalRuntime",ns))
		
		# ContentVersionList
		content_versions = list()
		if xml.find("ContentVersionList",ns) is not None:
			for cv in xml.find("ContentVersionList",ns).findall("ContentVersion",ns):
				content_versions.append(ContentVersion.fromXml(cv,ns))
		
		# Locales
		locale_list = list()
		for loc_list in xml.findall("LocaleList",ns):
			for locale in loc_list.findall("Locale",ns):
				locale_list.append(Locale.fromXml(locale,ns))
		
		# Application extensions
		extensions_list = []
		for prop_list in xml.findall("ExtensionProperties",ns):
			for prop in prop_list:
				extensions_list.append(ExtensionProperty.fromXml(prop,ns))
		
		# Signer
		# TODO: Fully implement
		if xml.find("Signer",ns) is not None:
			signer = Signer.fromXml(xml.find("Signer",ns),ns)
		else:
			signer=None
		
		# Signature
		# TODO: Fully implement
		if xml.find("ds:Signature",{"ds":"http://www.w3.org/2000/09/xmldsig#"}) is not None:
			signature = Signature.fromXml(xml.find("ds:Signature",{"ds":"http://www.w3.org/2000/09/xmldsig#"}), ns)
		else:
			signature=None
		
		# TODO: Signer and signature must be either both present, or both omitted
		# TODO: Do a check real good ok
		
		# Segments!
		segment_list = list()
		for segment in xml.find("SegmentList",ns):
			segment_list.append(Segment.fromXml(segment,ns))


		return cls(
			id=id,
			issue_date=issue_date,
			title=title,
			edit_rate=edit_rate,
			_segments=segment_list,
			annotation=annotation,
			issuer=issuer,
			creator=creator,
			content_originator=content_originator,
			content_kind=content_kind,
			tc_start=tc_start,
			runtime=runtime,
			content_versions=content_versions,
			locales=locale_list,
			extension_properties=extensions_list,
			signer=signer,
			signature=signature
		)
	
	@property
	def segments(self) -> typing.Iterator["Segment"]:
		return iter(self._segments)
	
	@property
	def sequences(self) -> typing.Iterator["Sequence"]:
		for seg in self.segments:
			for seq in seg.sequences:
				yield seq
	
	@property
	def resources(self) -> typing.Iterator["Resource"]:
		for seq in self.sequences:
			for res in seq.resources:
				yield res