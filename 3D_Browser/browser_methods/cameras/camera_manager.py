#!/usr/bin/env python
# encoding: utf-8
import numpy as np

from pinhole import Camera

class CameraManager(object):
	"""Manager for multiple cameras"""
	def __init__(self):
		self.cameras = []

	def add_cam(self, camera_object, image_object):
		self.cameras.append(camera_object)

	def load_other_cams(self, C_matrices, img_list, frames):
		for C, img, k in zip(C_matrices, img_list, frames):
			self.cameras.append(Camera(C, img=img, frame_num=k))

	def load_key_cams(self, C_matrices, img_list, frames):
		for C, img, k in zip(C_matrices, img_list, frames):
			if np.sum(C) != 0:
				# if the sum is 0, we don't show it 
				# because bundler rejected the frame
				self.cameras.append(Camera(C, img=img, frame_num=k, is_keyframe=True))

	def get_num_cams(self):
		return len(self.cameras)

	def get_img_scale(self):
		return self.cameras[0]._get_img_scale()
	def set_img_scale(self, value):
		for c in self.cameras:
			c._set_img_scale(float(value))

	def get_cams(self):
		return self.cameras

	def pyramid_show(self):
		for c in self.cameras:
			c.pyramid_show = True
	def cone_show(self):
		for c in self.cameras:
			c.cone_show = True

	def pyramid_hide(self):
		for c in self.cameras:
			c.pyramid_show = False
	def cone_hide(self):
		for c in self.cameras:
			c.cone_show = False