from TASCAM_blackfin_firmware import TASCAMBlackfinFirmware
import sys

ff = TASCAMBlackfinFirmware.from_file(sys.argv[1])

verintstr = str(ff.fw_version)

print("name = %s" % ff.device_name )
print("version = %s.%s" % (verintstr[0],verintstr[1:]) )
print("'numeric' version(?) = %s" % ff.numeric_version)
print("day = %s, month = %s" % (ff.month, ff.day))
print("checksum = %s = %s" % (hex(ff.checksum), ff.checksum))
print("filesize = %s" % ff.fw_file_size)
