from __future__ import division
import os
import sys
import numpy as np
import cv2

def invert_permutation(perm):
	result = np.zeros(256, dtype=np.uint8)

	for i,v in enumerate(perm):
		result[v] = i

	return result

def roundup(n, k):
	return n + (-n % k)
