from construct import *

import sys
import operator
import base64
from texttable import Texttable
import subprocess, tempfile

class SubstitutionCipher(Adapter):
	def __init__(self, *args, **kwargs):
		super(SubstitutionCipher, self).__init__(*args, **kwargs)
		self.decLUT = open("../fwupdate/lut_decode.bin", "rb").read()
		self.encLUT = open("../fwupdate/lut_encode.bin", "rb").read()

	def _encode(self, obj, ctx): #encrypt
		return bytes(bytearray(self.encLUT[b] for b in bytearray(obj)))

	def _decode(self, obj, ctx): #decrypt
		return bytes(bytearray(self.decLUT[b] for b in bytearray(obj)))
	

fwUpdateFile = Struct("fwUpdateFile",
	Struct("updateHeader",
		String("deviceName", 8, "ASCII"),
		UBInt16("fwVersion"),
		UBInt16("fwNumericVersion"),
		UBInt16("year"),
		UBInt8("day"),
		UBInt8("month"),
		UBInt32("checksum"),
		UBInt32("updateFileSize"),
		Const(UBInt64("padding"), 0) # TODO: what is this really? (check the code?)
		),
	Anchor("body"), Bytes("encryptedBody", lambda ctx: ctx.updateHeader.updateFileSize - 0x20),
	Pointer(lambda ctx: ctx.body, SubstitutionCipher(
		Bytes("decryptedBody", lambda ctx: ctx.updateHeader.updateFileSize - 0x20))
		))
########

data = open(sys.argv[1], "rb").read()

updateParsed = fwUpdateFile.parse(data)
print(updateParsed.updateHeader)
print("Firmware body length: %s" % len(updateParsed.decryptedBody))

#########
class PrintContext(Construct):
	def _parse(self, stream, context):
		print context


#see the hardware reference
blockHeader = Struct("blockHeader",
	Anchor("offset"),
	BitStruct("BLOCK CODE",
		BitField("reserved1", 1),
		BitField("reserved2", 1),
		Flag("BFLAG_AUX"),
		Flag("BFLAG_SAVE"),
		BitField("DMACODE", 4), #This should be a ULInt4		

		Flag("BFLAG_FINAL"),
		Flag("BFLAG_FIRST"),
		Flag("BFLAG_INDIRECT"),
		Flag("BFLAG_IGNORE"),
		Flag("BFLAG_INIT"),
		Flag("BFLAG_CALLBACK"),
		Flag("BFLAG_QUICKBOOT"),
		Flag("BFLAG_FILL"),

		BitField("HDRCHK", 8), #TODO: hex
		Const(BitField("HDRSGN", 8), 0xad)  #TODO: hex
#		ULInt8("HDRCHK"), #these cause off by one bit size errors each, what the fuck? bug?
#		ULInt8("HDRSGN")
		),
	ULInt32("TARGET ADDRESS"), #TODO: hex
	ULInt32("BYTE COUNT"),     #TODO: hex
	ULInt32("ARGUMENT")        #TODO: hex
	)

#TODO: find untouched sections
blockData = Struct("blockData",
	If(lambda ctx: not ctx._.blockHeader["BLOCK CODE"].BFLAG_FILL,
		Bytes("data", lambda ctx: ctx._.blockHeader["BYTE COUNT"])
		),
	If(lambda ctx: ctx._.blockHeader["BLOCK CODE"].BFLAG_IGNORE,
		Bytes("skip", lambda ctx: ctx._.blockHeader["BYTE COUNT"])
		)
	)

firmware = Struct("firmware",
	Struct("DXE",	
		GreedyRange(
			Struct("block",
				blockHeader,
				blockData
				)
			)
		)
	)


def enabledFlags(hdr):
	return [f for f,v in hdr["BLOCK CODE"].items() if v and "BFLAG" in f]

def hasPayload(hdr): #TODO: look into the conditions of this more
	if "BFLAG_FILL" not in enabledFlags(hdr) and hdr["BYTE COUNT"]:
		return True

def pprintHeader(block, cnt):
	#TODO: use indent instead of adding more columns to the left?
	hdr = block.blockHeader

	#i dont think theres a good way to get the original data, so we just have to believe this will give the original data...
	bs = [base64.b16encode(b) for b in blockHeader.build(hdr)]
	brow = ["%s. %s:" % (cnt, hex(hdr.offset)), " ".join(reversed(bs[0:4])), " ".join(reversed(bs[4:8])), " ".join(reversed(bs[8:12])), " ".join(reversed(bs[12:16]))]
	
	flagrows = []
	for f in enabledFlags(hdr):
		addrmsg, countmsg, argmsg = "", "", ""

		if f == "BFLAG_FILL":
			addrmsg += "(fill memory at addr)"
			argmsg += "(fill value)"
			countmsg += "(no payload, fill length?)" #TODO: is fill length correct?
		elif f == "BFLAG_INIT":
			addrmsg += "(call addr after optional payload load)"
				#TODO: "For example a zero-sized BFLAG_INIT block
				#would instruct the boot kernel to call a subroutine residing in ROM or
				#flash memory. This method is used to activate the CRC32 feature."
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
	table.set_cols_width([14,12,12,12,12])
	table.set_cols_align(["l","l","l","l","l"])
	table.add_rows(rows)
	print(table.draw())
	print

def objdumpDisasBlock(objdumpPath, block, tmpdir):
#TODO:
#      --start-address=ADDR       Only process data whose address is >= ADDR
#      --stop-address=ADDR        Only process data whose address is <= ADDR

	with tempfile.NamedTemporaryFile(dir=tmpdir) as f:
		offset = block.blockHeader.offset
		len = block.blockHeader["BYTE COUNT"]
		f.write(body[offset+16:offset+16+len])
		f.flush()

		command = ["%s/bfin-linux-uclibc-objdump" % objdumpPath, 
				"-D",
				"-m", "bfin",
				"-b", "binary",
				"--adjust-vma=%s" % hex(hdr["TARGET ADDRESS"]), 
				 f.name]
		output = subprocess.check_output(command).split("\n", 7)[-1]
		output = output.split("\n")

		for l in output:
			print(" "*10 + l.lstrip())

body = updateParsed.decryptedBody
firmwareParsed = firmware.parse(body)

tmpd = tempfile.mkdtemp()
for dxe in firmwareParsed.DXE:
	for i, block in enumerate(firmwareParsed.DXE.block):
		hdr = block.blockHeader
		offset = hdr.offset

		bytesl = [ord(x) for x in body[offset:offset+16]]
		hdr_checkxor = reduce(operator.xor, bytesl)
		assert hdr_checkxor == 0

		assert hdr["TARGET ADDRESS"] % 4 == 0
		assert hdr["BYTE COUNT"] % 4 == 0

		pprintHeader(block, i)
		if(hasPayload(hdr)):
			objdumpDisasBlock(sys.argv[2], firmwareParsed.DXE.block[i], tmpd)
		print("-"*90)
