from construct import *

import sys

class SubstitutionCipher(Adapter):
	def __init__(self, *args, **kwargs):
		super(SubstitutionCipher, self).__init__(*args, **kwargs)
		self.decLUT = open("../fwupdate/lut_decode.bin", "rb").read()
		self.encLUT = open("../fwupdate/lut_encode.bin", "rb").read()

	def _encode(self, obj, ctx): #encrypt
		return bytes("".join([self.encLUT[ord(b)] for b in obj])) #TODO: WTF

	def _decode(self, obj, ctx): #decrypt
		return bytes("".join([self.decLUT[ord(b)] for b in obj])) #TODO: WTF
	

########
updateHeader = Struct("updateHeader",
	String("deviceName", 8, "ASCII"),
	UBInt16("fwVersion"),
	UBInt16("fwNumericVersion"),
	UBInt16("year"),
	UBInt8("day"),
	UBInt8("month"),
	UBInt32("checksum"),
	UBInt32("updateFileSize"),
	Padding(8) # TODO: what is this really? #TODO: assert = 0x00 rep 8
	)
encryptedBody = Bytes("encryptedBody", lambda ctx: ctx.updateHeader.updateFileSize - 0x20)

fwUpdateFile = Struct("fwUpdateFile",
	updateHeader,
	encryptedBody
	)
########

file = open(sys.argv[1], "rb")
data = file.read()

updateParsed = fwUpdateFile.parse(data)
print(updateParsed.updateHeader)
encBodyLen = len(updateParsed.encryptedBody)
print("Firmware body length: %s" % encBodyLen)

decBody = SubstitutionCipher(Bytes("decBody", lambda ctx: encBodyLen)) #HAX
decBodyParsed = decBody.parse(updateParsed.encryptedBody)
print(len(decBodyParsed))
#########
class PrintContext(Construct):
	def _parse(self, stream, context):
		print context


#see the hardware reference
blockHeader = Struct("blockHeader",
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
		BitField("HDRSGN", 8)  #TODO: hex
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
				Anchor("offset"),
				blockHeader,
				blockData
				)
			)
		)
	)

firmwareParsed = firmware.parse(decBodyParsed)

#TODO: assert reduce(operator.xor, header) == 0, and HDRSGN

