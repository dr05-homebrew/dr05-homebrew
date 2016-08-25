#!/usr/bin/env python2
from __future__ import division
import os
import sys
import numpy as np

from fwutils import * # invert_permutation

permfile, firmwarefile = sys.argv[1:]

perm = np.memmap(permfile, shape=(256), dtype=np.uint8, mode='r')
firmware = np.memmap(firmwarefile, dtype=np.uint8, mode='r')
decoded = np.memmap(firmwarefile + ".bin", shape=(len(firmware) - 32 - 4), mode='w+', dtype=np.uint8)

iperm = invert_permutation(perm)

decoded[:] = iperm[firmware[32:-4]]

