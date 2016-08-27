import base64
from texttable import Texttable
import subprocess
import tempfile
import operator


def headerAsserts(hdr):
    # Note that constants are checked inside struct parsing with Const()
    bytesl = [ord(x) for x in hdr.headerBytes]
    hdr_checkxor = reduce(operator.xor, bytesl)
    assert hdr_checkxor == 0

    assert hdr["TARGET ADDRESS"] % 4 == 0
    assert hdr["BYTE COUNT"] % 4 == 0


def enabledFlags(hdr):
    return [f for f, v in hdr["BLOCK CODE"].items() if v and "BFLAG" in f]


def hasPayload(hdr):  # TODO: look into the conditions of this more
    if "BFLAG_FILL" not in enabledFlags(hdr) and hdr["BYTE COUNT"]:
        return True


def pprintHeader(block, idx):
    hdr = block.blockHeader

    bs = [base64.b16encode(b) for b in hdr.headerBytes]
    brow = ["%s. %s:" % (idx, hex(hdr.offset)),
            " ".join(reversed(bs[0:4])),
            " ".join(reversed(bs[4:8])),
            " ".join(reversed(bs[8:12])),
            " ".join(reversed(bs[12:16]))]

    flagrows = []
    for f in enabledFlags(hdr):
        addrmsg, countmsg, argmsg = "", "", ""

        if f == "BFLAG_FILL":
            addrmsg += "(fill memory at addr)"
            argmsg += "(fill value)"
            countmsg += "(no payload, fill length?)"  # TODO: is fill length correct?
        elif f == "BFLAG_INIT":
            addrmsg += "(call addr after optional payload load)"
                # TODO: "For example a zero-sized BFLAG_INIT block
                # would instruct the boot kernel to call a subroutine residing in ROM or
                # flash memory. This method is used to activate the CRC32 feature."
        elif f == "BFLAG_IGNORE":
            countmsg += "(redirect boot source pointer)"
        elif f == "BFLAG_FIRST":
            addrmsg += "(jmp target at end of boot)"
            argmsg += "(relative next-DXE pointer ^ next free boot source address after current boot stream)"
        elif f == "BFLAG_FINAL":
            f += "\n(pass control to application)"

        flagrows.append(["", f, addrmsg, countmsg, argmsg])

    rows = [
        brow,
        ["", "block code", "targ addr", "byte count", "argument"]
        ]
    rows.extend(flagrows)

    table = Texttable(max_width=90)
    table.set_deco(0)
    table.set_cols_width([14, 12, 12, 12, 12])
    table.set_cols_align(["l", "l", "l", "l", "l"])
    table.add_rows(rows)
    print(table.draw())
    print


def objdumpDisasBlock(objdumpPath, block, decryptedBlobPath):
    # TODO: use indent instead of adding more columns to the left?
    hdr = block.blockHeader
    offset = block.blockHeader.offset
    len = block.blockHeader["BYTE COUNT"]

    baseOffset = hdr["TARGET ADDRESS"]
    startOffset = baseOffset+offset+16
    stopOffset = baseOffset+offset+16+len
    command = [objdumpPath,
               "-D",
               "-m", "bfin",
               "-b", "binary",
               "--adjust-vma", hex(baseOffset),
               "--start-address", hex(startOffset), #objdump takes these relative to --adjust-vma
               "--stop-address", hex(stopOffset),
               decryptedBlobPath]

    print(" ".join(command))
    output = subprocess.check_output(command).split("\n", 7)[-1]
    output = output.split("\n")

    for l in output:
        print(" " * 10 + l.lstrip())
