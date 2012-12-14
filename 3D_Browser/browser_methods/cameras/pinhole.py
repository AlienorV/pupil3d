#!/usr/bin/env python
# encoding: utf-8

import numpy as np
from scipy import linalg
import glumpy

class Camera():
	""" Class for representing pinhole cameras"""
	def __init__(self, C, img=None, frame_num=None, is_keyframe=False, 
				c=None, f=None, w_s=None):	
		self.P = None
		self.C = C
		self.img = img
		self.frame_num = frame_num
		self.keyframe = True
		self.img_scale = 0.00001
		self.img_W = None
		self.img_H = None
		self.img_Z = None
		self.img_origin = None
		self.pyramid_show = True
		self.cone_show = False

		self.eye = None

		self.a = None

		self.K = None # calibration matrix
		self.R = self.C[1:4] # rotation
		self.R[1:] *= -1
		self.t = self.C[-1] # translation
		self.t[1:] *= -1
		self.c = c # camera center
		self.f = f # focal point 
		self.fx = self.C[0,0]
		self.fy = self.fx
		self.w_s = w_s
		self.center_ray = None
		self.pyramid = None
		self.up = [0.,1.,0.]


		self.inside_cone = [] 
		self.cone_len = 0
		# if self.P is not None:
			# self.factor()
			#self.make_center_ray()
		self.R_gl = self.rotation_matrix_gl(self.R)
		# self.make_pyramid()
		
	def project(self, X):
		""" Project points in X (4*n array) and normalize coordinates. """
		
		x = np.dot(self.P, X)
		for i in range(3):
			x[i] /= x[2]
		return x
		
		
	def rotation_matrix(self, a):
		""" 
			Creates a 3d rotation matrix for rotating points 
			around the axis of vector 'a'. 
		"""
		
		R = np.eye(4)
		R[:3,:3] = linalg.expm([[0,-a[2],a[1]], 
								[a[2],0,-a[0]],
								[-a[1],a[0],0]])
		return R
	
	def rotation_matrix_gl(self, R):
		"""
			Creates a rotation matrix for OpenGL from self matrix
		"""
		R_gl = np.eye(4)
		R[0:,] = -R[0:,]	 # - hacks for opengl
		R_gl[:3,:3] = R[:3,:3]
		R_gl = R_gl.flatten()
		return R_gl

	def make_P_matrix(self):
		""" make P matrix from C_Matrix (R,T and K)
		"""

	def factor(self):
		""" Factorize the camera into:
			K: Camera intrinsics 
			t: Camera position (or translation)
			R: Camera pose (or Rotation)
			P = K[R|t]
			see:
			http://www.janeriksolem.net/2011/03/rq-factorization-of-camera-matrices.html
		"""
		
		# factor for first 3*3 part
		K, R = linalg.rq(self.P[:,:3])
		#print "camera matrix: ", self.P
		
		# make diagonal of K positive
		# because focal length is positive
		T = np.diag(np.sign(np.diag(K)))
		
		self.K = np.dot(K, T)
		self.fx = K[0,0]
		self.fy = K[1,1]

		self.R = np.dot(T, R) # T is its own inverse
		self.t = np.dot(linalg.inv(self.K), self.P[:,3])
		

		return self.K, self.R, self.t
		
	def center(self):
		"""	If the camera projection matrix P is known then you can
		 	Compute and return the camera center
			i.e. where is the camera C is a point in 3d space where PC = 0
			with camera with P = K[R|t] this gives:
			K[R|t]C = KRC + Kt = 0
			C = -R^T*t
		"""
		
		if self.c is not None:
			return self.c
		else:
			# compute camera center c by factoring
			self.factor()
			self.c = -np.dot(self.R.T, self.t) 
			return self.c
			
	def pyramid_angle(self):
		"""	Compute the angle of the pyramid
			Input: 
				- Focal length f: length in pixels between 
				optic center and image plane
				- Image width, image height: to calculate angle 
		"""
		from math import atan2

		if self.fx and self.fy is None:
			self.factor()
		else: 
			ax = atan2((0.5*self.img.width/self.img.my_scale), self.fx)
		return ax


	def make_center_ray(self):
		"""Make center ray between optical center
			and focal plane center
			for debugging
		"""
		if self.c is not None: 
			x, y, z = self.c
		if 	self.f is not None:
			fx, fy, fz = self.f

		p = np.array([ [x, y, z], [fx, fy, fz] ])
		p *= self.w_s


		n = ( 	(0, 1, 0 ) )
		c = ( (1.0, 0.0, 0.0) ) # colors
		vert = np.array(
			[ 	(p[0],n[0],c[0]), (p[1],n[0],c[0])	], 
			dtype = [('position','f4',3), ('normal','f4',3), ('color','f4',3)] )

		# load to glumpy vertex buffer
		self.center_ray = glumpy.graphics.VertexBuffer(vert)


	def make_pyramid(self):
		"""Make pyramid with apex at optical center
			- base centered at focal center (also center of image)
			- width and height of base based on intrinsics of camera
		"""
		from math import tan, sin, cos, pi
		
		a = self.pyramid_angle()
		W = 0.5*(self.img_scale*self.img.width)
		H = 0.5*(self.img_scale*self.img.height)

		Z = W/tan(a)
		self.img_Z = Z
		up = [0.0, 1.0, 0.0]
		f = [0.0, 0.0, -Z]

		if self.eye is not None:
			# if there is an eye position for the image frame
			# denormalize x,y of point and move point onto image plane
			# multiply by rotation matrix and translation matrix
			# make vertex buffer object
			point_scale = 0.99
			eye_x= (-W*point_scale) * self.eye[0]
			eye_y= (-H*point_scale) * self.eye[1]
			eye_z = -(W*point_scale)/tan(a)

			p_eye = np.array([[0.0, 0.0, 0.0], [eye_x,eye_y,eye_z]])
			n_eye = (0, 1, 0 )
			c_eye = (1.0, 0.0, 0.0, 0.5)

			p_eye = np.asarray(np.asmatrix(p_eye)*np.asmatrix(self.R))
			t_eye = np.asarray(np.asmatrix(self.t)*np.asmatrix(self.R))
			p_eye += t_eye

			vert_eye = np.array([ (p_eye[1], n_eye, c_eye) ],
								dtype=[('position','f4',3), ('normal','f4',3), ('color','f4',4)] )
			self.eye_point = glumpy.graphics.VertexBuffer(vert_eye)

			# compose rotation matrix for eye cone visualization
			rot_x = tan(eye_y/eye_z)
			rot_x += pi # rotate because glutSolidCone draws base at 0.0 and height always positive on Z
			rot_y = tan(eye_x/eye_z)
			R_y = np.array([	[cos(rot_y), 0, sin(rot_y)],
								[0, 1, 0],
								[-sin(rot_y), 0, cos(rot_y)] ])
			
			R_x = np.array([	[1, 0, 0],
								[0, cos(rot_x), -sin(rot_x)],
								[0, sin(rot_x), cos(rot_x)] ])
			R_cone = np.dot(R_y, R_x)
			self.R_cone = R_cone

			self.R_cone_gl = self.rotation_matrix_gl(R_cone)

		else:
			self.eye_point = None


		p = np.array([	[0.0,0.0,0.0], 	# apex point 
						[-W, -H, -Z], 	# base bottom left
						[-W, H, -Z], 	# base top left
						[W, H, -Z], 	# base top right
						[W, -H, -Z]	])	# base bottom right

		p = np.asarray(np.asmatrix(p)*np.asmatrix(self.R))
		t = np.asarray(np.asmatrix(self.t)*np.asmatrix(self.R))
		p += t

		f = np.asarray(np.asmatrix(f)*np.asmatrix(self.R))
		f += t



		n = (0, 1, 0 ) 
		c = (1.0, 0.0, 0.0,1.0)  # colors
		vert = np.array([ (p[1],n,c), (p[2],n,c), (p[3],n,c), (p[4],n,c), # base
						  (p[0],n,c), (p[1],n,c), (p[2],n,c), (p[0],n,c), # tri 1	
						  (p[0],n,c), (p[2],n,c), (p[3],n,c), (p[0],n,c), # tri 2
						  (p[0],n,c), (p[3],n,c), (p[4],n,c), (p[0],n,c), # tri 3
						  (p[0],n,c), (p[4],n,c), (p[1],n,c), (p[0],n,c) ], # tri 4
						dtype = [('position','f4',3), ('normal','f4',3), ('color','f4',4)] )

		self.pyramid = glumpy.graphics.VertexBuffer(vert)
		self.img_origin = p[-1]

		self.img_W = W
		self.img_H = H
		self.a = a
		up = np.asarray(np.asmatrix(up)*np.asmatrix(self.R))
		up += t
		self.up = up.flatten()
		self.f = f.flatten()
		self.c = t.flatten()

		#print "self.t: %s\nself.f: %s\nself.up: %s" %(self.t, self.f, self.up)


	def cone_intersect(self,pts,colors):
		from math import tan,radians, sqrt

		pts = np.asarray(np.asmatrix(pts)*np.asmatrix(self.R).T)
		pts -= self.t
		pts = np.asarray(np.asmatrix(pts)*np.asmatrix(self.R_cone).T)
		# pts -= self.img_Z
		angle = radians(.75) # foveal with = 1.5degrees 
		r_2 = tan(angle)**2
		for pt, i in zip(pts,xrange(pts.shape[0])):
			x,y,z = pt[0],pt[1],pt[2]
			result = z**2 - x**2/r_2 - y**2/r_2
			if result > 0:
				d = sqrt(x**2 +y**2 +z**2 ) 
				self.inside_cone.append(((x,y,z),i,d))	
				# print "pt is inside",(x,y,z),i

		self.inside_cone= sorted(self.inside_cone, key=lambda point: point[2]) # sort by distance
		inside_pts = [list(p) for p,i,d in self.inside_cone]
		inside_colors = [colors[i]/255 for p,i,d in self.inside_cone]
		
		n = (0, 1, 0 ) 
		v = []
		for pt,c in zip(inside_pts,inside_colors):
			c =(c[0],c[1],c[2],1.0)
			v.append((pt, n, c))

		verts = np.asarray(v, dtype=[('position','f4',3), ('normal','f4',3), ('color','f4',4)] )
		self.inside_cone_vbo = glumpy.graphics.VertexBuffer(verts)
		
		if len(self.inside_cone) > 0: # if points are insode visual cone
			self.cone_len = self.inside_cone[len(self.inside_cone)/2][2] #median
		else:
			self.cone_len = .2 
		self.cone_r = self.cone_len*tan(angle)

	def _get_img_scale(self):
		return self.img_scale
	def _set_img_scale(self, value):
		self.img_scale = value
		self.make_pyramid()

