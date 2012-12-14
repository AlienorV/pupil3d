import os, subprocess, gzip, logging

from sift import Sift

className = "VlfeatSift"
class VlfeatSift(Sift):
	
	win32Executable = "vlfeat/bin/w32/sift.exe"
	linuxExecutable = "vlfeat/bin/maci64/sift"

	def __init__(self, distrDir):
		Sift.__init__(self, distrDir)

	def extract(self, photo, photoInfo):
		photo_name = photo[:-4]
		logging.info("\tExtracting features with the SIFT method from VLFeat library...")
		print self.executable
		subprocess.call([self.executable, "%s.pgm" %photo, "--verbose", "-o", "%s.key" %photo_name]) #"--threshold=0.04",  
		# perform conversion to David Lowe's format
		vlfeatTextFile = open("%s.key" % photo_name, "r")
		loweGzipFile = gzip.open("%s.key.gz" % photo_name, "wb")
		featureStrings = vlfeatTextFile.readlines()
		numFeatures = len(featureStrings)
		# write header
		loweGzipFile.write("%s 128\n" % numFeatures)
		for featureString in featureStrings:
			features = featureString.split()
			#features[0] = str(photoInfo['width']-float(features[0])) # Coordinate system correction
			fx = features[1]
			fy = features[0]
			features[0] = fx
			features[1] = fy
			i1 = 0
			for i2 in (4,24,44,64,84,104,124,132):
				loweGzipFile.write("%s\n" % " ".join(features[i1:i2]))
				i1 = i2
		loweGzipFile.close()
		vlfeatTextFile.close()
		# remove original SIFT file
		os.remove("%s.key" % photo_name)
		logging.info("\tFound %s features" % numFeatures)
