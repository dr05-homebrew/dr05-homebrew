import sys
import click
import os

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
@click.option('--blockidx', help='comma separated list of zero-based block indexes e.g.: 0,4,5,100')
@click.option('--pbm', help='pbm output, arguments: WIDTH:OFFSET, where offset is in pixels (i.e. bits)')
@click.option('--headerinfo', help='output header with human readable information', is_flag=True)
@click.option('--disas', help='output objdump disassembly. Specify path to blackfin supporting objdump binary with OBJDUMP_PATH', is_flag=True)
@click.option('--raw', help='output raw block bytes (implies decryption)', is_flag=True)
@click.option('--raw-only-header', help='output raw block header (implies decryption)', is_flag=True)
@click.option('--raw-only-body', help='output raw block body (implies decryption)', is_flag=True)
@click.option('--to-files', help='output individual blocks to individual files instead of stdout', type=click.Path(exists=True))
@click.option('--fname-format', help='used by --to-files: python format string taking {dxe} and {blockid}', default='{dxe}-{blockid}.bin')
def dump_block(**kwargs):  # blockidx, pbm, headerinfo, disas, raw, raw_only_header, raw_only_body, to_files, fname_format
    if kwargs["blockidx"]:
        blocks = [int(c) for c in kwargs["blockidx"].split(",")]
    else:
        blocks = range(0, len(firmwareParsed.DXE[0]))

    for i in blocks:
        block = firmwareParsed.DXE.block[i]
        hdr = block.blockHeader

        try:
            headerAsserts(hdr)
        except AssertionError as e:
            print(e)  # TODO

        if kwargs["headerinfo"]:
            pprintHeader(block, i)

        if kwargs["disas"]:
            assert hasPayload(hdr)

            if "OBJDUMP_PATH" in os.environ:
                objdumpPath = os.environ["OBJDUMP_PATH"]
            else:
                objdumpPath = "blackfin-linux-uclibc-obdump"  # TODO: whats the difference between all the versions?

            objdumpDisasBlock(objdumpPath, block, decryptedBlobFile.name)

        if kwargs["pbm"]:
            pass

        if kwargs["raw"]:
            pass

        if kwargs["raw_only_header"]:
            pass

        if kwargs["raw_only_body"]:
            pass

        if kwargs["to_files"]:
            pass

        if kwargs["fname_format"]:
            pass

        print("-" * 90)


@click.command()
def dump_header():
    print(blobParsed.updateHeader)
    print("Firmware body length: %s" % len(blobParsed.decryptedBody))
    pass

@click.command()
@click.option('--decrypt', is_flag=True)
def dump_body(**kwargs):
    pass
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
@click.option('--blockidx', help='zero-based index of block to patch', type=int)
@click.option('--offset', help='if blockidx is specified this is the offset inside the block, otherwise it is the offset from the beginning of the header')
@click.option('--already-encrypted', help='use this if you are patching with already encrypted data', is_flag=True)
@click.option('--mask', help='bitmask file to use when patching', type=click.File('rb'))
def patch_binary():
    """
    PATCHFILE is the path to the binary patch file
    """
    pass
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


