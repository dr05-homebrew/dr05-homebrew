#!/usr/bin/env python2
import os
import sys
import struct
import numpy as np
from fwutils import *

permfile, flashfile, outfile = sys.argv[1:]

perm = np.memmap(permfile, dtype=np.uint8, mode='r')
flash = np.memmap(flashfile, dtype=np.uint8, mode='r')

length = len(flash)
checksum = flash.sum()

version, version2 = 211,44
year, month, day = 2016, 18, 5

outlen = 32 + len(flash) + 4

out = np.memmap(outfile, shape=outlen, dtype=np.uint8, mode='w+')

out[0:32] = np.fromstring(struct.pack(">8sHHHHII8s",
	"DR-05\0\0\0",
	version, version2,
	year, day * 100 + month,
	checksum,
	length + 32 + 4,
	'\0' * 8
), dtype=np.uint8)
out[32:][:len(flash)] = perm[flash]
out[-4:] = perm[np.fromstring(struct.pack(">I", checksum), dtype=np.uint8)]
