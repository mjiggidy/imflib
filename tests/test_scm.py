from imflib import scm
import sys, xml.etree.ElementTree

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		sys.exit(f"Usage: {__file__} path/to/scm.xml [path/to/another_scm.xml ...]")
	
	for path_scm in sys.argv[1:]:
		print(path_scm)
		print("-----")
		
		try:
			map = scm.SidecarCompositionMap.from_file(path_scm)
		except Exception as e:
			print(f"Unable to parse SCM: {e}")
			continue

		print(f"Has UUID {map.id}")
		print(f"Issued by {map.issuer or '[Unknown Issuer]'} on {map.issue_date}")
		if map.annotation: print(f"Has annotation: {map.annotation}")
		print(f"Contains asset-to-CPL mappings for {len(map.assets)} sidecar asset(s):")
		for asset in map.assets:
			print(f"\t{asset}")

		print("Re-written to XML:")
		print("==================")

		map.to_file(sys.stdout)