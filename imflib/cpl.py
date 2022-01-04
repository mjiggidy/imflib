from abc import abstractclassmethod
import xml.etree.ElementTree as et
import pathlib, sys, dataclasses, typing, re
from posttools import timecode

pat_nsextract = re.compile(r'^\{(.+)\}')

@dataclasses.dataclass
class Resource:
	"""A resource within a sequence"""

	id:str
	file_id:str
	_edit_rate:typing.Tuple[int]
	_start_frame:int
	_duration:int
	
	@abstractclassmethod
	def fromXml(cls, resource, ns) -> "Resource":
		id = resource.find("cpl:Id", ns).text
		file_id = resource.find("cpl:TrackFileId", ns).text
		edit_rate = tuple([int(x) for x in resource.find("cpl:EditRate",ns).text.split(' ')])
		start_frame = int(resource.find("cpl:EntryPoint", ns).text)
		duration = int(resource.find("cpl:SourceDuration", ns).text)
		
		return cls(id, file_id, edit_rate, start_frame, duration)

	
	@property
	def edit_rate(self) -> float:
		return self._edit_rate[0] / self._edit_rate[1]
	


class ImageResource(Resource):
	"""A main image resource"""
	@property
	def duration(self) -> timecode.Timecode:
		return timecode.Timecode(self._duration, self.edit_rate)
	
	@property
	def in_point(self) -> timecode.Timecode:
		return timecode.Timecode(self._start_frame, self.edit_rate)
	
	@property
	def out_point(self) -> timecode.Timecode:
		return self.in_point + self.duration

class AudioResource(Resource):
	"""A main audio resource"""


@dataclasses.dataclass
class Sequence:
	"""A sequence within a segment"""
	id:str
	resources:typing.List[Resource]

	@abstractclassmethod
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

class Cpl:
	"""An IMF Composition Playlist"""

	def __init__(self):
		self._title      = str()
		self._segments   = list()
		self._namespaces = dict()
		self._editrate   = tuple()
		self._tc_start   = None
	
	@classmethod
	def fromFile(cls, path:str) -> "Cpl":
		"""Parse an existing CPL"""

		cpl = cls()

		file_cpl = et.parse(path)
		root = file_cpl.getroot()

		# Get the CPL namespace
		cpl.addNamespace("cpl",pat_nsextract.match(root.tag).group(1))
		cpl.setEditRate(*[int(x) for x in root.find("cpl:EditRate",cpl.namespaces).text.split(' ')])

		# Get title
		cpl.setTitle(root.find("cpl:ContentTitle", cpl.namespaces).text)

		# Get the start timecode
		tc_info = root.find("cpl:CompositionTimecode", cpl.namespaces)
		tc_drop = tc_info.find("cpl:TimecodeDropFrame",cpl.namespaces).text == '1'
		tc_rate = int(tc_info.find("cpl:TimecodeRate",cpl.namespaces).text)
		tc_addr = tc_info.find("cpl:TimecodeStartAddress",cpl.namespaces).text

		cpl.setStartTimecode(timecode.Timecode(tc_addr, rate=tc_rate, mode=timecode.Timecode.Mode.DF if tc_drop else timecode.Timecode.Mode.NDF))

		for segment in root.find("cpl:SegmentList", cpl.namespaces):
			seg = Segment.fromXmlSegment(segment, cpl.namespaces)
			cpl.addSegement(seg)

		return cpl		

	@property
	def namespaces(self) -> dict:
		"""Known namespaces in the CPL"""
		return self._namespaces

	@property
	def title(self) -> str:
		"""Title of the CPL"""
		return self._title
	
	@property
	def edit_rate(self) -> float:
		"""Calculate the edit rate"""
		return self._editrate[0] / self._editrate[1]
	
	@property
	def tc_start(self) -> timecode.Timecode:
		"""The start timecode of the CPL"""
		return self._tc_start

	@property
	def segments(self) -> typing.List[Segment]:
		return self._segments
	
	def addNamespace(self, name:str, uri:str):
		"""Add a known namespace to the zeitgeist"""
		if name in self._namespaces:
			raise KeyError(f"Namespace {name} already exists as {self._namespaces.get('name')}")	
		self._namespaces.update({name: uri})
	
	def setTitle(self, title:str):
		"""Set the title of the CPL"""
		self._title = title
	
	def setEditRate(self, numerator:int, denominator:int):
		"""Set the CPL edit rate"""
		self._editrate = (numerator, denominator)
	
	def setStartTimecode(self, tc_start:timecode.Timecode):
		"""Set the CPL start timecode"""
		self._tc_start = tc_start
	
	def addSegement(self, segment:Segment):
		"""Add a segment to the CPL"""
		self._segments.append(segment)
