#!/usr/bin/env python
# encoding: utf-8
import os, subprocess, gzip, logging

import cv2
import numpy as np

from sift import Sift

className = "SurfCV"
class SurfCV(Sift):
	
	def __init__(self, distrDir):
		Sift.__init__(self, distrDir)
		self.thresh=500
		self.octaves=4
		self.layers=2
		
	def extract(self, photo, photoInfo):
		logging.info("\tExtracting features with the SURF method from OpenCV library...")
	
		# make an opencv image from photo dir
		src_dir = photoInfo['dirname']
		src_n = photoInfo['basename']
		full_dir = src_dir+'/'+src_n

		src = cv2.imread(full_dir)
		img = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
		
		#detector = cv2.FeatureDetector_create('SURF')
		detector = cv2.SurfFeatureDetector(self.thresh, self.octaves, self.layers)
		extractor = cv2.DescriptorExtractor_create('SIFT')
		
		kp = detector.detect(img)
		kp, desc = extractor.compute(img, kp)
		
		# write the .key file in David Lowe's format
		loweGzipFile = gzip.open("%s.key.gz" % photo, "wb")
		loweGzipFile.write("%s %s\n" %(len(kp), len(desc[0])) ) # header for Lowe format
		desc = np.int32(desc) # Bundler's Keypoint matcher doesn't deal well with floats
        
		for k, d in zip(kp, desc):
			loweGzipFile.write("%s %s %s %s\n %s\n %s\n %s\n %s\n %s\n %s\n %s\n" \
								%(photoInfo['width']-k.pt[0], k.pt[1], k.size, np.radians(k.angle), 
								" ".join(map(str, d[0:20])), " ".join(map(str, d[20:40])), " ".join(map(str, d[40:60])), 
								" ".join(map(str, d[60:80])), " ".join(map(str, d[80:100])), " ".join(map(str, d[100:120])),
								" ".join(map(str, d[120:])) ))
								
		loweGzipFile.close()

		logging.info("\tFound %s features" % len(kp))
