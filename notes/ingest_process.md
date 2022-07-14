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