import xml.etree.ElementTree as et
import dataclasses, typing, re, abc, datetime
from posttools import timecode
from . import pkl
from imflib import xsd_datetime_to_datetime

pat_nsextract = re.compile(r'^\{(.+)\}')

@dataclasses.dataclass
class Resource(abc.ABC):
	"""A resource within a sequence"""

	id:str
	file_id:str
	_edit_rate:typing.Tuple[int]
	_start_frame:int
	_duration:int
	_asset:pkl.Asset
	
	@classmethod
	def fromXml(cls, resource, ns) -> "Resource":
		id = resource.find("cpl:Id", ns).text
		file_id = resource.find("cpl:TrackFileId", ns).text

		res_edit_rate = resource.find("cpl:EditRate",ns)
		# FIXME: Quick n dirty default values
		edit_rate = tuple([int(x) for x in res_edit_rate.text.split(' ')]) if res_edit_rate is not None else (24000, 1001,)
		

		start_frame = int(resource.find("cpl:EntryPoint", ns).text)
		duration = int(resource.find("cpl:SourceDuration", ns).text)
		
		return cls(id, file_id, edit_rate, start_frame, duration, None)

	@abc.abstractproperty
	def edit_units(self) -> str:
		"""Units used to express the edit rate"""
	
	@property
	def edit_rate(self) -> float:
		return self._edit_rate[0] / self._edit_rate[1]
	
	@property
	def edit_rate_formatted(self) -> str:
		"""Edit rate formatted nicely as a string"""
		rate = int(self.edit_rate) if self.edit_rate.is_integer() else round(self.edit_rate, 2)
		return f"{rate} {self.edit_units}"
	
	@property
	def in_point(self) -> timecode.Timecode:
		return timecode.Timecode(self._start_frame, self.edit_rate)
	
	@property
	def out_point(self) -> timecode.Timecode:
		return self.in_point + self.duration

	@property
	def duration(self) -> timecode.Timecode:
		return timecode.Timecode(self._duration, self.edit_rate)
	
	@property
	def file_asset(self) -> pkl.Asset:
		"""Get the file asset associated with this resource"""
		return self._asset or None
	
	def setAsset(self, asset:pkl.Asset):
		"""Set the file asset associated with this resource"""
		self._asset = asset

class ImageResource(Resource):
	"""A main image resource"""

	@property
	def edit_units(self) -> str:
		return "fps"
	

class AudioResource(Resource):
	"""A main audio resource"""

	@property
	def edit_units(self) -> str:
		return "Hz"

@dataclasses.dataclass
class Sequence:
	"""A sequence within a segment"""
	id:str
	resources:typing.List[Resource]

	@classmethod
	def fromXml(cls, sequence, ns) -> "Sequence":
		id = sequence.find("cpl:Id",ns).text
		resources = list()

		seq = cls(id, resources)

		for resource in sequence.find("cpl:ResourceList",ns):
			if isinstance(seq, MainImageSequence):
				resources.append(ImageResource.fromXml(resource, ns))
			elif isinstance(seq, MainAudioSequence):
				resources.append(AudioResource.fromXml(resource, ns))

		return cls(id, resources)

class MainImageSequence(Sequence):
	"""Main image sequence of a segment"""

class MainAudioSequence(Sequence):
	"""Main audio sequence of a segment"""


@dataclasses.dataclass
class Segment:
	"""A CPL segment"""
	id:str
	sequences:typing.List[Sequence]

	@classmethod
	def fromXmlSegment(cls, xml_segment:et.Element, ns:dict) -> "Segment":

		seg = cls(xml_segment.find("cpl:Id",ns).text, list())

		for sequence in xml_segment.find("cpl:SequenceList", ns):
			# Try to collect any new namespaces
			try:
				ns.update({"cc": pat_nsextract.match(sequence.tag).group(1)})
			except KeyError:
				pass

			if "MainImageSequence" in sequence.tag:
				seg.sequences.append(MainImageSequence.fromXml(sequence, ns))
		
			elif "MainAudioSequence" in sequence.tag:
				seg.sequences.append(MainAudioSequence.fromXml(sequence, ns))
			
		return seg
	
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

	annotation_text:typing.Optional[str]=None
	languages:typing.Optional[list[str]]=None
	regions:typing.Optional[list[str]]=None
	content_maturity_ratings:typing.Optional[list[ContentMaturityRating]]=None

	@classmethod
	def fromXml(cls, xml:et.Element, ns:typing.Optional[dict]=None)->"Locale":
		"""Parse a LocaleType from a LocaleListType"""
		annotation_text = xml.find("Annotation",ns).text if xml.find("Annotation",ns) else ""
		
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
			
		return cls(annotation_text, languages, regions, ratings)
		


@dataclasses.dataclass(frozen=True)
class ExtensionProperty:
	"""Application extension"""

@dataclasses.dataclass(frozen=True)
class KeyInfo:
	"""Signing info"""

@dataclasses.dataclass(frozen=True)
class Signature:
	"""ds:Signature"""
		
@dataclasses.dataclass(frozen=True)
class Cpl:
	"""An IMF Composition Playlist"""

	id:str
	issue_date:datetime.datetime
	title:str
	edit_rate:tuple[int,int]
	segments:list["Segment"]
	
	annotation_text:str=""
	issuer:str=""
	creator:str=""
	content_originator:str=""
	content_kind:str=""
	runtime:str=""

	tc_start:timecode.Timecode=None
	content_versions:list["ContentVersion"]=None
	locales:list["Locale"]=None

	essence_descriptors:list["EssenceDescriptor"]=None
	extension_properties:list["ExtensionProperty"]=None
	signer:KeyInfo=None
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

		annotation_text = xml.find("Annotation",ns).text if xml.find("Annotation",ns) is not None else ""
		issuer = xml.find("Issuer",ns).text if xml.find("Issuer",ns) is not None else ""
		creator = xml.find("Creator",ns).text if xml.find("Creator",ns) is not None else ""
		content_originator = xml.find("ContentOriginator",ns).text if xml.find("ContentOriginator",ns) is not None else ""
		content_kind = xml.find("ContentKind",ns).text if xml.find("ContentKind",ns) is not None else ""

		# Rate and timecode
		edit_rate = tuple(int(x) for x in xml.find("EditRate",ns).text.split(' '))
		tc_start = cls.timecode_from_composition(xml.find("CompositionTimecode",ns),ns) if xml.find("CompositionTimecode",ns) is not None \
			else timecode.Timecode("00:00:00:00",float(edit_rate[0])/float(edit_rate[1]))

		# Runtime is just hh:mm:ss and not to be trusted
		runtime = xml.find("TotalRuntime",ns).text if xml.find("TotalRuntime",ns) is not None else ""
		
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


		return cls(
			id=id,
			issue_date=issue_date,
			title=title,
			edit_rate=edit_rate,
			segments=[],
			annotation_text=annotation_text,
			issuer=issuer,
			creator=creator,
			content_originator=content_originator,
			content_kind=content_kind,

			tc_start=tc_start,
			runtime=runtime,

			content_versions=content_versions,
			locales=locale_list
		)


		for segment in root.find("cpl:SegmentList", cpl.namespaces):
			seg = Segment.fromXmlSegment(segment, cpl.namespaces)
			cpl.addSegement(seg)

		return cpl		
#
#	@property
#	def namespaces(self) -> dict:
#		"""Known namespaces in the CPL"""
#		return self._namespaces
#
#	@property
#	def title(self) -> str:
#		"""Title of the CPL"""
#		return self._title
#	
#	@property
#	def edit_rate(self) -> float:
#		"""Calculate the edit rate"""
#		return self._editrate[0] / self._editrate[1]
#	
#	@property
#	def tc_start(self) -> timecode.Timecode:
#		"""The start timecode of the CPL"""
#		return self._tc_start
#
#	@property
#	def segments(self) -> typing.List[Segment]:
#		return self._segments
#	
#	@property
#	def resources(self) -> typing.List[Resource]:
#		reslist = list()
#		for seg in self.segments:
#			reslist.extend(seg.resources)
#		return reslist
#	
#	def addNamespace(self, name:str, uri:str):
#		"""Add a known namespace to the zeitgeist"""
#		if name in self._namespaces:
#			raise KeyError(f"Namespace {name} already exists as {self._namespaces.get('name')}")	
#		self._namespaces.update({name: uri})
#	
#	def setTitle(self, title:str):
#		"""Set the title of the CPL"""
#		self._title = title
#	
#	def setEditRate(self, numerator:int, denominator:int):
#		"""Set the CPL edit rate"""
#		self._editrate = (numerator, denominator)
#	
#	def setStartTimecode(self, tc_start:timecode.Timecode):
#		"""Set the CPL start timecode"""
#		self._tc_start = tc_start
#	
#	def addSegement(self, segment:Segment):
#		"""Add a segment to the CPL"""
#		self._segments.append(segment)
#