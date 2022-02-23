__all__ = ["cpl","pkl"]

import datetime, re, typing
import xml.etree.ElementTree as et
def xsd_datetime_to_datetime(xsd_datetime:str)->datetime:
	"""Convert XML XSD DateTime to python datetime"""
	# XSD DateTime format is:
	# YYYY-MM-DDTHH:MM:SS(.SS)
	#
	# Followed optionally by
	# Z        - UTC
	# +|-HH:MM - Timezone offset from UTC

	match_date = re.match(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}(?:\.\d+)?)(?P<timezone>(?:Z)|([\+\-].+))?", xsd_datetime, re.I)
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

def xsd_optional_string(xml:et.Element, default_value:typing.Optional[str]="") -> typing.Union[str,None]:
	"""Return a string that may be optionally defined in the XML"""
	return xml.text if xml is not None else default_value