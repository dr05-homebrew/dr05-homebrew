from construct import *

import sys
import operator
import base64
from texttable import Texttable

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


def pprintHeader(block):
	#TODO: use indent instead of adding more columns to the left
	hdr = block.blockHeader

	#i dont think theres a way to get the original data, so we just have to believe this will give the original data...
	bs = [base64.b16encode(b) for b in blockHeader.build(hdr)]
	brow = [hex(hdr.offset), " ".join(bs[0:4]), " ".join(bs[4:8]), " ".join(bs[8:12]), " ".join(bs[12:16])]
	
	enabledFlags = [f for f,v in hdr["BLOCK CODE"].items() if v and "BFLAG" in f]
	flagrows = [["", f, "","",""] for f in enabledFlags]

	rows = [
		brow,
		["", "block code", "targ addr", "byte count", "argument"]
		]
	rows.extend(flagrows)

	table = Texttable()
	table.add_rows(rows)
	table.set_deco(0)
	print(table.draw())
	print

body = updateParsed.decryptedBody
firmwareParsed = firmware.parse(body)

for dxe in firmwareParsed.DXE:
	for i,block in enumerate(firmwareParsed.DXE.block):
		offset = block.blockHeader.offset

		hdr_checkxor =  reduce(operator.xor, [ord(x) for x in body[offset:offset+16]])
		assert hdr_checkxor == 0

		pprintHeader(block)
