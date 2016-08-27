import sys
import click
import os

from structures import *
from util import *


########
@click.group()
@click.argument('BLOB', nargs=1, type=click.File('rb'))
def cli(blob):
    pass

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
@click.option('--to-files', help='output individual blocks to individual files instead of stdout')
@click.option('--fname-format', help='used by --to-files: python format string taking {dxe} and {blockid}', default='{dxe}-{blockid}.bin')
def dump_block():
    pass

@click.command()
def dump_header():
    pass

@click.command()
@click.option('--decrypt', is_flag=True)
def dump_body():
    pass
########
#patch
@click.command()
@click.option('--recalc-hdr-checksum', help='recalculate the checksum for the block header', is_flag=True)
@click.argument('IDX', nargs=1)#, help='zero-based index of the block to patch', nargs=1)
@click.argument('JSON', nargs=1)#, help='a json string mirroring the structure containing the values to patch', nargs=1)
def patch_struct():
    pass

@click.command()
@click.option('--blockidx', help='zero-based index of block to patch')
@click.option('--offset', help='if blockidx is specified this is the offset inside the block, otherwise it is the offset from the beginning of the header')
@click.option('--already-encrypted', help='use this if you are patching with already encrypted data', is_flag=True)
@click.option('--mask', help='bitmask file to use when patching')
def patch_binary():
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

exit()

blobPath = sys.argv[1]
objdumpPath = sys.argv[2]

if "OBJDUMP_PATH" in os.environ:
    objdumpPath = os.environ["OBJDUMP_PATH"]
else:
    objdumpPath = "blackfin-linux-uclibc-obdump" #TODO: whats the difference between all the versions?

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

