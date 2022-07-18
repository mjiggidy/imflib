import sys, pathlib
from imflib import opl

def opl_info(opl:opl.Opl):
	"""Show them infos"""
	if opl.annotation_text: print(opl.annotation_text)
	print(f"OPL ID {opl.id} intended for CPL ID {opl.cpl_id}")
	print(f"Created by {opl.issuer} on {opl.issue_date} using {opl.creator}")
	if opl.security:
		print(f"It is signed with {opl.securtiy}")
	else:
		print("It is unsigned")

	if opl.aliases:
		print(f"{len(opl.aliases)} aliases defined:")
		for alias in opl.aliases:
			print(alias)
	
	if opl.extension_properties:
		print(f"{len(opl.extension_properties)} extension properties defined:")
		for prop in opl.extension_properties:
			print(f"  {prop}")
	
	print(f"{len(opl.macros)} macros defined:")
	for macro in opl.macros:
		print(f"  {macro}")
	


def main(paths:list[str]):
	"""Parse an OPL for secret testings"""

	for path_opl in paths:
		print(path_opl)
		opl_info(opl.Opl.from_file(path_opl))
		print("---")

if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit(f"Usage: {pathlib.Path(__file__).name} OPL_filepath.xml")
	
	main(sys.argv[1:])