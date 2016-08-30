#!/usr/bin/env python2
import sys
import click
import os
import os.path
from io import BytesIO
import shutil
import construct

from structures import *
from util import *

global blobFile  # TODO: fix with Click context passing stuff
global blobData
global blobParsed
global firmwareParsed
global decryptedBlobFile

########
@click.group()
@click.argument('BLOB', nargs=1, type=click.File('rb'))
def cli(blob):
    """
    BLOB is the path to the firmware file.
    """
    global blobFile
    global blobData
    global blobParsed
    global firmwareParsed
    global decryptedBlobFile

    blobFile = blob
    blobData = blobFile.read()

    blobParsed = fwUpdateFile.parse(blobData)

    decryptedBlobFile = tempfile.NamedTemporaryFile()
    decryptedBlobFile.write(blobParsed.decryptedBody)
    decryptedBlobFile.flush()

    firmwareParsed = firmware.parse(blobParsed.decryptedBody)

@click.group()
def dump():
    pass

@click.group()
def patch():
    pass

########
#dump
@click.command()
@click.option('--blockidx', help='comma separated list of zero-based block indexes e.g.: 0,4,5,100, if it\'s not set all blocks are processed')
@click.option('--pbm', help='pbm output, arguments: WIDTH:OFFSET, where offset is in bytes (i.e. *8 bits)', is_flag=True)
@click.option('--pbm-format', help='overridden by --iter-widths, arguments: WIDTH:OFFSET, where offset is in bytes (i.e. *8 bits), defaults to 128:0', default='128:0')
@click.option('--iter-widths', help='output multiple pbms with various widths, arguments: start:stop , overrides --pbm-format')
@click.option('--header-info', help='output header with human readable information', is_flag=True)
@click.option('--disas', help='output objdump disassembly. Specify path to blackfin supporting objdump binary with OBJDUMP_PATH', is_flag=True)
@click.option('--raw', help='output raw block bytes (implies decryption)', is_flag=True)
@click.option('--raw-only-header', help='output raw block header (implies decryption)', is_flag=True)
@click.option('--raw-only-body', help='output raw block body (implies decryption)', is_flag=True)
@click.option('--to-files', help='output individual blocks to individual files instead of stdout', type=click.Path(exists=True))
@click.option('--fname-format', help='used by --to-files: python format string taking {dxe} and {blockid}, {width} if --pbm-format', default='{dxe}-{blockid}.bin')
def dump_block(**kwargs):  # blockidx, pbm, headerinfo, disas, raw, raw_only_header, raw_only_body, to_files, fname_format
    if kwargs["blockidx"]:
        blocks = [int(c) for c in kwargs["blockidx"].split(",")]
    else:
        blocks = range(0, len(firmwareParsed.DXE.block))

    for i in blocks:
        block = firmwareParsed.DXE.block[i]
        hdr = block.blockHeader

        try:
            headerAsserts(hdr)
        except AssertionError as e:
            print(e)  # TODO

        if kwargs["iter_widths"]:
            sw, ew = kwargs["iter_widths"].split(":")
            sw = int(sw)
            ew = int(ew) if kwargs["pbm"] and kwargs["to_files"] else sw
        else:
            sw = int(kwargs["pbm_format"].split(":")[0])
            ew = sw

        for w in range(sw, ew+8, 8):
            if kwargs["to_files"]:
                try:
                    if kwargs["pbm"] or kwargs["disas"] or kwargs["raw_only_body"] and not (kwargs["header_info"] or kwargs["raw_only_header"]):
                        assert hasPayload(block)
                    path = os.path.join(kwargs["to_files"], kwargs["fname_format"].format(dxe=0, blockid=i, width=w))
                    f = open(path, "wb")  # TODO: dxe
                except AssertionError as e:
                    #print(repr(e))  # TODO
                    continue

                stdoutsave = sys.stdout
                sys.stdout = f

            if kwargs["pbm"]:
                try:
                    assert hasPayload(block)
                    import PIL.Image
                    import math

                    if kwargs["iter_widths"]:
                        width, offset = w, kwargs["pbm_format"].split(":")[1]
                    else:
                        width, offset = kwargs["pbm_format"].split(":")
                    width = int(width)
                    offset = int(offset)

                    data = block.blockData.data[offset:]

                    height = int(math.ceil(((len(block.blockData.data) - offset) * 8) / float(width)))
                    data += "\x00" * ((height*width/8) - (len(block.blockData.data) - offset))  # pad

                    img = PIL.Image.frombytes(mode="1", size=(width, height), data=data)

                    vf = BytesIO()
                    img.save(vf, format="ppm")
                    vf.seek(0)
                    sys.stdout.write(vf.read())
                except AssertionError as e:
                    print(e)  # TODO

            if kwargs["header_info"]:
                pprintHeader(block, i)

            if kwargs["disas"]:
                try:
                    assert hasPayload(block)
                    if "OBJDUMP_PATH" in os.environ:
                        objdumpPath = os.environ["OBJDUMP_PATH"]
                    else:
                        objdumpPath = "blackfin-linux-uclibc-obdump"  # TODO: whats the difference between all the versions?

                    objdumpDisasBlock(objdumpPath, block, decryptedBlobFile.name)
                except AssertionError as e:
                    print(e)  # TODO

            if kwargs["raw"]:  # TODO: make mutex
                sys.stdout.write(block.blockHeader.headerBytes)
                try:
                    assert hasPayload(block)
                    sys.stdout.write(block.blockData.data)
                except AssertionError as e:
                    print(e)  # TODO
                sys.stdout.flush()

            if kwargs["raw_only_header"]:
                sys.stdout.write(block.blockHeader.headerBytes)
                sys.stdout.flush()

            if kwargs["raw_only_body"]:
                try:
                    assert hasPayload(block)
                    sys.stdout.write(block.blockData.data)
                except AssertionError as e:
                    print(e)  # TODO
                sys.stdout.flush()


            if len(blocks) != 1 and not kwargs["to_files"]:  # TODO: /stdout, binary?
                print("-" * 90)

            if kwargs["to_files"]:  # TODO: more proper wrapping
                f.flush()
                f.close()
                sys.stdout = stdoutsave



@click.command()
def dump_header():
    print(blobParsed.updateHeader)
    print("Firmware body length: %s" % len(blobParsed.decryptedBody))
    pass

@click.command()
@click.option('--decrypt', is_flag=True)
@click.option('--to-file', help='output to file instead of stdout', type=click.File('wb'))
def dump_body(**kwargs):
    if kwargs["to_file"]:
        f = kwargs["to_file"]
        stdoutsave = sys.stdout
        sys.stdout = f

    if kwargs["decrypt"]:
        data = blobParsed.decryptedBody
    else:
        data = blobParsed.encryptedBody

    sys.stdout.write(data)
    sys.stdout.flush()

    if kwargs["to_file"]:  # TODO: more proper wrapping
        f.flush()
        f.close()
        sys.stdout = stdoutsave


########
#patch
@click.command()
@click.option('--patch-hdr-checksum', help='automatically recalculate and patch the checksum for the block header', is_flag=True)
@click.argument('IDX', nargs=1, type=int)
@click.argument('JSON', nargs=1)
def patch_struct(**kwargs):
    """
    IDX is the zero-based index of the block to patch
    JSON is a json string mirroring the structure containing the values to patch
    """
    pass

@click.command()
@click.argument('PATCHFILE', nargs=1, type=click.File('rb'))
@click.argument('OUTFILE', nargs=1, type=click.File('w+b'))
@click.option('--blockidx', help='zero-based index of block to patch', type=int)
@click.option('--offset', help='if blockidx is specified this is the offset inside the block, otherwise it is the offset from the beginning of the header')
@click.option('--already-encrypted', help='use this if you are patching with already encrypted data', is_flag=True)
@click.option('--patch-block-hdr-checksum', help='automatically recalculate and patch the checksum for the block header (for the lazy)', is_flag=True)
@click.option('--patch-blob-hdr-checksum', help='automatically recalculate and patch the checksum for the blob header (for the lazy)', is_flag=True)
@click.option('--mask', help='bitmask file to use when patching, the first byte of the mask corresponds to the first byte of the patchfile', type=click.File('rb'))
#@click.option('--overwrite', help='overwrite original blob')  # TODO?
def patch_binary(**kwargs):
    """
    PATCHFILE is the path to the binary patch file
    """

    of = kwargs["outfile"]
    data = kwargs["patchfile"].read()
    if kwargs["mask"]:
        mask = kwargs["mask"].read()
    else:
        mask = "\xFF"*len(data)

    offset = 0
    if kwargs["blockidx"]:
        i = kwargs["blockidx"]
        offset = firmwareParsed.DXE.block[i].blockHeader.offset

    if kwargs["offset"]:
        try:
            assert offset[0:2] == "0x"
            offset += int(kwargs["offset"][2:], 16)
        except AssertionError:
            offset += int(kwargs["offset"])


    if not kwargs["already_encrypted"]:
        data = SubstitutionCipher(Bytes("", len(data))).build(data)

    blobFile.seek(0)
    shutil.copyfileobj(blobFile, of)
    of.seek(0)

    blobFile.seek(offset)
    blob = blobFile.read(len(data))
    of.seek(offset)

    maskedOrig = [ord(blobbyte) & ~ord(maskbyte) for blobbyte, maskbyte in zip(blob, mask)]
    maskedPatch = [ord(databyte) & ord(maskbyte) for databyte, maskbyte in zip(data, mask)]

    for orig, patch in zip(maskedOrig, maskedPatch):  # TODO:what if patch is longer than the file?
        of.write(chr(orig | patch))

    if kwargs["patch_block_hdr_checksum"]:
        assert kwargs["blockidx"]
        of.seek(firmwareParsed.DXE.block[i].blockHeader.offset)

        bytesl = [ord(x) for x in of.read(4)]  # TODO: move to seaparate function (see also asserts)
        hdr_checkxor = reduce(operator.xor, bytesl)
        of.seek(firmwareParsed.DXE.block[i].blockHeader.offset + 3)
        of.write(construct.UBInt32("").build(hdr_checkxor))

    if kwargs["patch_blob_hdr_checksum"]:
        of.seek(0)
        checksum = sum(ord(b) for b in fwUpdateFile.parse(of.read()).decryptedBody)
        print(checksum)
        of.seek(0)
        of.seek(16)
        of.write(construct.ULInt32("").build(checksum))

########

cli.add_command(dump)
cli.add_command(patch)

patch.add_command(patch_struct, name="struct")
patch.add_command(patch_binary, name="binary")

dump.add_command(dump_block, name="block")
dump.add_command(dump_header, name="header")
dump.add_command(dump_body, name="body")

if __name__ == '__main__':
    cli()


