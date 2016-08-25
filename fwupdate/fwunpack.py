#!/usr/bin/env python2
from __future__ import division
import os
import sys
import numpy as np

from fwutils import * # invert_permutation

firmwarefile = sys.argv[1]

flashfile = firmwarefile + ".flash"

lut_decode = np.memmap(os.path.join(os.path.dirname(__file__), "lut_decode.bin"), shape=(256), dtype=np.uint8, mode='r')
firmware = np.memmap(firmwarefile, dtype=np.uint8, mode='r')
decoded = np.memmap(flashfile, shape=(len(firmware) - 32 - 4), mode='w+', dtype=np.uint8)

decoded[:] = lut_decode[firmware[32:-4]]

