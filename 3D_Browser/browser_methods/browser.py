#!/usr/bin/env python
# encoding: utf-8

"""
Browser manages all classes within browser_methods folder
The browser class performs the following:
	1. Parse command line options & generate help text
	2. Generate attributes that point to locations of source files: 
		2.1. 	Sparse .stl file from Bundler (sparse_ply)
		2.2. 	Dense .stl file from PMVS2 (dense_ply)
		2.3. 	Projection Matrices for each camera used to generate
				(dense_ply) stored as .txt files produced by PMVS2
		2.4. 	Image files associated with the projection matrices 
	3. 
"""

import logging 
import sys, os, argparse, tempfile
from glob import glob 

from points.points import Points
from cameras.camera_manager import CameraManager
from graphics.visualize import Visualize

import numpy as np
import cv2

distrPath = os.path.dirname( os.path.abspath(sys.argv[0]) )
logging.basicConfig(level=logging.INFO, format="%(message)s")

class Browser(object):
	"""Browser: visualization for SfM (Bundle+PMVS)"""
	currentDir = ""
	workDir = ""

	def __init__(self):
		self.ply_path = "SfM/pmvs/models/pmvs_options.txt.ply"
		self.ply_fallback_path = "SfM/bundle/*.ply"
		self.bundle_out_path = "SfM/bundle/bundle.out"
		self.src_imgs_path = "SfM/undistorted_imgs/"
		self.video_path = "world.avi"
		self.keyframes_path = "keyframes.npy"
		self.otherframes_path = "otherframes.npy" 
		self.audio_path = "world.wav"
		self.pupil_positions_path = "pupil_positions.npy"
		self.using_sparse = False
		self.bundle_img_list_path = "SfM/list.txt"

		self.mask = '*.jpg'

		self.parseCommandLineFlags()

		self.currentDir = os.getcwd()
		#self.workDir = tempfile.mkdtemp(prefix="SfM_Browser_")
		#logging.info("Working directory created: "+self.workDir)
		self.exceptions()

	def parseCommandLineFlags(self):
		parser = argparse.ArgumentParser(description="Get files from SfM pipeline needed for the SfM Browser")
		parser.add_argument('-d', '--data_path', type=str, 
			help='A directory where .stl, .txt, .jpg/.png data from SfM pipeline is saved. (only required option)',
			required=True)
		

		parser.add_argument('-v', '--verbose', type=bool, default=False, 
			help='Set to True for verbose dialogue')
		
		try:
			args = parser.parse_args(namespace=self)						
		except:
			parser.print_help()
			sys.exit()

	def exceptions(self):
		if not os.path.isdir(self.data_path):
			raise Exception, "'%s' is not a directory.  Please specify a data directory." %(self.data_path)

	def load_data(self):
		os.chdir(self.data_path)
		try:
			self.ply = open(self.ply_path, 'r')
		except:
			print "No dense reconstruction found, using sparse reconstruction"
			try:
				self.ply = open(max(glob(self.ply_fallback_path)), 'r')
				self.using_sparse = True
			except:
				print "No .ply file found at: %s" %(self.ply_path)
				self.ply = None

		try:
			self.bundle_out = open(self.bundle_out_path, 'r')
		except:			
			print "No bundle.out file found at: %s" %(self.bundle_out_path)
			self.bundle_out = None

		try: 
			self.pupil_positions = np.load(self.pupil_positions_path)
		except:
			print "No pupil_positions.npy file found at: %s" %self.pupil_positions_path
			self.pupil_positions = None
		
		try:
			self.keyframes = np.load(self.keyframes_path)
		except:			
			print "No keyframes.npy file found at: %s" %(self.keyframes_path)
			self.keyframes = None
		
		try:
			self.otherframes = np.load(self.otherframes_path)
		except:			
			print "No otherframes.npy file found at: %s" %(self.otherframes_path)
			self.otherframes = None

		try:
			self.bundle_img_list = open(self.bundle_img_list_path, 'r')
			self.bundle_img_list = [i.split('.')[0] for i in self.bundle_img_list]

			self.bundle_keyframes = [int(i) for i in self.bundle_img_list] # keyframe numbers as int

			# undistorted keyframe image file names as string
			self.bundle_img_list = [os.path.join(self.src_imgs_path, i+'.rd.jpg') for i in self.bundle_img_list] 
		except:
			print "No image.txt file found"
			self.bundle_img_list = None


		if self.otherframes is not None:
			# we assume that the files exist
			otherframe_strings = ["%s%08d.rd.jpg" %(self.src_imgs_path, i) for i in self.otherframes]
			self.otherframe_imgs = otherframe_strings
		else:
			self.otherframe_imgs = None

			
		if self.bundle_img_list:

			self.bundle_img_list = self.load_images(self.bundle_img_list)

		if self.otherframe_imgs:
			self.otherframe_imgs = self.load_images(self.otherframe_imgs)




	def prepare_data(self):
		self.load_data()
		pt_manager = Points()
		camera_manager = CameraManager()

		# load points from ply file to point class
		if self.verbose: print "Loading points from .ply file..."
		if self.using_sparse:
			pt_manager.load_sparse_ply(self.ply)
			if self.verbose: print "Loaded %s float_points, %s color values from ply"\
					%(pt_manager.f_pts.shape[0], pt_manager.colors.shape[0])
		else:
			pt_manager.load_ply(self.ply)
			if self.verbose: print "Loaded %s float_points, %s normalized_points, %s color values from ply"\
					%(pt_manager.f_pts.shape[0], pt_manager.n_pts.shape[0], pt_manager.colors.shape[0])

		# load Camera intrinsics and extrinsics from bundle.out file as np.array
		if self.verbose: print "Creating camera objects from projection matrices and image files..."
		head = self.bundle_out.readline()
		cams, points = [int(x) for x in self.bundle_out.readline().split()]
		C_matrices = [[[float(x) for x in line.split()] for line in [self.bundle_out.readline() for x in range(5)]] for cam in range(cams)]
		C_matrices =  np.asarray(C_matrices)
		# camera_manager.load_key_cams(C_matrices, self.keyframe_imgs, self.keyframes)
		camera_manager.load_key_cams(C_matrices, self.bundle_img_list, self.bundle_keyframes)

		camera_manager.cameras = camera_manager.cameras[0:-1] # change step for debugging
		if self.verbose: print "Loaded %s cameras." %(camera_manager.get_num_cams())

		if self.pupil_positions is not None:
			for cam in camera_manager.cameras:
				cam.eye = self.pupil_positions[cam.frame_num,0:2]

		for cam in camera_manager.cameras:
			cam.make_pyramid()
		
		for cam in camera_manager.cameras:
			print cam
			cam.cone_intersect(pt_manager.f_pts,pt_manager.colors)


		return pt_manager, camera_manager


	def run(self):
		vis = Visualize()
		vis._set_Points_Cameras(*self.prepare_data())
		vis.main()
		











	#------------------- Helper Functions -------------------#
	def load_P_matrices(self, file_names):
		Ps = []
		for fn in file_names:
			src = open(fn, 'r')
			src = src.readlines() # make it a list
			P = np.asarray([i.split() for i in src[1:]], dtype='f4') #don't use first line
			Ps.append(P)

		return Ps

	def load_images(self, file_names):
		import glumpy 

		imgs = []
		
		for fn in file_names:
			src = cv2.imread(fn, 1)
			if src is not None:
				# if undistorted image exists and not rejected by bundler
				cv2.flip(src, 1, src)
				src = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
				scale = 1
				if max(src.shape) > 1500:
					scale = 1280/float(src.shape[1])
					# src = cv2.resize(src,np.asarray([src.shape[1]/10, src.shape[0]/10,src.shape[2]]),4)	
					src = cv2.resize(src,(0,0), fx=scale, fy=scale,interpolation=4)	
				# need to init glumpy before glumpy images can be created
				img = glumpy.image.Image(src, format='RBGA') 
				img.my_scale = scale
				imgs.append(img)
			else: 
				imgs.append(None)
			
		return imgs

