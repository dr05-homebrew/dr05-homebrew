#!/usr/bin/env python3
# encoding: utf-8

import sys
import logging
import pprint

from collections import namedtuple
from elf32 import elf32_file

# inspired by http://svn.navi.cx/misc/trunk/python/bin2elf.py

def pageAlign(p):
    return (p + 0xfff) & ~0xfff


segment = namedtuple("segment", "vaddr data flags")

def create_elf(entrypoint, segments, fp_out):
    class SHTNull:
        type = "NULL"
        name_offset = flags = addr = offset = size = link = info = align = entry_size = 0
        name = None
        data = None

    mysections = [
            SHTNull()
            ]

    class MyELF:
        class identifier:
            file_class = "CLASS32"
            encoding = "LSB"
            version = 1 # the only version
        type          = "SHARED" # good?
        machine       = 106
        version       = 1
        header_size   = 0x34
        entry         = entrypoint
        flags         = 0

        ph_offset     = header_size
        ph_entry_size = 0x20
        ph_count      = len(segments)


        sh_offset     = ph_offset + ph_count * ph_entry_size
        sh_entry_size = 0x28
        sh_count      = len(mysections)

        strtab_section_index = 0
        strtab_data_offset = 0

        program_table = []
        sections      = mysections

    elf = MyELF()

    data_offset = pageAlign(elf.ph_offset
            + elf.ph_count * elf.ph_entry_size
            + elf.sh_count * elf.sh_entry_size
            )
    cur_offset = data_offset

    data = b""
    for seg in segments:
        size = len(seg.data)
        class MyPH:
            type = "LOAD"
            offset = cur_offset
            vaddr = seg.vaddr
            paddr = seg.vaddr
            file_size = size
            mem_size = size
            flags = seg.flags # or perm
            align = 1
        cur_offset = pageAlign(cur_offset + size)
        data += seg.data
        elf.program_table.append(MyPH())

    elfdata = elf32_file.build(elf)
    fp_out.write(elfdata)
    fp_out.seek(data_offset)
    fp_out.write(data)
    pprint.pprint(elf32_file.parse(elfdata))

