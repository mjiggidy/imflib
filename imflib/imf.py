from imflib import cpl, pkl
import datetime
import pathlib, typing, dataclasses, re

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


@dataclasses.dataclass
class Imf:
	"""An IMF package"""

	cpl:cpl.Cpl
	pkl:pkl.Pkl

	@classmethod
	def fromPath(cls, path_imf:typing.Union[str,pathlib.Path]) -> "Imf":
		"""Parse an existing IMF"""
		
		if not isinstance(path_imf, pathlib.Path):
			path_imf = pathlib.Path(path_imf)
		if not path_imf.is_dir():
			raise NotADirectoryError(f"Path does not exist or is not a directory: {path_imf}")
		
		glob_temp = list(path_imf.glob("CPL*.xml"))
		if len(glob_temp) != 1:
			raise FileNotFoundError("Could not find a CPL in this directory")

		input_cpl = cpl.Cpl.fromFile(str(glob_temp[0]))

		glob_temp = list(path_imf.glob("PKL*.xml"))
		if len(glob_temp) != 1:
			raise FileNotFoundError("Could not find a PKL in this directory")

		input_pkl = pkl.Pkl.fromFile(str(glob_temp[0]))

		# Marry the pkl assets to the CPL
		for res in input_cpl.resources:
			res.setAsset(input_pkl.getAsset(res.file_id))
		
		return cls(input_cpl, input_pkl)