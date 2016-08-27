import sys

import argparse

from structures import *
from util import *

data = open(sys.argv[1], "rb").read()

updateParsed = fwUpdateFile.parse(data)
print(updateParsed.updateHeader)
print("Firmware body length: %s" % len(updateParsed.decryptedBody))

firmwareParsed = firmware.parse(updateParsed.decryptedBody)

tmpd = tempfile.mkdtemp()
for dxe in firmwareParsed.DXE:  # TODO: not implemented yet
    for i, block in enumerate(firmwareParsed.DXE.block):
        hdr = block.blockHeader

        headerAsserts(hdr)

        pprintHeader(block, i)
        if hasPayload(hdr):
            objdumpDisasBlock(sys.argv[2], firmwareParsed.DXE.block[i], tmpd)
        print("-" * 90)
