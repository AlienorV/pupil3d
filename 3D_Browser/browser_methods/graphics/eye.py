#!/usr/bin/env python
# encoding: utf-8

import OpenGL.GL as gl
import OpenGL.GLU as glu

import math
import numpy as np

# Some useful functions on vectors
# -----------------------------------------------------------------------------
def _v_add(v1, v2):
	return [v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2]]
def _v_sub(v1, v2):
	return [v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2]]
def _v_mul(v, s):
	return [v[0]*s, v[1]*s, v[2]*s]
def _v_dot(v1, v2):
	return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]
def _v_cross(v1, v2):
	return [(v1[1]*v2[2]) - (v1[2]*v2[1]),
			(v1[2]*v2[0]) - (v1[0]*v2[2]),
			(v1[0]*v2[1]) - (v1[1]*v2[0])]
def _v_length(v):
	return math.sqrt(_v_dot(v,v))
def _v_normalize(v):
	try:                      return _v_mul(v,1.0/_v_length(v))
	except ZeroDivisionError: return v

class Eye(object):
	"""Scene camera using opengl.GLU
		Functions like the subject's eye
		Aligns with SfM cameras in the scene using gluLookAt
	"""
	def __init__(self, center=[0.0, 0.0, -1.0], focus=[0.0, 0.0, 0.0], up=[0.,1.,0.], aperture=35.0):
		self.center = center
		self.focus = focus
		self.up = up
		self.aperture = aperture
		self.zoom = 1.0
		self.near = 0.1
		self.far = 100.0
		self.pt_avg = None

		self.near = 0.01
		self.far = 100.0
		self.show = False
		self.id = 0

		self.cams = None


	def push(self):
		viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
		aspect = viewport[2]/float(viewport[3])

		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glPushMatrix()
		gl.glLoadIdentity()
		glu.gluPerspective(self.aperture*self.zoom,aspect,self.near,self.far) 
		glu.gluLookAt(	self.center[0], self.center[1], self.center[2],
						self.focus[0], self.focus[1], self.focus[2], 
						self.up[0], self.up[1], self.up[2])

		gl.glMatrixMode (gl.GL_MODELVIEW)
		gl.glPushMatrix()
		gl.glLoadIdentity()


	def pop(self):
		gl.glMatrixMode(gl.GL_MODELVIEW)
		gl.glPopMatrix()
		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glPopMatrix()		


	def _get_aperture(self):
		return self.aperture
	def _set_aperture(self, value):
		self.aperture = value

	def _get_up_x(self):
		return self.up[0]
	def _set_up_x(self, value):
		self.up[0] = float(value)
	def _get_up_y(self):
		return self.up[1]
	def _set_up_y(self, value):
		self.up[1] = float(value)
	def _get_up_z(self):
		return self.up[2]
	def _set_up_z(self, value):
		self.up[2] = float(value)
	
	def _set_up(self, values):
		self.up = _v_normalize(values)

	def _show(self):
		self._set_current(self.id)
		self.show = True
	def _hide(self):
		self.show = False

	def _set_cams(self, cams):
		self.cams = cams
	def _get_cams(self):
		return len(self.cams)

	def _set_pt_avg(self, value):
		self.pt_avg = value

	def _get_current(self):
		return	self.id
	def _set_current(self, value):
		i = int(value)
		if self.cams is not None:
			if i in range(0, len(self.cams)):
				self.aperture = np.degrees(self.cams[i].a)*2
				
				self.center = np.array([self.cams[i].c[0]+self.pt_avg[0], 
									self.cams[i].c[1]+self.pt_avg[1], 
									self.cams[i].c[2]+self.pt_avg[2] ]	)
				self.focus = np.array([	self.cams[i].f[0]+self.pt_avg[0], 
									self.cams[i].f[1]+self.pt_avg[1], 
									self.cams[i].f[2]+self.pt_avg[2]])
				self.up = self.cams[i].up-self.cams[i].c

				self.id = i
		


		
