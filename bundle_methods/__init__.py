import sys, os, argparse, tempfile, subprocess
from threading import Thread
import numpy as np

import sqlite3

from PIL import Image
from PIL.ExifTags import TAGS

import defaults

import matching
from matching import *

import features
from features import *

distrPath = os.path.dirname( os.path.abspath(sys.argv[0]) )

bundlerExecutable = ''
if sys.platform == "win32": bundlerExecutable = os.path.join(distrPath, "software/bundler/bin/bundler.exe")
else: bundlerExecutable = os.path.join(distrPath, "software/bundler/bin_dev/bundler")

RadialUndistordExecutable = os.path.join(distrPath, "software/bundler/bin_dev/RadialUndistort")

SCALE = 1.0
bundler_list_fn = "list.txt"
bundler_list_add_fn = "add_list.txt"

CAMERA_DB = os.path.join(distrPath, "bundle_methods/cameras/cameras.sqlite")
EXIF_ATTRS = dict(Model=True,Make=True,ExifImageWidth=True,ExifImageHeight=True,FocalLength=True)


class Bundler(object):
	"""Multithreaded Bundler Pipeline
		INPUT: Directory with .jpg photos to be used for Bundler
		OUTPUT: Bundler reconstruction in tempfile Directory

		Steps:
		+ Parse Command Line Flags and set these variables to the object
		******* To do in multiple threads ******
		+ Process Photos: 
			- make copy of image in pgm format for SIFT
			- Extract exif data from photos
			- Look up camera in database for sensor type
			- Calculate focal length in pixels
			- Append photo_list with image names and focal lengths
				[(photoname.jpg, 0, focal_length_pixels),(..,..,..)...] 
				eg: ["000001.jpg", 0, 524.2]
		+ Feature detection
			- Detect Features with specified engine
			- Save features to .key file using image name as file names
				eg. 00000001.jpg.key 
			- append feature_list with image names and keypoint file names
		******* Stop Multithread processes ******
		+ File I/O
			- Write list.txt with sorted photo_list
			- Write list_features.txt with sorted feature_list
		+ Match Features
			- Match features with matching engine
		+ Run Bundler
			- Using list.txt and options.txt as options file 
	"""
	def __init__(self):
		self.currentDir = os.getcwd()
		self.matching_engine = "bundler"

		self.photo_list = [] # list to store photo file names & focal lengths
		self.feature_list = [] # list to store keypoint file names 
		self.photo_dict = {}

		self.parse_command_line()
		self.sfm_path = os.path.join(self.data_in, "SfM")
		if not self.add_photos:
			os.mkdir(self.sfm_path)
		self.src_imgs_path = os.path.join(self.data_in, "src_imgs")
		self.load_data() 


		if self.verbose:
			print "Working directory created\n%s\n" %(self.sfm_path)
		self.init_matching_engine()
		self.init_feature_extractor()


	def parse_command_line(self):
		parser = argparse.ArgumentParser(description="Give directory of photographs used for SfM reconstruction using Bundler.")
		parser.add_argument('-d', '--data_in', type=str,
			help='A directory that contains a folder called "src_imgs" (Required).',
			required=True)
		parser.add_argument('-t', '--num_threads', type=int, 
			help='Set number of threads to use for image processing and feature detection/extraction.  Default = 8', 
			default=8)
		parser.add_argument('-v', '--verbose', type=bool, 
			help='Set to True for verbose dialogue', default=False)

		parser.add_argument('-s', '--max_size', type=int,
			help="Give maximum dimensions of photos (as integer).  Photos > maximum size will be resized accordingly. Default = 1280.",
			default=1280)
		parser.add_argument('-f', '--feature_engine', type=str,
			help="Specify feature detection engine (as string). Default = 'siftvlfeat'.",
			choices=['siftvlfeat', 'sift', 'siftlowe', 'surfcv'],
			default='siftvlfeat')
		
		parser.add_argument('-add', '--add_photos', type=bool, 
			help='Set to True to add images to existing bundler reconstruction. User working directory must be specified (-wd flag).', 
			default=False)
		parser.add_argument('-rr', '--re_run', type=bool, 
			help='Set to True to run bundler only.  User working directory must be specified (-wd flag).', 
			default=False)	

 		try:
			args = parser.parse_args(namespace=self)						
		except:
			parser.print_help()
			sys.exit()
		
	def exceptions(self):
		if not os.path.isdir(self.data_in):
			raise Exception, "'%s' is not a directory.  Please specify a directory with photos with -d or --data_in flag." %(self.data_in)
		if not isinstance(self.num_threads, int):
			raise Exception, "'%s' is not an integer.  Please specify the number of threads as an integer." %(self.num_threads)
		if not isinstance(self.max_size, int):
			raise Exception, "'%s' is not an integer.  Please specify the number of threads as an integer." %(self.max_size)

	def load_data(self):
		os.chdir(self.data_in)
		if self.add_photos:
			try:
				self.otherframes = np.load("otherframes.npy")
			except:
				print "No otherframes.npy file found... using all the frames in src_imgs/."
				self.otherframes = None

			if self.otherframes is not None:
				otherframe_strings =  ["%08d.jpg" %i for i in self.otherframes]
				self.photos = otherframe_strings
			else: 
				self.photos =[f for f in os.listdir("src_imgs") if os.path.isfile(os.path.join("src_imgs", f)) and os.path.splitext(f)[1].lower()==".jpg"]

		else:
			try:
				self.keyframes = np.load("keyframes.npy")
			except:
				print "No keyframes.npy file found... using all the frames in src_imgs/."
				self.keyframes = None

			if self.keyframes is not None:
				keyframe_strings =  ["%08d.jpg" %i for i in self.keyframes]
				self.photos = keyframe_strings
			else: 
				self.photos =[f for f in os.listdir("src_imgs") if os.path.isfile(os.path.join("src_imgs", f)) and os.path.splitext(f)[1].lower()==".jpg"]
		os.chdir(self.currentDir)


	def chunk_list(self, l, n):
		threads = [[] for i in range(n)]
		i = 0
		for i in range(n):
			threads[i] = l[i::n]
			i += 1
		return threads

	def prepare_photos(self):
		thread_list = []
		
		# split the list of photos into chunks based on how many threads we want to run
		self.photos_chunk_list = self.chunk_list(self.photos, self.num_threads)
		# make threads for each chunk and process photos
		for th in xrange(0, self.num_threads):
			thread_list.append( Thread(target=self.process_photos, args=([self.photos_chunk_list[th]]) ))	

		os.chdir(self.sfm_path)

		for th in thread_list:
			th.start()

		for th in thread_list:
			th.join()

		# write the necessary output files
		# photo_list and feature_list

		if self.add_photos:		
			bundler_list_file = open(os.path.join(self.sfm_path,bundler_list_add_fn), "w")
			feature_list_file = open(os.path.join(self.sfm_path,self.matching_engine.features_list_add_fn), "w")
		else:
			bundler_list_file = open(os.path.join(self.sfm_path,bundler_list_fn), "w")
			feature_list_file = open(os.path.join(self.sfm_path,self.matching_engine.featuresListFileName), "w")


		for i in sorted(self.photo_list):
			#("%s.jpg 0 %s\n" % (photo,SCALE*focalPixels)
			bundler_list_file.write("%s %s %s\n" %(i[0], i[1], i[2]))

		for i in sorted(self.feature_list):
			feature_list_file.write("%s.%s\n" %(i[0],i[1]))

		bundler_list_file.close()
		feature_list_file.close()

		os.chdir(self.currentDir)




	def process_photos(self, photos):
		for p in photos:
			if self.verbose:
				print "\nProcessing Photo '%s':" %p

			photo_info = dict(dirname=self.src_imgs_path, basename=p)
			src_jpg_in = os.path.join(self.src_imgs_path, p)

			# make file paths for output into working directory
			jpg_out = os.path.join(self.sfm_path, p)
			pgm_out = "%s.pgm" % os.path.join(self.sfm_path, p)

			# now we open the image using PIL and get exif data
			p_obj = Image.open(src_jpg_in)
			exif = self.get_exif(p_obj)
			self.calc_focal_length_pixels(p_obj, photo_info, exif)


			# resize photo if necessary
			max_dim = max(p_obj.size)
			if max_dim > self.max_size:
				scale = float(self.max_size)/float(max_dim)
				new_width = int(scale * p_obj.size[0])
				new_height = int(scale * p_obj.size[1])
				p_obj = p_obj.resize((new_width, new_height))
				if self.verbose:
					print "\tCopy of the photo has been scaled down to %sx%s" %(new_width,new_height)
			
			photo_info['width'] = p_obj.size[0]
			photo_info['height'] = p_obj.size[1]
			
			p_obj.save(jpg_out)
			p_obj.convert("L").save(pgm_out)

			self.photo_dict[p] = photo_info

			# extract feature keypoints
			self.extract_features(p)
			os.remove(pgm_out)



	def get_exif(self, p_obj):
		# helper function to extract exif data from .jpgs
		exif = {}
		info = p_obj._getexif()
		if info:
			for attr, value in info.items():
				decoded_attr = TAGS.get(attr, attr)
				if decoded_attr in EXIF_ATTRS:
					exif[decoded_attr] = value
		if 'FocalLength' in exif: 
			exif['FocalLength'] = float(exif['FocalLength'][0])/float(exif['FocalLength'][1])
			if self.verbose: print "exif['FocalLength']: \t", exif['FocalLength']
		
		return exif

	def calc_focal_length_pixels(self, p_obj, photo_info, exif):
		conn = sqlite3.connect(CAMERA_DB)
		dbCursor = conn.cursor()
		if 'Make' in exif and 'Model' in exif:
			# check if have camera entry in the database by make/model taken from exif
			dbCursor.execute("select ccd_width from cameras where make=? and model=?", (exif['Make'].strip(),exif['Model'].strip()))
			ccdWidth = dbCursor.fetchone()
			if ccdWidth:
				if 'FocalLength' in exif and 'ExifImageWidth' in exif and 'ExifImageHeight' in exif:
					focalLength = float(exif['FocalLength'])
					width = float(exif['ExifImageWidth'])
					height = float(exif['ExifImageHeight'])
					if self.verbose: print "\nphoto: %s, width %s, height: %s, focal_length: %s" %(p_obj, width, height, focalLength)

					if focalLength>0 and width>0 and height>0:
						if width<height: width = height
						focalPixels = width * (focalLength / ccdWidth[0])
						#
						self.photo_list.append((photo_info['basename'],0,SCALE*focalPixels))

						if self.verbose:
							print "\nAdded image %s to the photo_list with focal length: %s" \
									%(photo_info['basename'], SCALE*focalPixels)
						#self.bundlerListFile.write("%s.jpg 0 %s\n" % (p_obj,SCALE*focalPixels))
			else: 
				if self.verbose: 
					print "\tEntry for the camera '%s', '%s' does not exist in the camera database" % (exif['Make'], exif['Model'])
		if 'FocalLength' not in exif:
			if self.verbose: 
				print "\tCan't estimate focal length in pixels for the photo '%s'" % os.path.join(p_obj_info['dirname'],p_obj_info['basename'])
			self.photo_list.append((photo_info['basename'],0,' '))

		dbCursor.close()

	def init_matching_engine(self):
		try:
			matching_engine = getattr(matching, self.matching_engine)
			matching_engine_class = getattr(matching_engine, matching_engine.className)
			self.matching_engine = matching_engine_class(os.path.join(distrPath, "software"))
		except:
			raise Exception, "Unable initialize matching engine %s" % self.matching_engine


	def init_feature_extractor(self):
		try:
			# get the class from the features init file with specified string
			feature_extractor = getattr(features, self.feature_engine) 
			# get the name of the class as specified as variable the class header
			feature_extractor_class = getattr(feature_extractor, feature_extractor.className)
			self.feature_engine = feature_extractor_class(os.path.join(distrPath, "software"))
		except:
			raise Exception, "Unable initialize feature extractor %s" %self.feature_engine

	def extract_features(self, photo):
		self.feature_engine.extract(photo, self.photo_dict[photo])
		self.feature_list.append((photo[:-4], self.feature_engine.fileExtension))

	def match_features(self):
		# let self.matchingEngine do its job
		os.chdir(self.sfm_path)
		self.matching_engine.match()
		os.chdir(self.currentDir)

	def run_bundle_adjustment(self):
		# just run Bundler here
		print "\nPerforming bundle adjustment..."
		os.chdir(self.sfm_path)
		os.mkdir("bundle")
		
		# create options.txt
		optionsFile = open("options.txt", "w")
		optionsFile.writelines(defaults.bundlerOptions)
		optionsFile.close()

		bundlerOutputFile = open("bundle/out", "w")
		subprocess.call([bundlerExecutable, "list.txt", "--options_file", "options.txt"], **dict(stdout=bundlerOutputFile))
		bundlerOutputFile.close()

		os.mkdir("undistorted_imgs")
		subprocess.call([RadialUndistordExecutable, "list.txt", "bundle/bundle.out", "undistorted_imgs"])
		
		os.chdir(self.currentDir)
		print "Finished!"


	def add_to_bundle(self):
		# we want to add to an existing bundle.out file
		# therefore we will need a set of 
		print "\nPerforming bundle adjustment..."
		os.chdir(self.sfm_path)
		#os.mkdir("bundle_add")
		
		# create options.txt
		optionsFile = open("options_add.txt", "w")
		optionsFile.writelines(defaults.bundler_add_options)
		optionsFile.close()

		bundlerOutputFile = open("bundle/out", "w")
		subprocess.call([bundlerExecutable, "list.txt", "--options_file", "options_add.txt"], **dict(stdout=bundlerOutputFile))
		bundlerOutputFile.close()
		os.chdir(self.currentDir)
		print "Finished!"

	# def re_run_bundle_adjustment(self):
	# 	# rerun bundler to optimize 
	# 	print "\nPerforming bundle adjustment..."
	# 	os.chdir(self.sfm_path)
	# 	os.mkdir("bundle_rerun")
		
	# 	# create options.txt
	# 	optionsFile = open("options_rerun.txt", "w")
	# 	optionsFile.writelines(defaults.bundler_rerun_options)
	# 	optionsFile.close()

	# 	bundlerOutputFile = open("bundle_rerun/out", "w")
	# 	subprocess.call([bundlerExecutable, "list.txt", "--options_file", "options_rerun.txt"], **dict(stdout=bundlerOutputFile))
	# 	bundlerOutputFile.close()
	# 	os.chdir(self.currentDir)
	# 	print "Finished!"



	def open_result(self):
		if sys.platform == "win32": 
			subprocess.call(["explorer", self.sfm_path])
		else: 
			print "See the results in the '%s' directory.  Opening result..." %self.sfm_path
			subprocess.call(["open", "-R", self.sfm_path])





