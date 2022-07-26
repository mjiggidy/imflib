import xml.etree.ElementTree as et
import dataclasses, typing, re, abc, datetime, uuid
from posttools import timecode
from imflib import xsd_datetime_to_datetime, xsd_optional_string, xsd_optional_integer, xsd_optional_bool, xsd_optional_usertext, xsd_optional_security, UserText, Security

pat_nsextract = re.compile(r'^\{(?P<uri>.+)\}(?P<name>[a-z0-9]+)',re.I)

@dataclasses.dataclass(frozen=True)
class Resource(abc.ABC):
	"""A BaseResource XSD within a sequence"""

	id:str
	intrinsic_duration:int
	
	annotation:typing.Optional[str]
	edit_rate:typing.Optional["EditRate"]
	entry_point:typing.Optional[int]
	source_duration:typing.Optional[int]
	repeat_count:typing.Optional[int]

	# References
	_src_sequence:typing.Optional["Sequence"]
	_src_offset:int

	@property
	def duration(self) -> int:
		"""Duration in frames for now"""
		return self.source_duration  + (self.source_duration * self.repeat_count)
	
	@property
	def edit_range(self) -> timecode.TimecodeRange:
		"""In/out point of subclip"""
		rate = float(self.edit_rate or self._src_sequence._src_segment._src_cpl.edit_rate)
		tc_start = timecode.Timecode(self.entry_point, rate)
		duration = timecode.Timecode(self.source_duration, rate)
		return timecode.TimecodeRange(
			start=tc_start,
			duration=duration
		)

	@property
	def timecode_range(self) -> timecode.TimecodeRange:
		"""Timecode range relative to CPL"""
		tc_start = self._src_sequence.timecode_range.start + self._src_offset
		tc_duration = timecode.Timecode(self.duration, float(self.edit_rate or tc_start.rate)).resample(tc_start.rate)
		return timecode.TimecodeRange(
			start    = tc_start,
			duration = tc_duration
		)

@dataclasses.dataclass(frozen=True)
class TrackFileResource(Resource):
	"""A file-based resource"""
	source_encoding:str
	track_file_id:str

	key_id:typing.Optional[str]
	hash:typing.Optional[str]
	hash_algorithm:typing.Optional[str]

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"ImageResource":

		# BaseResource
		id = xml.find("Id",ns).text
		intrinsic_duration = int(xml.find("IntrinsicDuration",ns).text)
		
		# BaseResource Optional
		annotation = xsd_optional_string(xml.find("Annotation",ns))
		edit_rate = EditRate.from_xml(xml.find("EditRate",ns), ns) if xml.find("EditRate",ns) is not None else None
		entry_point = xsd_optional_integer(xml.find("EntryPoint",ns))
		source_duration = xsd_optional_integer(xml.find("SourceDuration",ns))
		repeat_count = xsd_optional_integer(xml.find("RepeatCount",ns), 0)

		# TrackFileResource
		source_encoding = xml.find("SourceEncoding",ns).text
		track_file_id = xml.find("TrackFileId",ns).text
		
		# TrackResource Optional
		key_id = xsd_optional_string(xml.find("KeyId",ns))
		hash = xsd_optional_string(xml.find("Hash",ns))
		hash_algorithm = xsd_optional_string(xml.find("HashAlgorithm",ns))


		return cls(
			id=id,
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
			hash_algorithm=hash_algorithm,
			_src_sequence=None,
			_src_offset=0
		)

@dataclasses.dataclass(frozen=True)
class ImageResource(TrackFileResource):
	"""A main image resource"""

	edit_units:str = "fps"

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "ImageResource":
		res = super().from_xml(xml,ns)
		# I am surprised this just works
		return res
	
@dataclasses.dataclass(frozen=True)
class AudioResource(TrackFileResource):
	"""A main audio resource"""

	edit_units:str = "Hz"

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "AudioResource":
		res = super().from_xml(xml,ns)
		return res

# TODO: Markers are untested (no samples available)
@dataclasses.dataclass(frozen=True)
class MarkerResource(Resource):
	"""A CPL Marker"""

	label:str
	scope:str
	offset:int

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "MarkerResource":
		
		# BaseResource
		id = xml.find("Id",ns).text
		intrinsic_duration = int(xml.find("IntrinsicDuration",ns).text)

		# BaseResource Optional
		annotation = xsd_optional_string(xml.find("Annotation",ns))
		edit_rate = EditRate.from_xml(xml.find("EditRate",ns), ns) if xml.find("EditRate",ns) is not None else None
		entry_point = xsd_optional_integer(xml.find("EntryPoint",ns))
		source_duration = xsd_optional_integer(xml.find("SourceDuration",ns))
		repeat_count = xsd_optional_integer(xml.find("RepeatCount",ns), 0)

		label = xml.find("Label",ns).text
		scope = xsd_optional_string(xml.find("Label",ns).attrib("scope"), "http://www.smpte-ra.org/schemas/2067-3/2013#standard-markers")
		offset = int(xml.find("Offset",ns).text)

		return cls(
			id=id,
			intrinsic_duration=intrinsic_duration,
			annotation=annotation,
			edit_rate=edit_rate,
			entry_point=entry_point,
			source_duration=source_duration,
			repeat_count=repeat_count,
			label=label,
			scope=scope,
			offset=offset,
			_src_sequence=None,
			_src_offset=0
		)


@dataclasses.dataclass(frozen=True)
class Sequence:
	"""A sequence within a segment"""
	id:str
	track_id:str
	_resources:typing.List[Resource]

	# References
	_src_segment:typing.Optional["Segment"]=None
	_src_offset:int=0

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "Sequence":
		"""Parse from XML"""

		if xml.tag.endswith("MainImageSequence"):
			return MainImageSequence.from_xml(xml, ns)
		
		elif xml.tag.endswith("MainAudioSequence"):
			return MainAudioSequence.from_xml(xml, ns)
		
		elif xml.tag.endswith("MarkerSequence"):
			return MarkerSequence.from_xml(xml, ns)
		
		# TODO: Implement additional
		else:
			raise NotImplementedError(f"Unknown/unsupported/scary sequence type: {xml.tag}")
	
	@property
	def resources(self) -> typing.Iterator["Resource"]:
		rel_offset = 0
		for res in self._resources:
			yield dataclasses.replace(
				res,
				_src_sequence = self,
				_src_offset   = rel_offset
			)
			rel_offset += res.duration
	
	@property
	def duration(self) -> int:
		"""Duration in frames for now"""
		# The timeline of a Sequence shall consist of the concatenation, without gaps, of the timeline of all its Resources in the order they appear in the ResourceList element
		return sum(res.duration for res in self.resources)

	@property
	def timecode_range(self) -> timecode.TimecodeRange:
		"""Timecode range relative to CPL"""
		tc_start = self._src_segment.timecode_range.start
		tc_duration = timecode.Timecode(self.duration, tc_start.rate, tc_start.mode)
		return timecode.TimecodeRange(
			start    = tc_start,
			duration = tc_duration
		)


class MainImageSequence(Sequence):
	"""An XSD MainImageSequenceType from IMF Core Constraints"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "MainImageSequence":
		"""Parse from XML"""
		
		id = xml.find("Id",ns).text
		track_id = xml.find("TrackId",ns).text
		
		resource_list = list()
		for resource in xml.find("ResourceList",ns).findall("Resource",ns):
			resource_list.append(ImageResource.from_xml(resource, ns))

		return cls(id=id, track_id=track_id, _resources=resource_list)

class MainAudioSequence(Sequence):
	"""Main audio sequence of a segment"""
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "MainImageSequence":
		"""Parse from XML"""
		id = xml.find("Id",ns).text
		track_id = xml.find("TrackId",ns).text
		
		resource_list = list()
		for resource in xml.find("ResourceList",ns).findall("Resource",ns):
			resource_list.append(AudioResource.from_xml(resource, ns))

		return cls(id=id, track_id=track_id, _resources=resource_list)

# TODO: MarkerSequence is untested
class MarkerSequence(Sequence):
	"""Marker sequence"""
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "MarkerSequence":
		"""Parse from """
		id = xml.find("Id",ns).text
		track_id = xml.find("TrackId",ns).text
		
		resource_list = list()
		for resource in xml.find("ResourceList",ns).findall("Resource",ns):
			resource_list.append(MarkerResource.from_xml(resource, ns))

		return cls(id=id, track_id=track_id, _resources=resource_list)

@dataclasses.dataclass(frozen=True)
class Segment:
	"""A CPL segment"""
	id:str
	_sequences:typing.List[Sequence]
	annotation:str=""

	# References
	_src_cpl:typing.Optional["Cpl"]=None
	_src_offset:int=0

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]) -> "Segment":

		id = xml.find("Id",ns).text
		annotation = xsd_optional_string(xml.find("Annotation",ns))

		sequence_list = list()

		for sequence in xml.find("SequenceList", ns):
			sequence_list.append(Sequence.from_xml(sequence,ns))

		return cls(
			id=id,
			_sequences=sequence_list,
			annotation=annotation
		)
	
	@property
	def resources(self) -> typing.List[Resource]:
		reslist = list()
		for seq in self.sequences:
			reslist.extend(seq.resources)
		return reslist
	
	@property
	def sequences(self) -> typing.Iterable["Sequence"]:
		rel_offset = 0
		for seq in self._sequences:
			yield dataclasses.replace(
				seq,
				_src_segment = self,
				_src_offset  = rel_offset
			)
			rel_offset += seq.duration
	
	@property
	def duration(self) -> int:
		"""Duration in frames for now"""
		#The duration of the Segment shall be equal to the duration of its Sequences and all Sequences within Segment shall have the same duration.
		return self._sequences[0].duration if self._sequences else 0
	
	@property
	def timecode_range(self) -> timecode.TimecodeRange:
		"""Timecode range relative to CPL"""
		tc_start = self._src_cpl.timecode_range.start + self._src_offset
		tc_duration = timecode.Timecode(self.duration, tc_start.rate, tc_start.mode)
		return timecode.TimecodeRange(
			start    = tc_start,
			duration = tc_duration
		)



@dataclasses.dataclass(frozen=True)
class ContentVersion:
	"""A content version"""

	id:str
	label:str
	additional:typing.Any=None	# TODO: Investigate handling of xs:any tags, ambiguous in spec

	@classmethod
	def from_xml(cls, xml:et.ElementTree, ns:typing.Optional[dict]=None)->"ContentVersion":
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
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict])->"ContentMaturityRating":
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
	"""Locale-specific information"""

	languages:list[str]=dataclasses.field(default_factory=list)
	"""RFC 5646 language tags of the audiences in this locale"""

	regions:list[str]=dataclasses.field(default_factory=list)
	"""RFC 5646 region subtags in this locale"""

	content_maturity_ratings:list[ContentMaturityRating]=dataclasses.field(default_factory=list)
	"""Content maturity ratings for this locale"""

	annotation:typing.Optional[UserText]=None
	"""Description of this locale"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "Locale":
		"""Parse a LocaleType from a LocaleListType"""

		annotation = xsd_optional_usertext(xml.find("Annotation",ns))
		
		languages = list()
		ll = xml.find("LanguageList",ns)
		if ll:
			for lang in ll:
				languages.append(lang.text)
		
		regions = list()
		rl = xml.find("RegionList",ns)
		if rl:
			for reg in rl:
				regions.append(reg.text)

		ratings = []
		ral = xml.find("ContentMaturityRatingList",ns)
		if ral:
			for rating in ral:
				ratings.append(ContentMaturityRating.from_xml(rating, ns))
			
		return cls(
			annotation=annotation,
			languages=languages,
			regions=regions,
			content_maturity_ratings=ratings
		)
		


@dataclasses.dataclass(frozen=True)
class ExtensionProperty:
	"""Application extension"""
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



# TODO: UNTESTED
@dataclasses.dataclass(frozen=True)
class Signer:
	"""Signing info"""
	raw_xml:str

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Signer":
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
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Signer":
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
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "EditRate":
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
class ContentKind:
	"""The kind of content undelying the composition"""

	kind:str
	"""The kind of content"""
	# TODO: Validate default against allowed types?

	scope:typing.Optional[str]="http://www.smpte-ra.org/schemas/2067-3/2013#content-kind"
	"""The defined set of possible kinds"""

	def __str__(self) -> str:
		return self.kind
	
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None) -> "ContentKind":
		"""Parse ContentKind from XML"""

		return cls(
			kind=xml.text,
			scope=xml.attrib.get("scope")
		)
		
@dataclasses.dataclass(frozen=True)
class Cpl:
	"""An IMF Composition Playlist"""

	id:uuid.UUID
	"""Unique identifier for this CPL encoded as a urn:UUID [RFC 4122]"""

	issue_date:datetime.datetime
	"""Datetime this asset map was issued"""

	title:UserText
	"""The title of the content in this CPL"""

	edit_rate:EditRate
	"""The granularity of time-related parameters used in this CPL"""

	_segments:list["Segment"]
	
	annotation:typing.Optional[UserText]=None
	"""Optional description of this CPL"""

	issuer:typing.Optional[UserText]=None
	"""The person or company that issued this CPL"""

	creator:typing.Optional[UserText]=None
	"""The facility or system that created this CPL"""

	content_originator:typing.Optional[UserText]=None
	"""The person or company that produced the content used in this CPL"""

	content_kind:typing.Optional[ContentKind]=None
	"""The kind of work represented by this CPL"""

	total_runtime:typing.Optional[datetime.timedelta]=None
	"""The approximate runtime of the content in this CPL, for informational purposes only"""

	tc_start:typing.Optional[timecode.Timecode]=None
	"""The starting timecode of this CPL"""

	content_versions:set["ContentVersion"]=dataclasses.field(default_factory=set)
	"""The specific version or revision of the content in this CPL"""
	#TODO: "No two ContentVersion elements shall have identical Id elements."
	#TODO: "Two Composition Playlist instances shall be assumed to refer to the same 
	# content if they have in common at least one Id element of a ContentVersion element."
	#TODO: `dict` instead?

	locales:list["Locale"]=dataclasses.field(default_factory=list)
	"""The intended audiences for this CPL"""

	# Still need
	essence_descriptors:list["EssenceDescriptor"]=dataclasses.field(default_factory=list)
	"""Descriptors intended for scheduling and tracking content referenced by this CPL"""

	extension_properties:list["ExtensionProperty"]=dataclasses.field(default_factory=list)
	"""Additional metadata describing this CPL"""

	security:typing.Optional[Security]=None
	"""XML signer and signature"""

	@staticmethod
	def xsd_optional_compositiontimecode(xml:et.Element, ns:typing.Optional[dict]=None, default:typing.Optional[timecode.Timecode]=None) -> timecode.Timecode:
		"""Return a Timecode object from an XSD CompositionTimecodeType"""

		if xml is None:
			return default

		tc_addr = xml.find("TimecodeStartAddress",ns).text
		tc_rate = int(xml.find("TimecodeRate",ns).text)
		tc_drop = xsd_optional_bool(xml.find("TimecodeDropFrame",ns))
		return timecode.Timecode(tc_addr, tc_rate, timecode.Timecode.Mode.DF if tc_drop else timecode.Timecode.Mode.NDF)
	
	@staticmethod
	def xsd_optional_runtime(xml:et.Element, ns:typing.Optional[dict]=None, default:typing.Optional[datetime.timedelta]=None) -> datetime.timedelta:
		"""Return a `datetime.timedelta` object based on a given runtime"""
		if xml is None:
			return default
		
		runtime = [int(x) for x in xml.text.split(":")]
		return datetime.timedelta(hours=int(runtime[0], minutes=runtime[1], seconds=runtime[2]))
	
	@classmethod
	def from_file(cls, path:str) -> "Cpl":
		"""Parse an existing CPL from a given file path."""
		file_cpl = et.parse(path)
		return cls.from_xml(file_cpl.getroot(), {"":"http://www.smpte-ra.org/schemas/2067-3/2016"})
	
	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Cpl":
		"""
		Parse an existing CPL from a given root XMLElementTree Element
		Intended to be called from Cpl.from_file(), but you do you.
		"""
		
		id = uuid.UUID(xml.find("Id",ns).text)
		issue_date = xsd_datetime_to_datetime(xml.find("IssueDate",ns).text)
		title = xml.find("ContentTitle",ns).text

		annotation = xsd_optional_usertext(xml.find("Annotation",ns))
		issuer = xsd_optional_usertext(xml.find("Issuer",ns))
		creator = xsd_optional_usertext(xml.find("Creator",ns))
		content_originator = xsd_optional_usertext(xml.find("ContentOriginator",ns))
		content_kind = xsd_optional_usertext(xml.find("ContentKind",ns))

		# Rate and timecode
		edit_rate = EditRate.from_xml(xml.find("EditRate",ns), ns)
		tc_start = cls.xsd_optional_compositiontimecode(xml.find("CompositionTimecode",ns),ns)

		# Runtime is just hh:mm:ss and not to be trusted
		runtime = cls.xsd_optional_runtime(xml.find("TotalRuntime",ns))
		
		# ContentVersionList
		content_versions = list()
		cvl = xml.find("ContentVersionList",ns)
		if cvl:
			for cv in cvl:
				content_versions.append(ContentVersion.from_xml(cv,ns))
		
		# Locales
		locale_list = list()
		ll = xml.find("LocaleList",ns)
		if ll:
			for locale in ll:
				locale_list.append(Locale.from_xml(locale,ns))
		
		# Extensions
		extensions_list = list()
		el = xml.find("ExtensionProperties",ns)
		if el:
			for prop in el:
				extensions_list.append(ExtensionProperty.from_xml(prop,ns))

		# Signer and signature
		# TODO: Definitely needs testing
		security = xsd_optional_security(
			xml_signer=xml.find("Signer",ns),
			xml_signature=xml.find("ds:Signature",{"ds":"http://www.w3.org/2000/09/xmldsig#"})
		)

		# Segments!
		segment_list = [Segment.from_xml(segment,ns) for segment in xml.find("SegmentList",ns)]

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
			total_runtime=runtime,
			content_versions=content_versions,
			locales=locale_list,
			extension_properties=extensions_list,
			security=security
		)
	
	@property
	def segments(self) -> typing.Iterator["Segment"]:
		for seg in self._segments:
			rel_offset = 0
			yield dataclasses.replace(
				seg,
				_src_cpl    =self,
				_src_offset = rel_offset
			)
			rel_offset += seg.duration
	
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
	
	@property
	def duration(self) -> int:
		"""Duration in frames for now"""
		return sum(seg.duration for seg in self.segments)
	
	@property
	def timecode_range(self) -> timecode.TimecodeRange:
		"""Timecode range of the CPL"""
		return timecode.TimecodeRange(
			start    = self.tc_start,
			duration = timecode.Timecode(self.duration, float(self.edit_rate))
		)
