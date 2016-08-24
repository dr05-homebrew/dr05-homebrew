from __future__ import division
import os
import sys
import numpy as np
import cv2

permfile, offset, firmwarefile = sys.argv[1:]

perm = np.memmap(permfile, shape=(256), dtype=np.uint8, mode='r')
offset = int(offset)
firmware = np.memmap(firmwarefile, dtype=np.uint8, mode='r')
decoded = np.memmap(firmwarefile + ".bin", shape=(len(firmware) - offset), mode='w+', dtype=np.uint8)

def invert_permutation(perm):
	result = np.zeros(256, dtype=np.uint8)

	for i,v in enumerate(perm):
		result[v] = i

	return result

iperm = invert_permutation(perm)

decoded[:] = iperm[firmware[offset:]]

