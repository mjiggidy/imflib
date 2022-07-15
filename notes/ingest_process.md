From SMPTE 429-8-2007: https://ieeexplore.ieee.org/document/7290438

# Package ingest process
As illustrated using pseudo-code in Figure 2 below, a DCP storage volume is ingested by first opening the Asset Map document on that volume. The means of identifying the Asset Map on the volume is defined by the normative DCP Map Profile (see Section 9) for that media type. The Asset Map is used to locate the Packing List(s) which detail the contents of the available DCP(s). Assets are chosen from the Packing List(s), and the selected assets are ingested by using the Asset Map to locate the chunks of data on the storage volume. The chunks are concatenated to restore the original file. (This example does not illustrate multi-volume ingest). Ingest DCP volume:

```
open the Asset Map
for each Packing List in the Asset Map
    open the Packing List
    for each Asset in the Packing List
        if this Asset is wanted
            locate the corresponding Asset structure in the Asset Map
            for each chunk in the Asset structure
                read the chunk data
                write to destination
            test the message digest
```


# Update from SMPTE 429-8-2014
## Asset Map Location
The filesystem shall contain either: Authorized licensed use limited to:

- A single Asset Map document in root directory of the filesystem; or
- One or more Asset Map documents, each within a directory whose immediate parent is the root directory, i.e. a top-level directory. The length of the name of the directory containing the Asset Map document shall be no more than 100 characters.

For example, Asset Map documents will not be present both (i) in the root directory of the filesystem and (ii) within directories whose immediate parent directory is the root directory.  Each Asset Map document shall be a file named `ASSETMAP.xml`.

*Note:* Similarly named files, e.g. `ASSETMAP` can be present, but are not considered in the context of this specification, i.e. they are ignored.

## Example Ingest Algorithm (Informative)
The following is an example ingest process for a filesystem organized according to the Basic Map Profile v2. The Ingest Mapped File Set algorithm is defined in Section 4.1.

```
Ingest Basic Map Profile V2 Filesystem:

    if root directory contains a file named "ASSETMAP.xml"
        Ingest Mapped File Set in root directory

    else for each top level directory of root directory:
        if top level directory contains a file named "ASSETMAP.xml"
            Ingest Mapped File Set in top level directory
```