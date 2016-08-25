#!/usr/bin/env python2
from __future__ import division
import os
import sys
import numpy as np
import cv2
from fwutils import *

flashfile, firmwarefile = sys.argv[1:]

flash = np.memmap(flashfile, dtype=np.uint8, mode='r')
firmware = np.memmap(firmwarefile, dtype=np.uint8, mode='r')

def heatmap(seq1, seq2):
	length = min(len(seq1), len(seq2))
	indices = (seq1[:length].astype(np.uint16) << 8) | (seq2[:length])
	counts = np.bincount(indices)
	bins = np.zeros((256, 256), dtype=np.uint32)
	bins.flat = counts
	return bins

def extract_permutation(heatmap):
	result = np.zeros(256, dtype=np.uint8)

	for i,row in enumerate(heatmap):
		result[i] = np.argmax(row)

	return result

offset = 32

def redraw():
	global hm
	print "offset", offset
	hm = heatmap(flash, firmware[offset:]).astype(np.float32)
	hm[hm > 0] = np.log(hm[hm>0])
	hm /= hm.max()
	cv2.imshow("heatmap", hm)

redraw()

VK_LEFT = 2424832
VK_RIGHT = 2555904

while True:
	key = cv2.waitKey(1000)
	if key == -1:
		continue

	elif key in (13, 10, 27):
		break
	
	elif key == VK_LEFT and offset > 0:
		offset -= 1
		redraw()
	
	elif key == VK_RIGHT:
		offset += 1
		redraw()
	
	else:
		print key

cv2.destroyAllWindows()

cv2.imwrite("substitution.png", (hm*255).astype(np.uint8))

print "chosen offset", offset

lut_encode = np.memmap("lut_encode.bin", shape=(256), dtype=np.uint8, mode='w+')
lut_decode = np.memmap("lut_decode.bin", shape=(256), dtype=np.uint8, mode='w+')
lut_encode[:] = extract_permutation(hm)
lut_decode[:] = invert_permutation(lut_encode)
