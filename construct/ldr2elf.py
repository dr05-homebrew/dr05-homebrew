#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile

from construct import GreedyRange, Struct

from structures import fwUpdateFile
from structures import blockHeader
from structures import blockData

from collections import namedtuple

section = namedtuple("section", "vma data")


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
        offset += HEADER_SIZE

    dxe = fw[offset:]
    header = blockHeader.parse(dxe)
    assert header["BLOCK CODE"].BFLAG_FIRST
    entrypoint = header["TARGET ADDRESS"]
    return entrypoint, dxe


def get_sections(dxe):
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
            yield section(vma, data)

def get_decrypted(filename):
    with open(filename, "rb") as fp:
        data = fp.read()
    fwupdate = fwUpdateFile.parse(data)
    return fwupdate.decryptedBody

def create_ldscript(ld_scriptname, entrypoint, sections):
    script = """OUTPUT_FORMAT("elf32-bfin", "elf32-bfin", "elf32-bfin")
OUTPUT_ARCH(bfin)
ENTRY(__start)

ENTRY(.entrypoint)
SECTIONS
{{
    .entrypoint = 0x{:x} ;
    """.format(entrypoint)
    for vma, _ in sections:
        script += ".text_{0:x} 0x{0:x} : {{ *(.text_{0:x}) }}".format(vma)

    script += "}"
    with open(ld_scriptname, "w") as f:
        f.write(script)


def link_objects(ld_scriptname, outfile, infiles):
    res = subprocess.run(
            ["bfin-uclinux-ld",
                "--omagic", # Turn off page alignment of sections, and disable linking against shared libraries.
                "--script={}".format(ld_scriptname),
                "-o", outfile] + infiles)
    assert res.returncode == 0

def obj_from_section(objfile, section):
    with tempfile.NamedTemporaryFile(mode="wb", suffix="bin", prefix="ldr2elf", delete=False) as binfile:
        binfile.write(section.data)
        binfile.close()
        res = subprocess.run(
                ["bfin-uclinux-objcopy",
                    "--input-target", "binary",
                    "--output-target", "elf32-bfin",
                    "--binary-architecture", "bfin",
                    "--set-section-flags", ".data=alloc,load,code",
                    "--rename-section", ".data=.text_{:x}".format(section.vma),
                    "--discard-all",
                    binfile.name,
                    objfile])
        os.unlink(binfile.name)
        assert res.returncode == 0

def create_elf(outfile, entrypoint, sections):
    with tempfile.TemporaryDirectory() as temp_dir:
        objfiles = []
        for section in sections:
            objfile = os.path.join(temp_dir, "{:x}.bin".format(section.vma))
            objfiles.append(objfile)
            obj_from_section(objfile, section)

        ld_scriptname = os.path.join(temp_dir, "link.ld")
        create_ldscript(ld_scriptname, entrypoint, sections)
        link_objects(ld_scriptname, outfile, objfiles)

        res = subprocess.run( ["bfin-uclinux-strip", outfile])
        assert res.returncode == 0


def main(argv):
    if len(argv) != 4:
        print("usage: ldr2dxe <firmware_filename> <dxe number (try 0 or 1)> <outfile>")
        return 1

    filename = argv[1]
    dxe_num = int(argv[2])
    outfile = argv[3]

    data = get_decrypted(filename)
    entrypoint, dxe = get_dxe(data, dxe_num)
    sections = list(get_sections(dxe))

    create_elf(outfile, entrypoint, sections)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
