"""`Common Image Pixel Color Encoding Schemes` and related classes

Based on st-2067-102-2017: https://ieeexplore.ieee.org/document/8058111
"""

import xml.etree.ElementTree as et
import dataclasses, typing, abc

@dataclasses.dataclass(frozen=True)
class ColorEncoding(abc.ABC):
	"""Abstract base class for color encoding schemes"""

	@staticmethod
	def xsd_validate_color_values(vals:typing.Iterable, min_val:typing.Union[int,float], max_val:typing.Union[int,float], count:int, val_type:type):
		"""Generic function for parsing these color value lists"""

		if len(vals) != count:
			raise ValueError(f"Must contain {count} values")
		if any(val<min_val or val>max_val for val in vals):
			raise ValueError(f"Values must be between {min_val} and {max_val}, inclusive")
		if any(type(val) is not val_type for val in vals):
			raise ValueError(f"Values mut be of type {val_type.__name__}")

# Rec709 Color Encodings
@dataclasses.dataclass(frozen=True)
class Rec709RGB8(ColorEncoding):
	"""8-bit RGB components with COLOR.3 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 255, 3, int)

@dataclasses.dataclass(frozen=True)
class Rec709RGB10(ColorEncoding):
	"""10-bit RGB components with COLOR.3 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Rec709RGB10(ColorEncoding):
	"""10-bit RGB components with COLOR.3 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)


@dataclasses.dataclass(frozen=True)
class Rec709FullRGB10(ColorEncoding):
	"""10-bit full-range RGB components with COLOR.3 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Rec709YCbCr8(ColorEncoding):
	"""8-bit YCbCr components with COLOR.3 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 255, 3, int)

@dataclasses.dataclass(frozen=True)
class Rec709YCbCr10(ColorEncoding):
	"""10-bit YCbCr components with COLOR.3 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 1023, 3, int)

# Extended-Gamut YCbCr

@dataclasses.dataclass(frozen=True)
class XvYCCYCbCr8(ColorEncoding):
	"""8-bit Extended-Gamut YCbCr components with COLOR.4 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 255, 3, int)

@dataclasses.dataclass(frozen=True)
class XvYCCYCbCr10(ColorEncoding):
	"""10-bit Extended-Gamut YCbCr components with COLOR.4 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 1023, 3, int)

# Rec2020

@dataclasses.dataclass(frozen=True)
class Rec2020YCbCr10(ColorEncoding):
	"""10-bit Rec2020 YCbCr components with COLOR.5 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Rec2020YCbCr12(ColorEncoding):
	"""12-bit Rec2020 YCbCr components with COLOR.5 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 4095, 3, int)

@dataclasses.dataclass(frozen=True)
class Rec2020RGB10(ColorEncoding):
	"""10-bit RGB components with COLOR.5 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)


@dataclasses.dataclass(frozen=True)
class Rec2020RGB12(ColorEncoding):
	"""10-bit RGB components with COLOR.5 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 4095, 3, int)


@dataclasses.dataclass(frozen=True)
class Rec2020FullRGB10(ColorEncoding):
	"""10-bit full-range RGB components with COLOR.5 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Rec2020FullRGB12(ColorEncoding):
	"""12-bit full-range RGB components with COLOR.5 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 4095, 3, int)

# COLOR6

@dataclasses.dataclass(frozen=True)
class Color6RGB10(ColorEncoding):
	"""10-bit RGB components with COLOR.6 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Color6FullRGB10(ColorEncoding):
	"""10-bit full-range RGB components with COLOR.6 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Color6RGB12(ColorEncoding):
	"""12-bit RGB components with COLOR.6 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 4095, 3, int)

@dataclasses.dataclass(frozen=True)
class Color6FullRGB12(ColorEncoding):
	"""12-bit full-range RGB components with COLOR.6 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 4095, 3, int)

@dataclasses.dataclass(frozen=True)
class Color6RGB16(ColorEncoding):
	"""16-bit RGB components with COLOR.6 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 65535, 3, int)

@dataclasses.dataclass(frozen=True)
class Color6FullRGB16(ColorEncoding):
	"""16-bit full-range RGB components with COLOR.6 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 65535, 3, int)

# COLOR7

@dataclasses.dataclass(frozen=True)
class Color7YCbCr10(ColorEncoding):
	"""10-bit YCbCr components with COLOR.7 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7YCbCr12(ColorEncoding):
	"""12-bit YCbCr components with COLOR.7 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 4095, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7YCbCr16(ColorEncoding):
	"""16-bit YCbCr components with COLOR.7 colorimetry and QE.1 quanitization"""

	y:int
	"""Luminance"""

	cb:int
	"""Chroma B"""
	
	cr:int
	"""Chroma R"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		y,cb,cr = (int(val) for val in xml.text.split())
		return cls(y=y, cb=cb, cr=cr)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.y,self.cb,self.cr), 0, 65535, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7RGB10(ColorEncoding):
	"""10-bit RGB components with COLOR.7 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7FullRGB10(ColorEncoding):
	"""10-bit full-range RGB components with COLOR.7 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 1023, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7RGB12(ColorEncoding):
	"""12-bit RGB components with COLOR.7 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 4095, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7FullRGB12(ColorEncoding):
	"""12-bit full-range RGB components with COLOR.7 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 4095, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7RGB16(ColorEncoding):
	"""16-bit RGB components with COLOR.7 colorimetry and QE.1 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 65535, 3, int)

@dataclasses.dataclass(frozen=True)
class Color7FullRGB16(ColorEncoding):
	"""16-bit full-range RGB components with COLOR.7 colorimetry and QE.2 quanitization"""

	r:int
	"""Red primary"""

	g:int
	"""Green primary"""
	
	b:int
	"""Blue primary"""

	@classmethod
	def from_xml(cls, xml:et.Element, ns:typing.Optional[dict]=None):
		"""Parse from XML"""
		r,g,b = (int(val) for val in xml.text.split())
		return cls(r=r, g=g, b=b)
	
	def __post_init__(self):
		"""Validate"""
		self.xsd_validate_color_values((self.r,self.g,self.b), 0, 65535, 3, int)