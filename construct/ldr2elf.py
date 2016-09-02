#!/usr/bin/env python3
import sys
import os

from construct import GreedyRange, Struct

from structures import fwUpdateFile
from structures import blockHeader
from structures import blockData

from elf import segment
from elf import create_elf


blockparser = GreedyRange(
            Struct("block",
                blockHeader,
                blockData
                )
            )
HEADER_SIZE = 0x10
RWX = 0x7

def get_dxe(fw, dxe_num):
    """returns data STARTING with the DXE, figure out whree it ends yourself"""
    offset = 0
    entrypoint = 0
    for cur_dxe in range(dxe_num):
        header = blockHeader.parse(fw[offset:])
        assert header["BLOCK CODE"].BFLAG_FIRST
        arg = header["ARGUMENT"]
        offset += arg

        header = blockHeader.parse(fw[offset:])
        if header["BLOCK CODE"].BFLAG_FINAL:
            raise Exception("Reached FINAL @ 0x{:x} before finding requested DXE".format(offset))
        assert header["BLOCK CODE"].BFLAG_INIT
        entrypoint = header["TARGET ADDRESS"]
        arg = header["ARGUMENT"]
        offset += HEADER_SIZE
    return entrypoint, fw[offset:]


def get_segments(dxe):
    blocks = blockparser.parse(dxe)
    for block in blocks[1:]:
        header = block["blockHeader"]
        body = block["blockData"]

        block_code = header["BLOCK CODE"]
        if block_code["BFLAG_INIT"]:
            break
        vma = header["TARGET ADDRESS"]

        data = body["data"]
        if data:
            yield segment(vma, data, RWX)

def get_decrypted(filename):
    with open(filename, "rb") as fp:
        data = fp.read()
    fwupdate = fwUpdateFile.parse(data)
    return fwupdate.decryptedBody

def main(argv):
    if len(argv) != 3:
        print("usage: ldr2dxe <firmware_filename> <dxe number (try 0 or 1)>")
        return 1

    filename = argv[1]
    dxe_num = int(argv[2])

    data = get_decrypted(filename)
    entrypoint, dxe = get_dxe(data, dxe_num)
    segments = list(get_segments(dxe))

    out_filename = filename + ".elf"
    if os.path.isfile(out_filename):
        print("output file {} exists, overwriting.. hahahahaha, hope it was nothing important".format(out_filename))
    else:
        print("you'll find your ELF in {}".format(out_filename))

    with open(out_filename, "wb") as fp:
        create_elf(entrypoint, segments, fp)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

