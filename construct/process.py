import sys

import argparse

from structures import *
from util import *

blobPath = sys.argv[1]
objdumpPath = sys.argv[2]
data = open(blobPath, "rb").read()

updateParsed = fwUpdateFile.parse(data)
print(updateParsed.updateHeader)
print("Firmware body length: %s" % len(updateParsed.decryptedBody))

decryptedBlobFile = tempfile.NamedTemporaryFile()
decryptedBlobFile.write(updateParsed.decryptedBody)
decryptedBlobFile.flush()

firmwareParsed = firmware.parse(updateParsed.decryptedBody)

for dxe in firmwareParsed.DXE:  # TODO: not implemented yet
    for i, block in enumerate(firmwareParsed.DXE.block):
        hdr = block.blockHeader

        headerAsserts(hdr)

        pprintHeader(block, i)
        if hasPayload(hdr):
            objdumpDisasBlock(objdumpPath, firmwareParsed.DXE.block[i], decryptedBlobFile.name)
        print("-" * 90)
