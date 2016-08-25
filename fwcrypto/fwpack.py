#!/usr/bin/env python2
import os
import sys
import struct
import datetime
import numpy as np
from fwutils import *

permfile, flashfile, outfile = sys.argv[1:]

pagesize = 512

perm = np.memmap(permfile, dtype=np.uint8, mode='r')

flashlength = os.path.getsize(flashfile)
if flashlength > 0:
	flash = np.memmap(flashfile, shape=flashlength, dtype=np.uint8, mode='r')
else:
	flash = np.zeros((0,), dtype=np.uint8)

checksum = flash.sum()

paddedlength = roundup(flashlength + 4, pagesize)
outlength = 32 + paddedlength

version = 1337
revision = 42
now = datetime.datetime.now()
year, month, day = now.year, now.month, now.day

out = np.memmap(outfile, shape=outlength, dtype=np.uint8, mode='w+')

out[0:32] = np.fromstring(struct.pack(">8sHHHHII8s",
	"DR-05\0\0\0",
	version, revision,
	year, day * 100 + month,
	checksum,
	outlength,
	'\0' * 8
), dtype=np.uint8)

out[32:32+len(flash)] = perm[flash]
out[32+len(flash):-4] = 0xff
out[-4:] = perm[np.fromstring(struct.pack(">I", checksum), dtype=np.uint8)]
